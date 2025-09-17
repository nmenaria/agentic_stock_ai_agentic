import streamlit as st

# Secrets (Streamlit Cloud)
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
FROM_EMAIL = st.secrets.get("FROM_EMAIL", "")
EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD", "")
TO_EMAIL = st.secrets.get("TO_EMAIL", "")

# Screening thresholds
THRESHOLDS = {'roe': 0.15, 'peg': 2.0}

# Agent settings
TOP_N = 5
SCAN_INTERVAL = 60  # in minutes
