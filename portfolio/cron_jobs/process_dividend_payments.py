from datetime import datetime
import yfinance as yf
from .models import Portfolio, DividendPayment

def process_dividend_payments():
    # Get today's date
    today = datetime.today()

    # Filter Portfolio records with next_exdiv_payment = today
    portfolios =  Portfolio.objects.filter(next_exdiv_payment=today)

    # Get unique list of tickers
    unique_tickers = portfolios.values_list('ticker', flat=True).distinct()

    for ticker in unique_tickers:
        stock_data = yf.Ticker(ticker)
        last_dividend_value = stock_data.info["lastDividendValue"]
        exDividendDate = stock_data.info['exDividendDate']
        next_exdiv_payment = datetime.fromtimestamp(exDividendDate)

        # Filter Portfolio records for the ticker
        portfolios_for_ticker =  portfolios.filter(ticker=ticker)

        # Iterate over portfolios for the ticker and save DividendPayment records
        for portfolio in portfolios_for_ticker:
            # Create DividendPayment record
            dividend_payment = DividendPayment.objects.create(
                ticker=ticker,
                payment_date=today,
                amount=last_dividend_value,
                n_stock=portfolio.n_stock_next_exdiv_payment,
                user_id=portfolio.user_id
            )

            # Check if n_stock = 0, then delete the record
            if portfolio.n_stock == 0:
                portfolio.delete()
            else:
                # Update n_stock_next_exdiv_payment = n_stock
                portfolio.n_stock_next_exdiv_payment = portfolio.n_stock
                portfolio.next_exdiv_payment = next_exdiv_payment
                portfolio.save()


"""
After running some test the async version is slower
so I am keeping the sync version for prod.
"""
async def process_dividend_payments():
    # Get today's date
    today = datetime.today()

    # Filter Portfolio records with next_exdiv_payment = today
    portfolios = await sync_to_async(Portfolio.objects.filter)(next_exdiv_payment=today)

    # Get unique list of tickers
    unique_tickers = await sync_to_async(list)(portfolios.values_list('ticker', flat=True).distinct())

    for ticker in unique_tickers:
        stock_data = yf.Ticker(ticker)
        last_dividend_value = stock_data.info["lastDividendValue"]
        exDividendDate = stock_data.info['exDividendDate']
        next_exdiv_payment = datetime.fromtimestamp(exDividendDate)

        # Filter Portfolio records for the ticker
        portfolios_for_ticker = await sync_to_async(list)(portfolios.filter(ticker=ticker))

        # Iterate over portfolios for the ticker and save DividendPayment records
        for portfolio in portfolios_for_ticker:
            # Create DividendPayment record
            dividend_payment = await DividendPayment.objects.acreate(
                ticker=ticker,
                payment_date=today,
                amount=last_dividend_value,
                n_stock=portfolio.n_stock_next_exdiv_payment,
                user_id=portfolio.user_id
            )

            # Check if n_stock = 0, then delete the record
            if portfolio.n_stock == 0:
                await portfolio.adelete()
            else:
                # Update n_stock_next_exdiv_payment = n_stock
                portfolio.n_stock_next_exdiv_payment = portfolio.n_stock
                portfolio.next_exdiv_payment = next_exdiv_payment
                await sync_to_async(portfolio.save)()