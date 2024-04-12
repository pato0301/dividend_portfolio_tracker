from django.contrib.auth.decorators import login_required
from django import forms
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages, auth
from django.db.models import Avg, Min
from django.utils import timezone
from .models import Portfolio, Transaction, DividendPayment
from asgiref.sync import sync_to_async
from django.db.models import Q
from .cron_jobs.process_dividend_payments import process_dividend_payments

from .forms import BuyStockForm, CSVUploadForm, SellStockForm

import yfinance as yf
import csv
from datetime import datetime
import time

# class BuyStockForm(forms.Form):
#     ticker = forms.CharField(label="Stock ticker")
#     number_stocks = forms.FloatField(label="Number of stock", min_value=0, step_size=0.00001)
#     price_stocks = forms.FloatField(label="Price", min_value=0, step_size=0.01)
#     date = forms.DateField(
#         label="Date",
#         widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
#         input_formats=["%Y-%m-%d"]
#     )


# class SellStockForm(forms.Form):

#     def __init__(self, user, *args, **kwargs):
#         super(SellStockForm, self).__init__(*args, **kwargs)
#         # Filter tickers based on user's portfolio
#         portfolio_entries = Portfolio.objects.filter(user_id=user)
        
#         if portfolio_entries.exists():
#             ticker_choices = [(entry.ticker, entry.ticker) for entry in portfolio_entries]
#             self.fields['ticker'] = forms.ChoiceField(
#                 label="Stock ticker",
#                 choices=ticker_choices,
#                 # initial='',
#                 # disabled=True,
#                 # required=False
#             )
#         else:
#             self.fields['ticker'] = forms.ChoiceField(
#                 label="Stock ticker",
#                 choices=[('', '---')],
#                 initial='',
#                 disabled=True,
#                 required=False
#             )

#         self.fields['number_stocks'] = forms.FloatField(label="Number of stock", min_value=0)
#         self.fields['price_stocks'] = forms.FloatField(label="Price", min_value=0)
#         self.fields['date'] = forms.DateField(
#             label="Date",
#             widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
#             input_formats=["%Y-%m-%d"]
#         )

# class CSVUploadForm(forms.Form):
#     csv_file = forms.FileField(
#         label='Select a CSV file',
#         help_text='Please upload a CSV file',
#         widget=forms.FileInput(attrs={'accept': '.csv'})
#     )

#     def clean_csv_file(self):
#         csv_file = self.cleaned_data['csv_file']
#         if not csv_file.name.endswith('.csv'):
#             raise forms.ValidationError('Please upload a valid CSV file.')
#         return csv_file

# Create your views here.
@login_required
def index(request):
    return render(request, "portfolio/index.html", {
        "stocks" : Portfolio.objects.filter(user_id=request.user)
    })


def pay_div(request):
    if request.method != 'GET':
        # Return a 405 Method Not Allowed response for GET requests
        return HttpResponseNotAllowed(['GET'])

    # Run the process_dividend_payments function
    process_dividend_payments(Portfolio, DividendPayment)

    # Return a JSON response
    return JsonResponse({'message': 'Dividend payments processing started successfully'})

        

@login_required
def load_buy_stock(request):
    return render(request, "portfolio/buy_stock.html", {
        "form": BuyStockForm()
    })

async def save_buy_stock(request):
    # start_time = time.time()
    # if not await sync_to_async(request.user.is_authenticated):
    is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()
    if not is_authenticated:
        # print("Here")
        return HttpResponseRedirect(reverse("users:login"))
    else:
        if request.method == "POST":
            user = await sync_to_async(lambda: request.user)()
            form = BuyStockForm(request.POST)
            if form.is_valid():
                ticker = form.cleaned_data["ticker"]
                number_stocks = form.cleaned_data["number_stocks"]
                price_stocks = form.cleaned_data["price_stocks"]
                buy_date = form.cleaned_data["date"]
                today = timezone.now().date()
                # print(ticker, number_stocks, price_stocks, buy_date)

                if buy_date > today:
                    raise ValueError("Buy date cannot be in the future")

                if price_stocks <= 0:
                    raise ValueError("Buy price cannot be lower than 0")
                
                if number_stocks <= 0:
                    raise ValueError("Number of stock bought cannot be less than 0")

                try:
                    stock_data = yf.Ticker(ticker)
                    # Extract relevant information such as price, name, etc.
                    # industry = stock_data.info['sector']
                    # stock_name = stock_data.info['shortName']
                    # exDividendDate = stock_data.info['exDividendDate']
                    industry =  stock_data.info.get('sector', None)
                    stock_name = stock_data.info.get('shortName', None)
                    exDividendDate = stock_data.info.get('exDividendDate', None) 
                    if exDividendDate:
                        next_exdiv_payment = datetime.fromtimestamp(exDividendDate).date()
                    else:
                        next_exdiv_payment = None
                    # next_exdiv_payment = datetime.fromtimestamp(exDividendDate)

                    # print(industry, next_exdiv_payment)
                    new_stock = await Transaction.objects.acreate(
                        operation="buy",
                        ticker=ticker,
                        operation_date=buy_date,
                        n_stock=number_stocks,
                        price=price_stocks,
                        user_id=user
                    )

                    # Get the Portfolio entry for the user and ticker, if it exists
                    portfolio_entry = await Portfolio.objects.filter(user_id=user, ticker=ticker).afirst()
                    # print("got portfolio_entry")
                    # print(portfolio_entry)
                    # mid_time = time.time()
                    # execution_mid_time = mid_time - start_time
                    # print(f"Mid execution time: {execution_mid_time} seconds")
                    # print(True if portfolio_entry else False)
                    if portfolio_entry:
                        # Update avg_price and n_stock if the entry exists
                        transactions = Transaction.objects.filter(user_id=user, ticker=ticker)
                        # print("got transactions")
                        average_price = await sync_to_async(lambda: transactions.aggregate(avg_price=Avg('price'))['avg_price'])()
                        # print("got average_price")
                        
                        # Update the Portfolio entry
                        portfolio_entry.avg_price = round(average_price,2)
                        portfolio_entry.n_stock += number_stocks

                        # Check if buy_date is before next_exdiv_payment
                        if portfolio_entry.next_exdiv_payment and buy_date < portfolio_entry.next_exdiv_payment:
                            portfolio_entry.n_stock_next_exdiv_payment += number_stocks

                        await sync_to_async(portfolio_entry.save)()
                        # print("portfolio_entry saved")
                    
                    else:
                        # Create a new Portfolio entry if it doesn't exist
                        # print(industry, next_exdiv_payment)
                        new_stock = await Portfolio.objects.acreate(
                            ticker=ticker,
                            name=stock_name,
                            n_stock=number_stocks,
                            avg_price=price_stocks,
                            industry=industry,
                            n_stock_next_exdiv_payment=number_stocks if next_exdiv_payment and buy_date < next_exdiv_payment.date() else 0,
                            next_exdiv_payment=next_exdiv_payment if next_exdiv_payment and next_exdiv_payment.date() > buy_date else None,
                            user_id=user
                        )
                        # second_mid_time = time.time()
                        # execution_second_mid_time = mid_time - start_time
                        # print(f"Mid Second execution time: {execution_second_mid_time} seconds")
                    
                    # Redirect to the portfolio index page
                    return HttpResponseRedirect(reverse("portfolio:index"))
                except Exception as e:
                    # Handle any errors, such as invalid ticker symbols
                    form.add_error("ticker", str(e))
                    return render(request, "portfolio/buy_stock.html", {
                        "form": form
                    })
            else:
                return render(request, "portfolio/buy_stock.html", {
                    "form": form
                }) 
        
        else:
            return render(request, "portfolio/buy_stock.html", {
                "form": BuyStockForm()
            })                   


@login_required
def load_sell_stock(request):
    return render(request, "portfolio/sell_stock.html", {
        "form": SellStockForm(user=request.user)
    })

async def save_sell_stock(request):
    is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()
    if not is_authenticated:
        # print("Here")
        return HttpResponseRedirect(reverse("users:login"))
    else:
        user = await sync_to_async(lambda: request.user)()
        if request.method == "POST":
            form = await sync_to_async(lambda: SellStockForm(data=request.POST, user=user))()
            if form.is_valid():
                ticker = form.cleaned_data["ticker"]
                number_stocks = form.cleaned_data["number_stocks"]
                price_stocks = form.cleaned_data["price_stocks"]
                sell_date = form.cleaned_data["date"]
                today = timezone.now().date()
                try:
                    # Get the Portfolio entry for the user and ticker, if it exists
                    portfolio_entry = await Portfolio.objects.filter(user_id=user, ticker=ticker).afirst()
                    if not portfolio_entry:
                        raise ValueError("Stock not in portfolio")

                    if number_stocks > portfolio_entry.n_stock:
                        raise ValueError("Selling more stocks than in portfolio")
                    
                    if sell_date > today:
                        raise ValueError("Sell date cannot be in the future")

                    sell_stock = await Transaction.objects.acreate(
                        operation="sell",
                        ticker=ticker,
                        operation_date=sell_date,
                        n_stock=number_stocks,
                        price=price_stocks,
                        user_id=user
                    )

                    # Update the Portfolio entry
                    if portfolio_entry.n_stock == number_stocks:
                        await portfolio_entry.adelete()
                        # print("portfolio_entry deleted")
                    else:
                        # print("enter else")
                        portfolio_entry.n_stock -= number_stocks
                        # print("reduce n_stock")

                        # Check if sell_date is before next_exdiv_payment
                        if portfolio_entry.next_exdiv_payment and sell_date < portfolio_entry.next_exdiv_payment:
                            # print("reduce n_stock_next_exdiv_payment")
                            portfolio_entry.n_stock_next_exdiv_payment -= number_stocks

                        await sync_to_async(portfolio_entry.save)()
                        # print("portfolio_entry saved")

                    # Redirect to the portfolio index page
                    # mid_time = time.time()
                    # execution_mid_time = mid_time - start_time
                    # print(f"Mid execution time: {execution_mid_time} seconds")
                    return HttpResponseRedirect(reverse("portfolio:index"))
                except Exception as e:
                    # Handle any errors, such as invalid ticker symbols
                    # form.add_error("ticker", str(e))
                    messages.error(request, "Error: Stock not in portfolio.")
                    return render(request, "portfolio/sell_stock.html", {
                        "message": str(e),
                        "form": form
                    })
            else:
                return render(request, "portfolio/sell_stock.html", {
                    "message": "Something went wrong",
                    "form": form
                }) 
        else:
            return render(request, "portfolio/sell_stock.html", {
                "form": SellStockForm(user=user)
            })


@login_required
def load_dividen_log(request):
    # Today
    today = datetime.now()
    # Retrieve all dividend payments for the current user
    user_dividend_payments = DividendPayment.objects.filter(user_id=request.user)

    unique_stock_paid = user_dividend_payments.values_list('ticker', flat=True).distinct()

    # print("unique_stock_paid: ", unique_stock_paid)

    # Get the earliest payment date
    earliest_payment_date = user_dividend_payments.aggregate(earliest_date=Min('payment_date'))['earliest_date']

    # range_value = min((datetime.now().year - earliest_payment_date.year)+1, 5)
    range_value = 5
    
    # Generate a list of dates based on the range value
    date_list = []
    if range_value == 5:
        # Generate a date for every month from today's year - 5 years
        for i in range(1,6):
            for month in range(1, 13):
                if month > today.month and today.year == (today.year - 5 + i):
                    break
                date_list.append(datetime(datetime.now().year - 5 + i, month, 1).date())
    else:
        # Generate a list for each month from earliest_payment_date until the current month-year
        current_date = datetime.now()
        current_year = current_date.year
        current_month = current_date.month
        for year in range(earliest_payment_date.year, current_year + 1):
            start_month = earliest_payment_date.month if year == earliest_payment_date.year else 1
            end_month = current_month + 1 if year == current_year else 13
            for month in range(start_month, end_month):
                date_list.append(datetime(year, month, 1).date())

    # Create a list of dictionaries with date and ticker values
    # result = []
    # for date in date_list:
    #     ticker_dividends = [date]
    #     for dividend in user_dividend_payments:
    #         if dividend.payment_date.year == date.year and dividend.payment_date.month == date.month:
    #             ticker_dividends.append(dividend.amount)
    #         else:
    #             ticker_dividends.append(0)
    #     result.append(ticker_dividends)

    result = []
    lowest_date_with_value = None
    for date in date_list:
        # ticker_dividends = [date]
        ticker_dividends = {}
        ticker_dividends[date] = {}
        # print("ticker_dividends: ", ticker_dividends)
        for dividend in user_dividend_payments:
            if dividend.payment_date.year == date.year and dividend.payment_date.month == date.month:
                # print("dividend.ticker: ", dividend.ticker)
                # print("dividend.amount: ", dividend.amount)
                ticker_dividends[date][dividend.ticker] = dividend.amount
                # ticker_dividends.append(dividend.amount)
                if dividend.amount > 0 and (lowest_date_with_value is None or date < lowest_date_with_value):
                    lowest_date_with_value = date
            else:
                if dividend.ticker not in ticker_dividends[date].keys():
                    ticker_dividends[date][dividend.ticker] = 0
                # ticker_dividends.append(0)
        result.append(ticker_dividends)
        # print(f"result {date}: ", result)


    # Create a dictionary to organize dividend payments by ticker
    # ticker_dividends_dict = {dividend.ticker: [0] * len(date_list) for dividend in user_dividend_payments}

    # # Populate the dictionary with dividend amounts
    # for ticker, dividends in ticker_dividends_dict.items():
    #     for i, date in enumerate(date_list):
    #         dividend = user_dividend_payments.filter(ticker=ticker, payment_date__year=date.year, payment_date__month=date.month).first()
    #         if dividend:
    #             ticker_dividends_dict[ticker][i] = dividend.amount
    
    # # Convert the dictionary to the desired result format
    # result = [[date] + ticker_dividends_dict[ticker] for date in date_list for ticker in ticker_dividends_dict]

    # print("result: ", result)

    return render(request, "portfolio/dividend.html", {
        "stocks" : unique_stock_paid,
        "date_ticket_list" : result,
        "start_display_date" : lowest_date_with_value
    })

async def upload_csv(request):
    is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()
    if not is_authenticated:
        return HttpResponseRedirect(reverse("users:login"))

    if request.method == 'GET':
        return render(request, 'portfolio/upload_csv.html', {
            'form': CSVUploadForm()
        })

    elif request.method == 'POST':
        user = await sync_to_async(lambda: request.user)()
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            
            # Check if the uploaded file is a CSV
            if not csv_file.name.endswith('.csv'):
                return HttpResponse('Please upload a valid CSV file.')

            # Validate CSV content
            try:
                reader = csv.DictReader(csv_file.read().decode('utf-8').splitlines())
            except Exception as e:
                return HttpResponse(f'Error reading CSV: {e}')

            required_columns = ['ticker', 'number_stocks', 'price', 'date', 'type_of_action']
            for col in required_columns:
                if col not in reader.fieldnames:
                    return HttpResponse(f'Missing column: {col}')

            for row in reader:
                ticker = row['ticker']
                
                # Ensure price_stocks and number_stocks are not None or empty
                price_stocks = row.get('price')
                number_stocks = row.get('number_stocks')
                
                if price_stocks is None or not price_stocks.strip():
                    return HttpResponse("Price cannot be null or empty.")
                
                if number_stocks is None or not number_stocks.strip():
                    return HttpResponse("Number of stocks cannot be null or empty.")
                
                price_stocks = float(price_stocks)
                number_stocks = float(number_stocks)
                
                action_date = datetime.strptime(row['date'], '%d/%m/%Y').date()
                action_type = row['type_of_action']

                today = timezone.now().date()

                if action_type == 'BUY':
                    if action_date > today:
                        return HttpResponse("Buy date cannot be in the future")
                    if price_stocks <= 0:
                        return HttpResponse("Buy price cannot be lower than or equal to 0")
                    if number_stocks <= 0:
                        return HttpResponse("Number of stock bought cannot be less than or equal to 0")

                    try:
                        stock_data = yf.Ticker(ticker)
                        industry =  stock_data.info.get('sector', None) #stock_data.info['sector']
                        stock_name = stock_data.info.get('shortName', None) #stock_data.info['shortName']
                        exDividendDate = stock_data.info.get('exDividendDate', None) #stock_data.info['exDividendDate']
                        print(f"stock: {stock_name} exDividendDate: {exDividendDate}")
                        if exDividendDate:
                            next_exdiv_payment = datetime.fromtimestamp(exDividendDate).date()
                        else:
                            next_exdiv_payment = None
                        # next_exdiv_payment = datetime.fromtimestamp(exDividendDate).date()

                        new_stock = await Transaction.objects.acreate(
                            operation="buy",
                            ticker=ticker,
                            operation_date=action_date,
                            n_stock=number_stocks,
                            price=price_stocks,
                            user_id=user
                        )

                        portfolio_entry = await Portfolio.objects.filter(user_id=user, ticker=ticker).afirst()

                        if portfolio_entry:
                            transactions = Transaction.objects.filter(user_id=user, ticker=ticker)
                            average_price = await sync_to_async(lambda: transactions.aggregate(avg_price=Avg('price'))['avg_price'])()
                            
                            portfolio_entry.avg_price = round(average_price, 2)
                            portfolio_entry.n_stock += number_stocks

                            if portfolio_entry.next_exdiv_payment and action_date < portfolio_entry.next_exdiv_payment:
                                portfolio_entry.n_stock_next_exdiv_payment += number_stocks

                            await sync_to_async(portfolio_entry.save)()
                            
                        else:
                            new_stock = await Portfolio.objects.acreate(
                                ticker=ticker,
                                name=stock_name,
                                n_stock=number_stocks,
                                avg_price=price_stocks,
                                industry=industry,
                                n_stock_next_exdiv_payment=number_stocks if next_exdiv_payment and action_date < next_exdiv_payment else 0,
                                next_exdiv_payment=next_exdiv_payment if next_exdiv_payment and next_exdiv_payment > action_date else None,
                                user_id=user
                            )
                    except Exception as e:
                        return HttpResponse(f'Error processing buy action for {ticker}: {e}')

                elif action_type == 'SELL':
                    if action_date > today:
                        return HttpResponse("Sell date cannot be in the future")

                    portfolio_entry = await Portfolio.objects.filter(user_id=user, ticker=ticker).afirst()

                    if not portfolio_entry:
                        return HttpResponse("Stock not in portfolio")

                    if number_stocks > portfolio_entry.n_stock:
                        return HttpResponse("Selling more stocks than in portfolio")

                    try:
                        sell_stock = await Transaction.objects.acreate(
                            operation="sell",
                            ticker=ticker,
                            operation_date=action_date,
                            n_stock=number_stocks,
                            price=price_stocks,
                            user_id=user
                        )

                        if portfolio_entry.n_stock == number_stocks:
                            await portfolio_entry.adelete()
                        else:
                            portfolio_entry.n_stock -= number_stocks

                            if portfolio_entry.next_exdiv_payment and action_date < portfolio_entry.next_exdiv_payment:
                                portfolio_entry.n_stock_next_exdiv_payment -= number_stocks

                            await sync_to_async(portfolio_entry.save)()
                            
                    except Exception as e:
                        return HttpResponse(f'Error processing sell action for {ticker}: {e}')

            # return HttpResponse('CSV file processed successfully.')
            return redirect('portfolio:index') 

        else:
            return render(request, 'upload_csv.html', {'form': form})







# @login_required
# def pay_div(request):
#     # Get today's date
#     today = datetime.today()

#     # Filter Portfolio records with next_exdiv_payment = today
#     portfolios =  Portfolio.objects.filter(next_exdiv_payment=today)

#     # Get unique list of tickers
#     unique_tickers = portfolios.values_list('ticker', flat=True).distinct()

#     for ticker in unique_tickers:
#         stock_data = yf.Ticker(ticker)
#         last_dividend_value = stock_data.info["lastDividendValue"]
#         exDividendDate = stock_data.info['exDividendDate']
#         next_exdiv_payment = datetime.fromtimestamp(exDividendDate)
#         next_exdiv_payment_date = datetime.fromtimestamp(exDividendDate).date()

#         # Filter Portfolio records for the ticker
#         portfolios_for_ticker =  portfolios.filter(ticker=ticker)

#         # Iterate over portfolios for the ticker and save DividendPayment records
#         for portfolio in portfolios_for_ticker:
#             # Create DividendPayment record
#             dividend_payment = DividendPayment.objects.create(
#                 ticker=ticker,
#                 payment_date=today,
#                 amount=last_dividend_value,
#                 n_stock=portfolio.n_stock_next_exdiv_payment,
#                 user_id=portfolio.user_id
#             )

#             # Check if n_stock = 0, then delete the record
#             if portfolio.n_stock == 0:
#                 portfolio.delete()
#             else:
#                 # Update n_stock_next_exdiv_payment = n_stock
#                 portfolio.n_stock_next_exdiv_payment = portfolio.n_stock

#                 if portfolio.next_exdiv_payment >= next_exdiv_payment_date:
#                     portfolio.next_exdiv_payment = None
#                 else:
#                     portfolio.next_exdiv_payment = next_exdiv_payment

#                 portfolio.save()
    
#     return HttpResponse("ok")

# Async version of the GET, this goes lower than the sync
# so Im commenting it out.
# async def load_sell_stock(request):
#     start_time = time.time()
#     is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()
#     if not is_authenticated:
#         return HttpResponseRedirect(reverse("users:login"))
#     else:
#         user = await sync_to_async(lambda: request.user)()
#         ticker_choices = []
#         async for stock in Portfolio.objects.filter(user_id=user):
#             ticker_choices.append((stock.ticker, stock.ticker))
#         end_time = time.time()
#         execution_time = end_time - start_time
#         # print(f"Execution time: {execution_time} seconds")
#         return render(request, "portfolio/sell_stock.html", {
#             "form": SellStockForm(ticker_choices=ticker_choices)
#         })