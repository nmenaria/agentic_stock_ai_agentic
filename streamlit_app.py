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

st.subheader("🤖 Stock Analysis")

# Add tabs for different analysis modes
tab1, tab2 = st.tabs(["🎯 Direct Analysis (Reliable)", "🤖 AI Agent (Experimental)"])

with tab1:
    st.info("💡 This mode uses direct tools to ensure you always get real Yahoo Finance data")
    
    user_query_direct = st.text_area(
        "Enter your query:",
        "Analyze Infosys with detailed information",
        help="""Try these queries:
        • 'Analyze Microsoft' - Comprehensive analysis
        • 'Screen Apple' - Analysis with threshold check  
        • 'Show watchlist' - View watchlist with details
        • 'Set thresholds ROE 20 PEG 1.5' - Update criteria
        """,
        key="direct_query"
    )

    if st.button("🚀 Run Direct Analysis", key="run_direct"):
        with st.spinner("Getting real stock data..."):
            try:
                from direct_stock_analyzer import smart_stock_query
                result = smart_stock_query(user_query_direct)
                st.success("✅ Analysis completed!")
                st.markdown(f"```\n{result}\n```")
            except Exception as e:
                st.error(f"❌ Error: {e}")

with tab2:
    st.warning("⚠️ The AI agent sometimes generates fictional data instead of using real tools. Use 'Direct Analysis' for reliable results.")
    
    user_query_agent = st.text_area(
        "Ask the Agent:",
        "Screen Tesla and Apple automatically with detailed analysis and then show watchlist.",
        help="""Try these example queries:
        • 'Analyze Microsoft in detail' (comprehensive analysis without screening)
        • 'Screen Apple Inc with full details' (screening with threshold analysis)
        • 'Get detailed info for TSLA' (direct stock information lookup)
        • 'Screen Amazon and Google, then show watchlist'
        """,
        key="agent_query"
    )

    if st.button("🤖 Run Agent", key="run_agent"):
        with st.spinner("Running agent..."):
            try:
                result = agent.run(user_query_agent)
                st.success("✅ Agent completed successfully!")
                st.write(result)
            except Exception as e:
                st.error(f"❌ Agent error: {e}")
                st.write("Please check your API key and try again.")
                st.info("💡 Try using the 'Direct Analysis' tab for more reliable results.")

st.subheader("📊 Current Persistent Watchlist")
watchlist = show_watchlist()

if not watchlist:
    st.info("📋 Watchlist is empty. Use the agent to screen and add stocks!")
else:
    st.success(f"📈 {len(watchlist)} stocks in watchlist")
    
    # Import get_detailed_stock_info here to avoid circular imports
    from tools import get_detailed_stock_info
    
    # Display each stock with detailed information
    for i, symbol in enumerate(watchlist):
        with st.expander(f"📊 {symbol} - Click to view details", expanded=False):
            with st.spinner(f"Loading details for {symbol}..."):
                try:
                    details = get_detailed_stock_info(symbol)
                    if 'error' in details:
                        st.error(f"❌ Error loading {symbol}: {details['error']}")
                    else:
                        # Display the formatted information
                        st.markdown(details['formatted_info'])
                        
                        # Add remove button for each stock
                        if st.button(f"🗑️ Remove {symbol} from watchlist", key=f"remove_{symbol}_{i}"):
                            # We'll need to add a remove function
                            from tools import remove_from_watchlist
                            result = remove_from_watchlist(symbol)
                            st.success(result)
                            st.rerun()  # Refresh the page
                            
                except Exception as e:
                    st.error(f"❌ Failed to load details for {symbol}: {e}")
    
    # Add bulk actions
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh All Details"):
            st.rerun()
    with col2:
        if st.button("🗑️ Clear Entire Watchlist"):
            from tools import clear_watchlist
            result = clear_watchlist()
            st.success(result)
            st.rerun()
