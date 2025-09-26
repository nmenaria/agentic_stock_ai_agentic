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


# Helper function to determine market information
def _get_market_info(symbol: str) -> dict:
    """Determine market, currency, and currency symbol based on stock symbol"""
    if '.NS' in symbol or '.BO' in symbol:  # Indian markets (NSE or BSE)
        return {
            'market': 'NSE' if '.NS' in symbol else 'BSE',
            'currency': 'INR',
            'currency_symbol': '₹'
        }
    elif '.TO' in symbol:  # Toronto Stock Exchange
        return {
            'market': 'TSX',
            'currency': 'CAD',
            'currency_symbol': 'C$'
        }
    elif '.L' in symbol:  # London Stock Exchange
        return {
            'market': 'LSE',
            'currency': 'GBP',
            'currency_symbol': '£'
        }
    elif '.AX' in symbol:  # Australian Stock Exchange
        return {
            'market': 'ASX',
            'currency': 'AUD',
            'currency_symbol': 'A$'
        }
    else:  # Default to US markets
        return {
            'market': 'US (NASDAQ/NYSE)',
            'currency': 'USD',
            'currency_symbol': '$'
        }


# Helper functions for formatting
def _format_number(value, decimal_places=2):
    """Format a number with specified decimal places"""
    if value is None or (isinstance(value, (int, float)) and (value != value or value == float('inf'))):  # Check for None or NaN
        return "N/A"
    try:
        return f"{float(value):.{decimal_places}f}"
    except (ValueError, TypeError):
        return "N/A"


def _format_percentage(value):
    """Format a value as a percentage"""
    if value is None or (isinstance(value, (int, float)) and (value != value or value == float('inf'))):
        return "N/A"
    try:
        # If the value is already in percentage form (> 1), use it directly
        # If it's in decimal form (< 1), convert to percentage
        if float(value) < 1:
            return f"{float(value) * 100:.2f}%"
        else:
            return f"{float(value):.2f}%"
    except (ValueError, TypeError):
        return "N/A"


def _format_large_number(value):
    """Format large numbers with B, M, K suffixes"""
    if value is None or (isinstance(value, (int, float)) and (value != value or value == float('inf'))):
        return "N/A"
    try:
        value = float(value)
        if abs(value) >= 1e12:
            return f"${value/1e12:.2f}T"
        elif abs(value) >= 1e9:
            return f"${value/1e9:.2f}B"
        elif abs(value) >= 1e6:
            return f"${value/1e6:.2f}M"
        elif abs(value) >= 1e3:
            return f"${value/1e3:.2f}K"
        else:
            return f"${value:.2f}"
    except (ValueError, TypeError):
        return "N/A"

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
    """
    Search for a stock symbol based on company name.
    Enhanced with Indian market companies and both NSE/ADR options.
    """
    
    # Enhanced mapping of common companies to their symbols (including Indian companies)
    COMMON_STOCKS = {
        # US Companies
        'apple': 'AAPL',
        'microsoft': 'MSFT',
        'amazon': 'AMZN',
        'netflix': 'NFLX',
        'google': 'GOOGL',
        'alphabet': 'GOOGL',
        'tesla': 'TSLA',
        'meta': 'META',
        'facebook': 'META',
        'nvidia': 'NVDA',
        'berkshire hathaway': 'BRK-A',
        'visa': 'V',
        'johnson & johnson': 'JNJ',
        'walmart': 'WMT',
        'procter & gamble': 'PG',
        'mastercard': 'MA',
        'unitedhealth': 'UNH',
        'home depot': 'HD',
        'jpmorgan chase': 'JPM',
        'coca-cola': 'KO',
        'pepsico': 'PEP',
        'disney': 'DIS',
        'verizon': 'VZ',
        'at&t': 'T',
        'intel': 'INTC',
        'cisco': 'CSCO',
        'pfizer': 'PFE',
        'merck': 'MRK',
        'abbott': 'ABT',
        'salesforce': 'CRM',
        'oracle': 'ORCL',
        'adobe': 'ADBE',
        'broadcom': 'AVGO',
        'comcast': 'CMCSA',
        'thermo fisher': 'TMO',
        'accenture': 'ACN',
        'danaher': 'DHR',
        'mcdonald\'s': 'MCD',
        'costco': 'COST',
        'nextera energy': 'NEE',
        
        # Indian Companies (NSE)
        'tata consultancy services': 'TCS.NS',
        'tcs': 'TCS.NS',
        'reliance industries': 'RELIANCE.NS',
        'reliance': 'RELIANCE.NS',
        'hdfc bank': 'HDFCBANK.NS',
        'icici bank': 'ICICIBANK.NS',
        'infosys': 'INFY.NS',
        'hindustan unilever': 'HINDUNILVR.NS',
        'hul': 'HINDUNILVR.NS',
        'itc': 'ITC.NS',
        'state bank of india': 'SBIN.NS',
        'sbi': 'SBIN.NS',
        'bharti airtel': 'BHARTIARTL.NS',
        'airtel': 'BHARTIARTL.NS',
        'kotak mahindra bank': 'KOTAKBANK.NS',
        'kotak bank': 'KOTAKBANK.NS',
        'axis bank': 'AXISBANK.NS',
        'larsen & toubro': 'LT.NS',
        'l&t': 'LT.NS',
        'wipro': 'WIPRO.NS',
        'hcl technologies': 'HCLTECH.NS',
        'hcl tech': 'HCLTECH.NS',
        'bajaj finance': 'BAJFINANCE.NS',
        'maruti suzuki': 'MARUTI.NS',
        'maruti': 'MARUTI.NS',
        'asian paints': 'ASIANPAINT.NS',
        'tata steel': 'TATASTEEL.NS',
        'tata motors': 'TATAMOTORS.NS',
        'tata motor': 'TATAMOTORS.NS',
        'tatamotors': 'TATAMOTORS.NS',
        'tatamotor': 'TATAMOTORS.NS',
        'sun pharma': 'SUNPHARMA.NS',
        'sun pharmaceutical': 'SUNPHARMA.NS',
        'ntpc': 'NTPC.NS',
        'powergrid': 'POWERGRID.NS',
        'power grid corporation': 'POWERGRID.NS',
        'ultratech cement': 'ULTRACEMCO.NS',
        'ultratech': 'ULTRACEMCO.NS',
        'ongc': 'ONGC.NS',
        'oil and natural gas corporation': 'ONGC.NS',
        'bajaj finserv': 'BAJAJFINSV.NS',
        'tech mahindra': 'TECHM.NS',
        'dr reddy': 'DRREDDY.NS',
        'dr reddys': 'DRREDDY.NS',
        'titan company': 'TITAN.NS',
        'titan': 'TITAN.NS',
        'nestle india': 'NESTLEIND.NS',
        'nestle': 'NESTLEIND.NS',
        'hero motocorp': 'HEROMOTOCO.NS',
        'hero': 'HEROMOTOCO.NS',
        'adani enterprises': 'ADANIENT.NS',
        'adani': 'ADANIENT.NS',
        'indusind bank': 'INDUSINDBK.NS',
        'mahindra & mahindra': 'M&M.NS',
        'mahindra': 'M&M.NS',
        'coal india': 'COALINDIA.NS',
        'grasim industries': 'GRASIM.NS',
        'grasim': 'GRASIM.NS',
        'britannia industries': 'BRITANNIA.NS',
        'britannia': 'BRITANNIA.NS',
        'shree cement': 'SHREECEM.NS',
        'divislab': 'DIVISLAB.NS',
        'divis laboratories': 'DIVISLAB.NS',
        'eicher motors': 'EICHERMOT.NS',
        'eicher': 'EICHERMOT.NS',
        'sbi life': 'SBILIFE.NS',
        'sbi life insurance': 'SBILIFE.NS',
        'hdfc life': 'HDFCLIFE.NS',
        'hdfc life insurance': 'HDFCLIFE.NS',
        'icici lombard': 'ICICIGI.NS',
        'icici prudential': 'ICICIPRULI.NS',
        'bajaj auto': 'BAJAJ-AUTO.NS',
        'cipla': 'CIPLA.NS',
        'tata consumer products': 'TATACONSUM.NS',
        'tata consumer': 'TATACONSUM.NS',
        
        # Indian ADRs trading on US exchanges (for users who prefer USD trading)
        'hdfc bank adr': 'HDB',
        'infosys adr': 'INFY',
        'tata motors adr': 'TTM',
        'wipro adr': 'WIT',
        'icici bank adr': 'IBN',
        'dr reddys adr': 'RDY',
    }
    
    # First, try direct lookup (case-insensitive)
    name_lower = company_name.lower().strip()
    if name_lower in COMMON_STOCKS:
        return COMMON_STOCKS[name_lower]
    
    # Try to handle some common variations and abbreviations
    name_variations = [
        name_lower.replace(' limited', '').replace(' ltd', '').strip(),
        name_lower.replace(' inc', '').replace(' corp', '').replace(' corporation', '').strip(),
        name_lower.replace(' company', '').replace(' co', '').strip(),
        name_lower.replace('&', 'and').strip(),
        name_lower.replace(' and ', ' & ').strip()
    ]
    
    for variation in name_variations:
        if variation in COMMON_STOCKS:
            return COMMON_STOCKS[variation]
    
    # If not found in mapping, use yahooquery search
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
        
        # Determine market and currency
        market_info = _get_market_info(symbol)
        
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
            'market': market_info['market'],
            'currency': market_info['currency'],
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

Market Information:
- Exchange: {market_info['market']}
- Currency: {market_info['currency']}

Company Details:
- Sector: {info['sector']}
- Industry: {info['industry']}
- Current Price: {market_info['currency_symbol']}{info['current_price']} 
- Market Cap: {_format_large_number(info['market_cap'])}
- Enterprise Value: {_format_large_number(info['enterprise_value'])}
- 52-Week Range: {market_info['currency_symbol']}{info['52_week_low']} - {market_info['currency_symbol']}{info['52_week_high']}

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
        
        # Handle PEG more intelligently - if PEG is not available, don't penalize the stock
        if peg is not None and peg_val != float('inf'):
            meets_peg = peg_val < peg_thr
            peg_available = True
        else:
            meets_peg = True  # Don't penalize for missing PEG data
            peg_available = False
        
        # If both ROE and PEG are available, both must pass
        # If only ROE is available, just ROE needs to pass
        if peg_available:
            meets_criteria = meets_roe and meets_peg
        else:
            meets_criteria = meets_roe  # Only require ROE if PEG is not available
        
        # Build the analysis result
        result = detailed_info['formatted_info']
        
        # Add threshold analysis
        result += f"\n\nThreshold Analysis:"
        result += f"\n- Current Thresholds: ROE > {roe_thr}%, PEG < {peg_thr}"
        result += f"\n- ROE Check: {_format_percentage(roe)} {'✅ PASS' if meets_roe else '❌ FAIL'} (threshold: >{roe_thr}%)"
        
        if peg_available:
            result += f"\n- PEG Check: {_format_number(peg)} {'✅ PASS' if meets_peg else '❌ FAIL'} (threshold: <{peg_thr})"
        else:
            result += f"\n- PEG Check: {_format_number(peg)} ⚠️ DATA NOT AVAILABLE (threshold: <{peg_thr}) - Not penalized"
        
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
            if peg_available and not meets_peg:
                result += f"PEG too high ({_format_number(peg)} >= {peg_thr}) "
            if not peg_available and not meets_roe:
                result += f"(PEG data unavailable, evaluated on ROE only)"

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
        result += f"\n\nNOTE: This is a comprehensive analysis without threshold screening."
        result += f"\nUse 'Screen and Add' if you want to check against thresholds and potentially add to watchlist."
        
        return result

    except Exception as e:
        return f"Error analyzing {company_name}: {e}"
