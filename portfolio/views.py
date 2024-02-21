from django.contrib.auth.decorators import login_required
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages, auth
from django.db.models import Avg, F
from .models import Portfolio, Transaction
from asgiref.sync import sync_to_async
from django.db.models import Q

import yfinance as yf
from datetime import datetime
import time

class BuyStockForm(forms.Form):
    ticker = forms.CharField(label="Stock ticker")
    number_stocks = forms.FloatField(label="Number of stock", min_value=0, step_size=0.00001)
    price_stocks = forms.FloatField(label="Price", min_value=0, step_size=0.01)
    date = forms.DateField(
        label="Date",
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        input_formats=["%Y-%m-%d"]
    )


class SellStockForm(forms.Form):

    def __init__(self, user, *args, **kwargs):
        super(SellStockForm, self).__init__(*args, **kwargs)
        # Filter tickers based on user's portfolio
        portfolio_entries = Portfolio.objects.filter(user_id=user)
        
        if portfolio_entries.exists():
            ticker_choices = [(entry.ticker, entry.ticker) for entry in portfolio_entries]
            self.fields['ticker'] = forms.ChoiceField(
                label="Stock ticker",
                choices=ticker_choices,
                # initial='',
                # disabled=True,
                # required=False
            )
        else:
            self.fields['ticker'] = forms.ChoiceField(
                label="Stock ticker",
                choices=[('', '---')],
                initial='',
                disabled=True,
                required=False
            )

        self.fields['number_stocks'] = forms.FloatField(label="Number of stock", min_value=0)
        self.fields['price_stocks'] = forms.FloatField(label="Price", min_value=0)
        self.fields['date'] = forms.DateField(
            label="Date",
            widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            input_formats=["%Y-%m-%d"]
        )

# Create your views here.
@login_required
def index(request):
    # if not request.user.is_authenticated:
    #     return HttpResponseRedirect(reverse("users:login"))

    return render(request, "portfolio/index.html", {
        "stocks" : Portfolio.objects.all()
    })

@login_required
def load_buy_stock(request):
    return render(request, "portfolio/buy_stock.html", {
        "form": BuyStockForm()
    })

async def save_buy_stock(request):
    start_time = time.time()
    # if not await sync_to_async(request.user.is_authenticated):
    is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()
    if not is_authenticated:
        print("Here")
        return HttpResponseRedirect(reverse("users:login"))
    else:
        # end_time = time.time()
        # execution_time = end_time - start_time
        # print(f"Execution time: {execution_time} seconds")
        # return HttpResponse("ok")
        if request.method == "POST":
            user = await sync_to_async(lambda: request.user)()
            print("user: ", user)
            form = BuyStockForm(request.POST)
            if form.is_valid():
                ticker = form.cleaned_data["ticker"]
                number_stocks = form.cleaned_data["number_stocks"]
                price_stocks = form.cleaned_data["price_stocks"]
                buy_date = form.cleaned_data["date"]
                print(ticker, number_stocks, price_stocks, buy_date)
                try:
                    stock_data = yf.Ticker(ticker)
                    # Extract relevant information such as price, name, etc.
                    industry = stock_data.info['sector']
                    stock_name = stock_data.info['shortName']
                    exDividendDate = stock_data.info['exDividendDate']
                    next_exdiv_payment = datetime.fromtimestamp(exDividendDate)

                    print(industry, next_exdiv_payment)
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
                    print("got portfolio_entry")
                    print(portfolio_entry)
                    mid_time = time.time()
                    execution_mid_time = mid_time - start_time
                    print(f"Mid execution time: {execution_mid_time} seconds")
                    print(True if portfolio_entry else False)
                    if portfolio_entry:
                        # Update avg_price and n_stock if the entry exists
                        transactions = Transaction.objects.filter(user_id=user, ticker=ticker)
                        print("got transactions")
                        average_price = await sync_to_async(lambda: transactions.aggregate(avg_price=Avg('price'))['avg_price'])()
                        print("got average_price")
                        
                        # Update the Portfolio entry
                        portfolio_entry.avg_price = round(average_price,2)
                        portfolio_entry.n_stock += number_stocks

                        # Check if buy_date is before next_exdiv_payment
                        if buy_date < portfolio_entry.next_exdiv_payment:
                            portfolio_entry.n_stock_next_exdiv_payment += number_stocks

                        await sync_to_async(portfolio_entry.save)()
                        print("portfolio_entry saved")
                    
                    else:
                        # Create a new Portfolio entry if it doesn't exist
                        print(industry, next_exdiv_payment)
                        new_stock = await Portfolio.objects.acreate(
                            ticker=ticker,
                            name=stock_name,
                            n_stock=number_stocks,
                            avg_price=price_stocks,
                            industry=industry,
                            n_stock_next_exdiv_payment=number_stocks if buy_date < next_exdiv_payment.date() else 0,
                            next_exdiv_payment=next_exdiv_payment,
                            user_id=user
                        )
                        second_mid_time = time.time()
                        execution_second_mid_time = mid_time - start_time
                        print(f"Mid Second execution time: {execution_second_mid_time} seconds")
                    
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
                # end_time = time.time()
                # execution_time = end_time - start_time
                # print(f"Execution time: {execution_time} seconds")
                # return HttpResponse("ok")

@login_required
def sync_load_sell_stock(request):
    return render(request, "portfolio/sell_stock.html", {
        "form": SellStockForm(user=request.user)
    })

async def save_sell_stock(request):
    start_time = time.time()
    # if not await sync_to_async(request.user.is_authenticated):
    is_authenticated = await sync_to_async(lambda: request.user.is_authenticated)()
    if not is_authenticated:
        print("Here")
        return HttpResponseRedirect(reverse("users:login"))
    else:
        user = await sync_to_async(lambda: request.user)()
        if request.method == "POST":
            print("user: ", user)
            form = BuyStockForm(request.POST)
            if form.is_valid():
                ticker = form.cleaned_data["ticker"]
                number_stocks = form.cleaned_data["number_stocks"]
                price_stocks = form.cleaned_data["price_stocks"]
                sell_date = form.cleaned_data["date"]
                print(ticker, number_stocks, price_stocks, sell_date)
                try:
                    # Get the Portfolio entry for the user and ticker, if it exists
                    portfolio_entry = await Portfolio.objects.filter(user_id=user, ticker=ticker).afirst()
                    print("got portfolio_entry")
                    if not portfolio_entry:
                        raise ValueError("Stock not in portfolio")

                    if number_stocks > portfolio_entry.n_stock:
                        raise ValueError("Selling more stocks than in portfolio")

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
                        print("portfolio_entry deleted")
                    else:
                        print("enter else")
                        portfolio_entry.n_stock -= number_stocks
                        print("reduce n_stock")

                        # Check if sell_date is before next_exdiv_payment
                        if sell_date < portfolio_entry.next_exdiv_payment:
                            print("reduce n_stock_next_exdiv_payment")
                            portfolio_entry.n_stock_next_exdiv_payment -= number_stocks

                        await sync_to_async(portfolio_entry.save)()
                        print("portfolio_entry saved")

                    # Redirect to the portfolio index page
                    mid_time = time.time()
                    execution_mid_time = mid_time - start_time
                    print(f"Mid execution time: {execution_mid_time} seconds")
                    return HttpResponseRedirect(reverse("portfolio:index"))
                except Exception as e:
                    # Handle any errors, such as invalid ticker symbols
                    form.add_error("ticker", str(e))
                    messages.error(request, "Error: Stock not in portfolio.")
                    return render(request, "portfolio/sell_stock.html", {
                        "form": form
                    })
            else:
                return render(request, "portfolio/sell_stock.html", {
                    "form": form
                }) 
        else:
            return render(request, "portfolio/sell_stock.html", {
                "form": SellStockForm(user=user)
            })

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