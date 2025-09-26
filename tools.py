from yahooquery import search, Ticker
import json, os

WATCHLIST_FILE = "watchlist.json"
THRESHOLDS_FILE = "thresholds.json"

# ----- helpers -----
def _load_json(file, default):
    try:
        if not os.path.exists(file):
            return default
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def _save_json(file, data):
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving {file}: {e}")

# ----- watchlist -----
def _load_watchlist():
    return _load_json(WATCHLIST_FILE, [])

def _save_watchlist(watchlist):
    _save_json(WATCHLIST_FILE, watchlist)

def add_to_watchlist(symbol: str):
    try:
        watchlist = _load_watchlist()
        if symbol not in watchlist:
            watchlist.append(symbol)
            _save_watchlist(watchlist)
            return f"{symbol} added to watchlist."
        return f"{symbol} already in watchlist."
    except Exception as e:
        return f"Error adding {symbol} to watchlist: {e}"

def remove_from_watchlist(symbol: str):
    """Remove a stock symbol from the watchlist"""
    try:
        watchlist = _load_watchlist()
        if symbol in watchlist:
            watchlist.remove(symbol)
            _save_watchlist(watchlist)
            return f"{symbol} removed from watchlist."
        return f"{symbol} not found in watchlist."
    except Exception as e:
        return f"Error removing {symbol} from watchlist: {e}"

def clear_watchlist():
    """Clear all stocks from the watchlist"""
    try:
        _save_watchlist([])
        return "Watchlist cleared successfully."
    except Exception as e:
        return f"Error clearing watchlist: {e}"

def show_watchlist() -> list:
    try:
        return _load_watchlist()
    except Exception as e:
        return [f"Error loading watchlist: {e}"]

# ----- thresholds -----
def get_thresholds():
    try:
        return _load_json(THRESHOLDS_FILE, {"roe": 15, "peg": 2})
    except Exception as e:
        return {"roe": 15, "peg": 2, "error": str(e)}

def set_thresholds(roe: float, peg: float):
    try:
        _save_json(THRESHOLDS_FILE, {"roe": roe, "peg": peg})
        return f"Thresholds updated to ROE>{roe}% and PEG<{peg}"
    except Exception as e:
        return f"Error updating thresholds: {e}"

# ----- data -----
def get_symbol(company_name: str) -> str:
    try:
        results = search(company_name)
        quotes = results.get('quotes', [])
        if not quotes:
            return f"Could not find symbol for {company_name}"
        return quotes[0]['symbol']
    except Exception as e:
        return f"Error fetching symbol for {company_name}: {e}"

def get_fundamentals(symbol: str) -> dict:
    try:
        t = Ticker(symbol)
        # Try financial_data first, then key_stats as fallback
        financial_data = t.financial_data.get(symbol, {})
        key_stats = t.key_stats.get(symbol, {})
        
        # Get ROE from financial_data, PEG from key_stats
        roe = financial_data.get('returnOnEquity') or key_stats.get('returnOnEquity')
        peg = key_stats.get('pegRatio')
        
        return {'symbol': symbol, 'roe': roe, 'peg': peg}
    except Exception as e:
        return {'symbol': symbol, 'roe': None, 'peg': None, 'error': str(e)}

def get_detailed_stock_info(symbol: str) -> dict:
    """Get comprehensive stock information including fundamentals, price, and company details"""
    try:
        t = Ticker(symbol)
        
        # Get different data modules
        key_stats = t.key_stats.get(symbol, {})
        financial_data = t.financial_data.get(symbol, {})
        summary_detail = t.summary_detail.get(symbol, {})
        price_info = t.price.get(symbol, {})
        profile = t.asset_profile.get(symbol, {})
        
        # Extract key metrics from the most reliable sources
        info = {
            'symbol': symbol,
            'company_name': price_info.get('shortName', 'N/A'),
            'sector': profile.get('sector', 'N/A'),
            'industry': profile.get('industry', 'N/A'),
            'current_price': summary_detail.get('regularMarketPrice', summary_detail.get('previousClose', 'N/A')),
            'market_cap': price_info.get('marketCap', 'N/A'),
            'roe': financial_data.get('returnOnEquity') or key_stats.get('returnOnEquity'),
            'peg': key_stats.get('pegRatio'),
            'pe_ratio': key_stats.get('trailingPE') or key_stats.get('forwardPE'),
            'price_to_book': key_stats.get('priceToBook'),
            'debt_to_equity': financial_data.get('debtToEquity'),
            'revenue_growth': financial_data.get('revenueGrowth') or key_stats.get('revenueQuarterlyGrowth'),
            'profit_margin': key_stats.get('profitMargins'),
            'beta': key_stats.get('beta'),
            'dividend_yield': summary_detail.get('dividendYield'),
            '52_week_high': summary_detail.get('fiftyTwoWeekHigh'),
            '52_week_low': summary_detail.get('fiftyTwoWeekLow'),
            'current_ratio': financial_data.get('currentRatio'),
            'total_cash': financial_data.get('totalCash'),
            'total_debt': financial_data.get('totalDebt'),
            'enterprise_value': key_stats.get('enterpriseValue'),
        }
        
        # Format the information nicely
        formatted_info = f"""
Stock Analysis for {info['company_name']} ({symbol}):

Company Details:
- Sector: {info['sector']}
- Industry: {info['industry']}
- Current Price: ${info['current_price']} 
- Market Cap: {_format_large_number(info['market_cap'])}
- Enterprise Value: {_format_large_number(info['enterprise_value'])}
- 52-Week Range: ${info['52_week_low']} - ${info['52_week_high']}

Key Financial Metrics:
- ROE (Return on Equity): {_format_percentage(info['roe'])}
- PEG Ratio: {_format_number(info['peg'])}
- P/E Ratio: {_format_number(info['pe_ratio'])}
- Price-to-Book: {_format_number(info['price_to_book'])}
- Debt-to-Equity: {_format_number(info['debt_to_equity'])}
- Current Ratio: {_format_number(info['current_ratio'])}
- Profit Margin: {_format_percentage(info['profit_margin'])}
- Revenue Growth: {_format_percentage(info['revenue_growth'])}
- Beta: {_format_number(info['beta'])}
- Dividend Yield: {_format_percentage(info['dividend_yield'])}

Financial Position:
- Total Cash: {_format_large_number(info['total_cash'])}
- Total Debt: {_format_large_number(info['total_debt'])}
"""
        
        return {
            'symbol': symbol,
            'formatted_info': formatted_info.strip(),
            'raw_data': info
        }
        
    except Exception as e:
        return {
            'symbol': symbol,
            'formatted_info': f"Error fetching detailed information for {symbol}: {e}",
            'error': str(e)
        }

def _format_number(value, decimal_places=2):
    """Format a number with proper decimal places or return N/A"""
    if value is None or value == 'N/A':
        return 'N/A'
    try:
        return f"{float(value):.{decimal_places}f}"
    except:
        return 'N/A'

def _format_percentage(value, decimal_places=2):
    """Format a percentage value or return N/A"""
    if value is None or value == 'N/A':
        return 'N/A'
    try:
        return f"{float(value) * 100:.{decimal_places}f}%"
    except:
        return 'N/A'

def _format_large_number(value):
    """Format large numbers (like market cap) in readable format"""
    if value is None or value == 'N/A':
        return 'N/A'
    try:
        num = float(value)
        if num >= 1e12:
            return f"${num/1e12:.2f}T"
        elif num >= 1e9:
            return f"${num/1e9:.2f}B"
        elif num >= 1e6:
            return f"${num/1e6:.2f}M"
        elif num >= 1e3:
            return f"${num/1e3:.2f}K"
        else:
            return f"${num:.2f}"
    except:
        return 'N/A'

# ----- screening -----
def screen_and_add(company_name: str):
    """Screen a company and provide detailed analysis regardless of threshold results"""
    try:
        # Get symbol
        symbol = get_symbol(company_name)
        if not symbol or "Error" in symbol or "Could not find" in symbol:
            return symbol  # return error string

        # Get detailed stock information
        detailed_info = get_detailed_stock_info(symbol)
        if "error" in detailed_info:
            return f"Error fetching detailed information: {detailed_info['error']}"

        # Get thresholds for comparison
        thresholds = get_thresholds()
        roe_thr, peg_thr = thresholds.get("roe", 15), thresholds.get("peg", 2)
        
        # Extract ROE and PEG for threshold comparison
        raw_data = detailed_info.get('raw_data', {})
        roe = raw_data.get('roe')
        peg = raw_data.get('peg')
        
        # Convert ROE to percentage for comparison
        roe_pct = (roe * 100) if roe is not None else 0
        peg_val = peg if peg is not None else float('inf')
        
        # Check if stock meets criteria
        meets_roe = roe_pct > roe_thr if roe is not None else False
        meets_peg = peg_val < peg_thr if peg is not None and peg_val != float('inf') else False
        meets_criteria = meets_roe and meets_peg
        
        # Build the analysis result
        result = detailed_info['formatted_info']
        
        # Add threshold analysis
        result += f"\n\nThreshold Analysis:"
        result += f"\n- Current Thresholds: ROE > {roe_thr}%, PEG < {peg_thr}"
        result += f"\n- ROE Check: {_format_percentage(roe)} {'✅ PASS' if meets_roe else '❌ FAIL'} (threshold: >{roe_thr}%)"
        result += f"\n- PEG Check: {_format_number(peg)} {'✅ PASS' if meets_peg else '❌ FAIL'} (threshold: <{peg_thr})"
        
        # Add to watchlist if meets criteria
        if meets_criteria:
            add_result = add_to_watchlist(symbol)
            result += f"\n\n🎯 OVERALL: MEETS CRITERIA - Added to watchlist"
            result += f"\n{add_result}"
        else:
            result += f"\n\n❌ OVERALL: DOES NOT MEET CRITERIA - Not added to watchlist"
            result += f"\nReasons: "
            if not meets_roe:
                result += f"ROE too low ({_format_percentage(roe)} <= {roe_thr}%) "
            if not meets_peg:
                result += f"PEG too high ({_format_number(peg)} >= {peg_thr}) "

        return result

    except Exception as e:
        return f"Error screening {company_name}: {e}"

def analyze_stock(company_name: str):
    """Provide comprehensive stock analysis without threshold screening"""
    try:
        # Get symbol
        symbol = get_symbol(company_name)
        if not symbol or "Error" in symbol or "Could not find" in symbol:
            return symbol  # return error string

        # Get detailed stock information
        detailed_info = get_detailed_stock_info(symbol)
        if "error" in detailed_info:
            return f"Error fetching detailed information: {detailed_info['error']}"

        result = detailed_info['formatted_info']
        result += f"\n\n📊 This is a comprehensive analysis without threshold screening."
        result += f"\nUse 'Screen and Add' if you want to check against thresholds and potentially add to watchlist."
        
        return result

    except Exception as e:
        return f"Error analyzing {company_name}: {e}"
