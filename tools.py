from yahooquery import search, Ticker
import json, os

WATCHLIST_FILE = "watchlist.json"
THRESHOLDS_FILE = "thresholds.json"

# ----- helpers -----
def _load_json(file, default):
    if not os.path.exists(file):
        return default
    try:
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
        key_stats = t.key_stats.get(symbol, {})
        roe = key_stats.get('returnOnEquity')
        peg = key_stats.get('pegRatio')
        return {'symbol': symbol, 'roe': roe, 'peg': peg}
    except Exception as e:
        return {'symbol': symbol, 'roe': None, 'peg': None, 'error': str(e)}

# ----- screening -----
def screen_and_add(company_name: str):
    try:
        symbol = get_symbol(company_name)
        if not symbol or "Error" in symbol or "Could not find" in symbol:
            return symbol  # return the error string

        fundamentals = get_fundamentals(symbol)
        if "error" in fundamentals:
            return f"Error fetching fundamentals: {fundamentals['error']}"

        thresholds = get_thresholds()
        roe_thr, peg_thr = thresholds.get("roe", 15), thresholds.get("peg", 2)
        roe = (fundamentals.get('roe') or 0) * 100
        peg = fundamentals.get('peg') or float('inf')

        if roe > roe_thr and peg < peg_thr:
            add_to_watchlist(symbol)
            return f"{company_name} ({symbol}) passed criteria and added to watchlist."
        else:
            return f"{company_name} ({symbol}) did not pass criteria. ROE={roe}, PEG={peg}"

    except Exception as e:
        return f"Error screening {company_name}: {e}"
