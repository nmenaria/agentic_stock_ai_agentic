from data_fetch import get_stock_data, company_name_to_symbol
from analysis import screen_stock, rank_stocks
from planner import explain_stock_with_gemini
from memory import update_watchlist
from alerts import send_email
import config
import streamlit as st

def run_agentic_scan(company_names=None, send_email_flag=False):
    symbols = []

    # Convert company names to symbols
    if company_names:
        for name in company_names:
            symbol = company_name_to_symbol(name)
            if symbol:
                symbols.append(symbol)
            else:
                st.warning(f"Could not find symbol for: {name}")
    else:
        # Default companies if none provided
        symbols = ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN']

    all_stocks_data = []
    for symbol in symbols:
        data = get_stock_data(symbol)
        if screen_stock(data, config.THRESHOLDS):
            all_stocks_data.append(data)

    top_stocks = rank_stocks(all_stocks_data, config.TOP_N)

    for stock in top_stocks:
        stock['explanation'] = explain_stock_with_gemini(stock)

    update_watchlist(top_stocks)

    if send_email_flag and top_stocks:
        send_email(top_stocks, config.TO_EMAIL, config.FROM_EMAIL, config.EMAIL_PASSWORD)

    return top_stocks
