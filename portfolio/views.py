from django.contrib.auth.decorators import login_required
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.db.models import Avg, F
from .models import Portfolio, User, Transaction

import yfinance as yf
from datetime import datetime

class StockForm(forms.Form):
    ticker = forms.CharField(label="Stock ticker")
    number_stocks = forms.FloatField(label="Number of stock", min_value=0, step_size=0.00001)
    price_stocks = forms.FloatField(label="Price", min_value=0, step_size=0.01)
    date = forms.DateField(
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
def buy_stock(request):
    # if not request.user.is_authenticated:
    #     return HttpResponseRedirect(reverse("users:login"))

    if request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data["ticker"]
            number_stocks = form.cleaned_data["number_stocks"]
            price_stocks = form.cleaned_data["price_stocks"]
            buy_date = form.cleaned_data["date"]
            # Look up the ticker symbol using yfinance
            try:
                stock_data = yf.Ticker(ticker)

                # Extract relevant information such as price, name, etc.
                industry = stock_data.info['sector']
                exDividendDate = stock_data.info['exDividendDate']
                user = User.objects.get(id='f1c3285c-67d3-403e-a5bb-cf2fcaeddcd3')

                new_stock = Transaction.objects.create(
                    operation="buy",
                    ticker=ticker,
                    operation_date=buy_date,
                    n_stock=number_stocks,
                    price=price_stocks,
                    user_id=user
                )

                # Get the Portfolio entry for the user and ticker, if it exists
                portfolio_entry = Portfolio.objects.filter(user_id=user, ticker=ticker).first()

                if portfolio_entry:
                    # Update avg_price and n_stock if the entry exists
                    transactions = Transaction.objects.filter(user_id=user, ticker=ticker)
                    average_price = transactions.aggregate(avg_price=Avg('price'))['avg_price']
                    
                    # Update the Portfolio entry
                    portfolio_entry.avg_price = round(average_price,2)
                    portfolio_entry.n_stock += number_stocks

                    # Check if buy_date is before next_exdiv_payment
                    if buy_date < portfolio_entry.next_exdiv_payment:
                        portfolio_entry.n_stock_next_exdiv_payment += number_stocks

                    portfolio_entry.save()
                else:
                    # Create a new Portfolio entry if it doesn't exist
                    Portfolio.objects.create(
                        ticker=ticker,
                        name=ticker,
                        n_stock=number_stocks,
                        avg_price=price_stocks,
                        industry=industry,
                        n_stock_next_exdiv_payment=number_stocks,
                        next_exdiv_payment=datetime.fromtimestamp(exDividendDate),
                        user_id=user
                    )
                
                # Redirect to the portfolio index page
                return HttpResponseRedirect(reverse("portfolio:index"))
            except Exception as e:
                # Handle any errors, such as invalid ticker symbols
                form.add_error("ticker", str(e))
                return render(request, "portfolio/buy_stock.html", {
                    "form": form
                })
        else:
            print('else')
            return render(request, "portfolio/buy_stock.html", {
                "form": form
            })
    return render(request, "portfolio/buy_stock.html", {
        "form": StockForm()
    })


@login_required
def sell_stock(request):
    # if not request.user.is_authenticated:
    #     return HttpResponseRedirect(reverse("users:login"))

    if request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data["ticker"]
            number_stocks = form.cleaned_data["number_stocks"]
            price_stocks = form.cleaned_data["price_stocks"]
            sell_date = form.cleaned_data["date"]
            # Look up the ticker symbol using yfinance
            try:
                user = User.objects.get(id='f1c3285c-67d3-403e-a5bb-cf2fcaeddcd3')

                # Get the Portfolio entry for the user and ticker, if it exists
                portfolio_entry = Portfolio.objects.filter(user_id=user, ticker=ticker).first()

                if not portfolio_entry:
                    raise ValueError("Stock not in portfolio")

                sell_stock = Transaction.objects.create(
                    operation="sell",
                    ticker=ticker,
                    operation_date=sell_date,
                    n_stock=number_stocks,
                    price=price_stocks,
                    user_id=user
                )


                if portfolio_entry:
                    # Update the Portfolio entry
                    portfolio_entry.n_stock -= number_stocks

                    # Check if buy_date is before next_exdiv_payment
                    if sell_date < portfolio_entry.next_exdiv_payment:
                        portfolio_entry.n_stock_next_exdiv_payment -= number_stocks

                    portfolio_entry.save()
                
                # Redirect to the portfolio index page
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
    return render(request, "portfolio/sell_stock.html", {
        "form": StockForm()
    })