import yfinance as yf

def get_sector(ticker):
    try:
        stock_data = yf.Ticker(ticker)
        sector = stock_data.info.get('sector', None)
        return sector
    except:
        return None