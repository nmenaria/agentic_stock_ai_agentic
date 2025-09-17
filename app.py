import streamlit as st
from agent import run_agentic_scan
from memory import load_watchlist
from data_fetch import company_name_to_symbol
from yahooquery import Ticker

st.set_page_config(page_title="Agentic Stock AI", layout="wide")
st.title("Agentic Stock AI – Company Name Input & Agentic AI")

# ----------------------
# Input Section
# ----------------------
st.write("Enter company names separated by commas (e.g., Apple, Microsoft, Tesla):")
companies_input = st.text_input("Company Names")
send_email_flag = st.checkbox("Send Email Alerts After Analysis")

# ----------------------
# Run Analysis
# ----------------------
if st.button("Run Analysis"):
    if companies_input:
        company_names = [c.strip() for c in companies_input.split(",")]
    else:
        company_names = None

    top_stocks = run_agentic_scan(company_names, send_email_flag=send_email_flag)

    if not top_stocks:
        st.warning("No stocks passed the screening thresholds.")
    else:
        for stock in top_stocks:
            st.subheader(f"{stock['symbol']} – {stock.get('explanation','')}")
            st.write(f"Price: {stock['price']}")
            st.write(f"ROE: {stock['roe']}")
            st.write(f"PEG: {stock['peg_ratio']}")
            st.write(f"Market Cap: {stock['market_cap']}")
            st.write(f"Recommendation: {stock['explanation']}")
            st.markdown("---")

# ----------------------
# Watchlist Display
# ----------------------
st.subheader("Watchlist")
watchlist = load_watchlist()
if watchlist:
    for symbol, stock in watchlist.items():
        # Fetch latest price dynamically
        ticker = Ticker(symbol)
        price_info = ticker.price.get(symbol, {})
        latest_price = price_info.get('regularMarketPrice', stock.get('price'))

        st.write(f"{symbol} – Price: {latest_price}, ROE={stock.get('roe')}, PEG={stock.get('peg_ratio')}")
else:
    st.write("Watchlist is empty.")

# ----------------------
# Dynamic Company Info Example (Optional)
# ----------------------
st.subheader("Check Latest Company Info")
company_name_check = st.text_input("Enter a company name to fetch latest info:")
if st.button("Get Info") and company_name_check:
    symbol = company_name_to_symbol(company_name_check)
    if symbol:
        ticker = Ticker(symbol)
        info = ticker.quote_type.get(symbol, {})
        price_info = ticker.price.get(symbol, {})
        st.write({
            "Company Name": info.get('longName', company_name_check),
            "Symbol": symbol,
            "Price": price_info.get('regularMarketPrice')
        })
    else:
        st.write(f"Could not find symbol for: {company_name_check}")
