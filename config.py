import streamlit as st

# Streamlit secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
FROM_EMAIL = st.secrets["FROM_EMAIL"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
TO_EMAIL = st.secrets["TO_EMAIL"]

# Screening thresholds
THRESHOLDS = {
    'roe': 0.15,
    'peg': 2.0
}

# Agent settings
TOP_N = 5         # Number of top stocks to consider
SCAN_INTERVAL = 60  # minutes
