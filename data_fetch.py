import yfinance as yf

def company_name_to_symbol(company_name):
    """
    Convert company name to ticker symbol using yfinance search.
    Returns the first match if found, else None.
    """
    try:
        search_results = yf.utils.get_yf_tickers(company_name)
        if search_results:
            return search_results[0]
    except Exception as e:
        print(f"Error converting company name to symbol: {str(e)}")
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
