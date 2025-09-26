# agentic_app.py
import os
import time
import json
import requests
import streamlit as st
from pathlib import Path
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.llms.base import LLM
from google.api_core.exceptions import ResourceExhausted
from typing import Optional, List, Any

# Load environment variables from .env file if it exists
def load_env_file():
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value

load_env_file()

# import your tools (safe version)
import tools  # this is your tools.py

# --- Settings ---
MAX_ITERATIONS = 5       # fewer steps reduces Gemini calls
AGENT_TIMEOUT = 120      # seconds
MODEL_NAME = "models/gemini-2.0-flash"  # working model name
TEMPERATURE = 0.3

# --- Custom Gemini LLM using REST API directly ---
class GeminiLLM(LLM):
    """Custom LLM wrapper that uses Google AI REST API directly"""
    
    model_name: str = "models/gemini-2.0-flash"
    temperature: float = 0.3
    api_key: str = ""
    
    def __init__(self, model_name="models/gemini-2.0-flash", temperature=0.3, api_key=None, **kwargs):
        # Get API key
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key and hasattr(st, 'secrets'):
                api_key = st.secrets.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found")
        
        # Initialize parent with field values
        super().__init__(model_name=model_name, temperature=temperature, api_key=api_key, **kwargs)
    
    @property
    def _llm_type(self) -> str:
        return "gemini"
    
    def _call(
        self, 
        prompt: str, 
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any
    ) -> str:
        """Generate a response using Google AI REST API"""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/{self.model_name}:generateContent"
            
            headers = {"Content-Type": "application/json"}
            
            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": self.temperature,
                    "maxOutputTokens": 2048,
                }
            }
            
            response = requests.post(
                url, 
                headers=headers, 
                params={"key": self.api_key},
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and result['candidates']:
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    return "No response generated"
            else:
                return f"Error {response.status_code}: {response.text}"
                
        except Exception as e:
            return f"Error: {e}"

def create_safe_llm(model_name=MODEL_NAME, temperature=TEMPERATURE):
    """Create a Gemini LLM with proper API key handling"""
    return GeminiLLM(model_name=model_name, temperature=temperature)

# Create the LLM instance
llm = create_safe_llm()

# --- Define Tools ---
def safe_set_thresholds(input_str: str):
    """Safely parse and set thresholds from input string"""
    try:
        # Handle both comma and space separated values
        if ',' in input_str:
            roe_str, peg_str = input_str.split(',', 1)
        else:
            roe_str, peg_str = input_str.split(None, 1)
        roe = float(roe_str.strip())
        peg = float(peg_str.strip())
        return tools.set_thresholds(roe, peg)
    except Exception as e:
        return f"Error setting thresholds: {e}. Use format 'ROE,PEG' or 'ROE PEG'"

tools_list = [
    Tool(
        name="Get Symbol",
        func=tools.get_symbol,
        description="Find a stock ticker symbol from a company name."
    ),
    Tool(
        name="Get Fundamentals", 
        func=tools.get_fundamentals,
        description="Fetch basic ROE and PEG for a given stock ticker symbol."
    ),
    Tool(
        name="Get Detailed Stock Info",
        func=tools.get_detailed_stock_info,
        description="Get comprehensive stock information including fundamentals, price, company details, and financial metrics."
    ),
    Tool(
        name="Analyze Stock",
        func=tools.analyze_stock,
        description="Provide comprehensive stock analysis for a company without threshold screening."
    ),
    Tool(
        name="Add to Watchlist",
        func=tools.add_to_watchlist,
        description="Add a stock symbol to the watchlist."
    ),
    Tool(
        name="Remove from Watchlist",
        func=tools.remove_from_watchlist,
        description="Remove a stock symbol from the watchlist."
    ),
    Tool(
        name="Clear Watchlist",
        func=lambda _: tools.clear_watchlist(),
        description="Clear all stocks from the watchlist."
    ),
    Tool(
        name="Show Watchlist",
        func=lambda _: tools.show_watchlist(),
        description="Show the current watchlist."
    ),
    Tool(
        name="Get Thresholds",
        func=lambda _: tools.get_thresholds(),
        description="Show the current screening thresholds (ROE and PEG)."
    ),
    Tool(
        name="Set Thresholds",
        func=safe_set_thresholds,
        description="Update thresholds. Input format: 'ROE,PEG' (e.g. '20,1.5') or 'ROE PEG'"
    ),
    Tool(
        name="Screen and Add",
        func=tools.screen_and_add,
        description="Screen a company against thresholds with detailed analysis and add to watchlist if it passes criteria. Always provides comprehensive stock information."
    ),
]

# --- Create Agent ---
agent = initialize_agent(
    tools_list,
    llm,  # use the ChatGoogleGenerativeAI instance directly
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    max_iterations=MAX_ITERATIONS,
    handle_parsing_errors=True,
)

# --- Streamlit UI ---
st.title("Agentic Stock AI")

user_query = st.text_input("Ask the agent (e.g. 'screen Apple Inc.'):")

if user_query:
    try:
        # run the agent with timeout
        start = time.time()
        with st.spinner("Running agent..."):
            result = agent.run(user_query)
        elapsed = time.time() - start
        st.success(f"✅ Agent finished in {elapsed:.1f}s")
        st.write(result)
    except ResourceExhausted as e:
        st.error("❌ Gemini API quota exceeded. Please wait a few minutes and try again.")
        st.info("💡 Tip: The free tier has rate limits. Consider using shorter queries or upgrading to a paid plan.")
    except Exception as e:
        st.error(f"❌ Agent error: {e}")
        st.info("💡 Try rephrasing your query or check if the company name is correct.")
