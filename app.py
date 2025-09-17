import streamlit as st
from agent import run_agentic_scan
from memory import load_watchlist

st.set_page_config(page_title="Agentic Stock AI", layout="wide")
st.title("Agentic Stock AI – Company Name Input & Agentic AI")

st.write("Enter company names separated by commas (e.g., Apple, Microsoft, Tesla):")
companies_input = st.text_input("Company Names")
send_email_flag = st.checkbox("Send Email Alerts After Analysis")

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
            st.subheader(f"{stock['symbol']}")
            st.write(f"Price: {stock['price']}")
            st.write(f"ROE: {stock['roe']}")
            st.write(f"PEG: {stock['peg_ratio']}")
            st.write(f"Market Cap: {stock['market_cap']}")
            st.write(f"Recommendation: {stock['explanation']}")
            st.markdown("---")

st.subheader("Watchlist")
watchlist = load_watchlist()
for symbol, stock in watchlist.items():
    st.write(f"{symbol}: {stock['price']}, ROE={stock['roe']}, PEG={stock['peg_ratio']}")
