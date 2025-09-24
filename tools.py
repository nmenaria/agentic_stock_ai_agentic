from yahooquery import search, Ticker
import json, os

WATCHLIST_FILE = "watchlist.json"
THRESHOLDS_FILE = "thresholds.json"

def _load_json(file, default):
    if not os.path.exists(file):
        return default
    try:
        with open(file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def _save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ----- watchlist -----
def _load_watchlist():
    return _load_json(WATCHLIST_FILE, [])

def _save_watchlist(watchlist):
    _save_json(WATCHLIST_FILE, watchlist)

def add_to_watchlist(symbol: str):
    watchlist = _load_watchlist()
    if symbol not in watchlist:
        watchlist.append(symbol)
        _save_watchlist(watchlist)
        return f"{symbol} added to watchlist."
    return f"{symbol} already in watchlist."

def show_watchlist() -> list:
    return _load_watchlist()

# ----- thresholds -----
def get_thresholds():
    return _load_json(THRESHOLDS_FILE, {"roe": 15, "peg": 2})

def set_thresholds(roe: float, peg: float):
    _save_json(THRESHOLDS_FILE, {"roe": roe, "peg": peg})
    return f"Thresholds updated to ROE>{roe}% and PEG<{peg}"

# ----- data -----
def get_symbol(company_name: str) -> str:
    results = search(company_name)
    quotes = results.get('quotes', [])
    if not quotes:
        return None
    return quotes[0]['symbol']

def get_fundamentals(symbol: str) -> dict:
    t = Ticker(symbol)
    key_stats = t.key_stats.get(symbol, {})
    return {
        'symbol': symbol,
        'roe': key_stats.get('returnOnEquity'),
        'peg': key_stats.get('pegRatio')
    }

# ----- screening -----
def screen_and_add(company_name: str):
    thresholds = get_thresholds()
    roe_thr, peg_thr = thresholds["roe"], thresholds["peg"]

    symbol = get_symbol(company_name)
    if not symbol:
        return f"Could not find symbol for {company_name}"
    fundamentals = get_fundamentals(symbol)
    roe = fundamentals.get('roe') or 0
    peg = fundamentals.get('peg') or float('inf')
    if roe * 100 > roe_thr and peg < peg_thr:
        add_to_watchlist(symbol)
        return f"{company_name} ({symbol}) passed criteria and added to watchlist."
    else:
        return f"{company_name} ({symbol}) did not pass criteria. ROE={roe}, PEG={peg}"
