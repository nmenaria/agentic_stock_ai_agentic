import json
import os

WATCHLIST_FILE = 'watchlist.json'

def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, 'r', encoding='utf-8') as f:  # specify UTF-8
            try:
                return json.load(f)
            except UnicodeDecodeError:
                # If UTF-8 fails, try cp1252
                with open(WATCHLIST_FILE, 'r', encoding='cp1252') as f2:
                    return json.load(f2)
    return {}

def update_watchlist(stocks):
    watchlist = load_watchlist()
    for stock in stocks:
        watchlist[stock['symbol']] = stock
    with open(WATCHLIST_FILE, 'w', encoding='utf-8') as f:
        json.dump(watchlist, f, indent=4, ensure_ascii=False)
