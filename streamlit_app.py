# streamlit_app.py
import streamlit as st
import os
from tools import show_watchlist, get_thresholds, set_thresholds

# Check for API key before importing agent
if not os.environ.get("GEMINI_API_KEY") and not st.secrets.get("GEMINI_API_KEY", None):
    st.error("⚠️ GEMINI_API_KEY not found!")
    st.info("Please set your Gemini API key in one of these ways:")
    st.code("1. Environment variable: set GEMINI_API_KEY=your_key")
    st.code("2. Streamlit secrets: Add GEMINI_API_KEY to .streamlit/secrets.toml")
    st.stop()

try:
    from agentic_app import agent
except Exception as e:
    st.error(f"Error loading agent: {e}")
    st.stop()

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
    "Example queries:",
    "Screen Tesla and Apple automatically with detailed analysis and then show watchlist.",
    help="""Try these example queries:
    • 'Analyze Microsoft in detail' (comprehensive analysis without screening)
    • 'Screen Apple Inc with full details' (screening with threshold analysis)
    • 'Get detailed info for TSLA' (direct stock information lookup)
    • 'Screen Amazon and Google, then show watchlist'
    """
)

if st.button("Run Agent"):
    with st.spinner("Running agent..."):
        try:
            result = agent.run(user_query)
            st.success("✅ Agent completed successfully!")
            st.write(result)
        except Exception as e:
            st.error(f"❌ Agent error: {e}")
            st.write("Please check your API key and try again.")

st.subheader("Current Persistent Watchlist")
st.write(show_watchlist())
