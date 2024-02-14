from datetime import datetime
from background_task import background
import yfinance as yf
from .models import Portfolio, DividendPayment

@background(schedule=time(1, 0))  # Run every day at 1:00 AM
def check_dividend_payments():
    today = datetime.now().date()
    stocks_to_check = Portfolio.objects.filter(next_exdiv_payment=today)
    
    for stock in stocks_to_check:
        if stock.n_stock_next_exdiv_payment > 0:
            ticker = stock.ticker
            lastDividendValue = yf.Ticker(ticker).lastDividendValue
            next_exDividendDate = yf.Ticker(ticker).exDividendDate
            
            if not dividend_data.empty:
                for index, row in dividend_data.iterrows():
                    DividendPayment.objects.create(
                        ticker=ticker,
                        payment_date=index.date(),
                        amount_per_stock=row['Dividends'],
                        n_stock=stock.n_stock,
                        user_id=stock.user_id
                    )


        stock.n_stock_next_exdiv_payment = n_stock
        stock.next_exdiv_payment = datetime.utcfromtimestamp(next_exDividendDate)