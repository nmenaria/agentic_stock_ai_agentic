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
        symbols = ['AAPL','MSFT','TSLA','GOOGL','AMZN']

    all_stocks_data = []
    for symbol in symbols:
        data = get_stock_data(symbol)
        passed = screen_stock(data, config.THRESHOLDS)
        if passed:
            all_stocks_data.append(data)
        else:
            st.write(f"{symbol} did not pass screening: ROE={data.get('roe')}, PEG={data.get('peg_ratio')}")

    top_stocks = rank_stocks(all_stocks_data, config.TOP_N)

    # Generate Gemini explanations
    for stock in top_stocks:
        stock['explanation'] = explain_stock_with_gemini(stock)

    # Update watchlist
    update_watchlist(top_stocks)

    # Send email alerts if enabled
    if send_email_flag and top_stocks:
        send_email(top_stocks)

    return top_stocks
