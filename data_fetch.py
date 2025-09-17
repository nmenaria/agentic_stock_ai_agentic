import yfinance as yf
from yahooquery import search

def company_name_to_symbol(name):
    """
    Dynamically convert company name to ticker symbol using yahooquery search API.
    """
    try:
        result = search(name)
        quotes = result.get('quotes')
        if quotes:
            return quotes[0]['symbol']  # take first match
    except Exception as e:
        print(f"Error fetching symbol for {name}: {e}")
    return None

def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info
    return {
        'symbol': symbol,
        'market_cap': info.get('marketCap'),
        'pe_ratio': info.get('trailingPE'),
        'peg_ratio': info.get('pegRatio'),
        'roe': info.get('returnOnEquity'),
        'price': info.get('regularMarketPrice')
    }
