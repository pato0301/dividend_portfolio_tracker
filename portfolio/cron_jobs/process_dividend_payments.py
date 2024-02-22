from datetime import datetime
import yfinance as yf
from .models import Portfolio, DividendPayment

def process_dividend_payments():
    # Get today's date
    today = date.today()

    # Filter Portfolio records with next_exdiv_payment = today
    portfolios = Portfolio.objects.filter(next_exdiv_payment=today)

    # Get unique list of tickers
    unique_tickers = portfolios.values_list('ticker', flat=True).distinct()

    for ticker in unique_tickers:
        # stock_data = yf.Ticker(ticker)
        last_dividend_value = yf.Ticker(ticker).lastDividendValue
        next_exDividendDate = yf.Ticker(ticker).exDividendDate

        # Filter Portfolio records for the ticker
        portfolios_for_ticker = portfolios.filter(ticker=ticker)

        # Iterate over portfolios for the ticker and save DividendPayment records
        for portfolio in portfolios_for_ticker:
            # Create DividendPayment record
            dividend_payment = DividendPayment.objects.create(
                ticker=ticker,
                payment_date=today,
                amount_per_stock=last_dividend_value,
                n_stock=portfolio.n_stock_next_exdiv_payment,
                user_id=portfolio.user_id
            )

            # Check if n_stock = 0, then delete the record
            if portfolio.n_stock == 0:
                portfolio.delete()
            else:
                # Update n_stock_next_exdiv_payment = n_stock
                portfolio.n_stock_next_exdiv_payment = portfolio.n_stock
                portfolio.next_exdiv_payment = datetime.utcfromtimestamp(next_exDividendDate)
                portfolio.save()


# def check_dividend_payments():
#     today = datetime.now().date()
#     stocks_to_check = Portfolio.objects.filter(next_exdiv_payment=today)

#     for stock in stocks_to_check:
#         if stock.n_stock_next_exdiv_payment > 0:
#             ticker = stock.ticker
#             lastDividendValue = yf.Ticker(ticker).lastDividendValue
#             next_exDividendDate = yf.Ticker(ticker).exDividendDate

#             if not dividend_data.empty:
#                 for index, row in dividend_data.iterrows():
#                     DividendPayment.objects.create(
#                         ticker=ticker,
#                         payment_date=today,
#                         amount_per_stock=row['Dividends'],
#                         n_stock=stock.n_stock,
#                         user_id=stock.user_id
#                     )


#         stock.n_stock_next_exdiv_payment = n_stock
#         stock.next_exdiv_payment = datetime.utcfromtimestamp(next_exDividendDate)