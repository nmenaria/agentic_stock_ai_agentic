import os
from langchain.agents import initialize_agent, Tool
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import (
    get_symbol,
    get_fundamentals,
    add_to_watchlist,
    show_watchlist,
    screen_and_add,
    get_thresholds,
    set_thresholds
)

# Gemini API key (set in Streamlit secrets or environment variable)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",  # adjust if needed
    google_api_key=GEMINI_API_KEY,
    temperature=0
)

# ----- safe function to replace lambda -----
def safe_set_thresholds(user_input: str):
    try:
        roe_str, peg_str = user_input.split(",")
        roe = float(roe_str.strip())
        peg = float(peg_str.strip())
        return set_thresholds(roe, peg)
    except Exception as e:
        return f"Error setting thresholds: {e}"

# ----- tools -----
tools = [
    Tool(name="Get Symbol", func=get_symbol,
         description="Find a stock ticker symbol from a company name."),
    Tool(name="Get Fundamentals", func=get_fundamentals,
         description="Fetch ROE and PEG for a given stock ticker symbol."),
    Tool(name="Add To Watchlist", func=add_to_watchlist,
         description="Add a stock symbol to the persistent watchlist."),
    Tool(name="Show Watchlist", func=show_watchlist,
         description="Show the current persistent watchlist."),
    Tool(name="Screen And Add", func=screen_and_add,
         description="Automatically screen a company by saved thresholds and add to watchlist if it passes."),
    Tool(name="Get Thresholds", func=get_thresholds,
         description="Show the current screening thresholds (ROE and PEG)."),
    Tool(name="Set Thresholds", func=safe_set_thresholds,
         description="Update screening thresholds. Input format: 'ROE,PEG' (e.g. '20,1.5').")
]

agent = initialize_agent(
    tools,
    llm,
    agent="zero-shot-react-description",
    verbose=True
)

if __name__ == "__main__":
    question = "Screen Tesla and Apple and show watchlist."
    print(agent.run(question))
