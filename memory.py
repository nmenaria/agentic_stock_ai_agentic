import json
import os

WATCHLIST_FILE = 'watchlist.json'

def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, 'r') as f:
            return json.load(f)
    return {}

def update_watchlist(stocks):
    watchlist = load_watchlist()
    for stock in stocks:
        watchlist[stock['symbol']] = stock
    with open(WATCHLIST_FILE, 'w') as f:
        json.dump(watchlist, f, indent=4)
