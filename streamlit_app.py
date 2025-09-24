# streamlit_app.py
import streamlit as st
from agentic_app import agent
from tools import show_watchlist, get_thresholds, set_thresholds

st.title("Agentic Stock Watchlist App (Gemini)")

st.subheader("Screening Thresholds")
thr = get_thresholds()
roe_input = st.number_input("ROE Threshold (%)", value=thr["roe"])
peg_input = st.number_input("PEG Threshold", value=thr["peg"])
if st.button("Update Thresholds"):
    set_thresholds(roe_input, peg_input)
    st.success("Thresholds updated!")

st.subheader("Ask the Agent")
user_query = st.text_area(
    "Example: 'Screen Tesla and Apple automatically and then show watchlist.'",
    "Screen Tesla and Apple automatically and then show watchlist."
)

if st.button("Run Agent"):
    result = agent.run(user_query)
    st.write(result)

st.subheader("Current Persistent Watchlist")
st.write(show_watchlist())
