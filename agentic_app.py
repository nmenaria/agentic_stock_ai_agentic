# agentic_app.py
import time
import streamlit as st
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core.exceptions import ResourceExhausted

# import your tools (safe version)
import tools  # this is your tools.py

# --- Settings ---
MAX_ITERATIONS = 5       # fewer steps reduces Gemini calls
AGENT_TIMEOUT = 120      # seconds
MODEL_NAME = "gemini-1.5-flash"  # free tier model
TEMPERATURE = 0.3

# --- Gemini wrapper with retry/backoff ---
class SafeGeminiLLM:
    def __init__(self, model_name=MODEL_NAME, temperature=TEMPERATURE, max_retries=3, backoff=30):
        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        self.max_retries = max_retries
        self.backoff = backoff

    def __call__(self, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return self.llm(*args, **kwargs)
            except ResourceExhausted as e:
                wait = getattr(e, "retry_delay", None)
                if wait and hasattr(wait, "seconds"):
                    wait_time = wait.seconds
                else:
                    wait_time = self.backoff
                st.warning(f"Gemini quota exceeded. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
        raise RuntimeError("Gemini API quota exceeded repeatedly; try again later.")

# instantiate safe LLM
safe_llm = SafeGeminiLLM()

# --- Define Tools ---
tools_list = [
    Tool(
        name="Add to Watchlist",
        func=tools.add_to_watchlist,
        description="Add a stock symbol to the watchlist."
    ),
    Tool(
        name="Show Watchlist",
        func=lambda _: tools.show_watchlist(),
        description="Show the current watchlist."
    ),
    Tool(
        name="Set Thresholds",
        func=lambda s: tools.set_thresholds(*map(float, s.split())),
        description="Update thresholds. Input: 'ROE PEG'"
    ),
    Tool(
        name="Screen Company",
        func=tools.screen_and_add,
        description="Screen a company name against thresholds and add if passes."
    ),
]

# --- Create Agent ---
agent = initialize_agent(
    tools_list,
    safe_llm,  # safe LLM
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
        result = agent.run(user_query)
        elapsed = time.time() - start
        st.success(f"✅ Agent finished in {elapsed:.1f}s")
        st.write(result)
    except Exception as e:
        st.error(f"Agent error: {e}")
