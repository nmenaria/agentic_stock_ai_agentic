import google.generativeai as genai
import config

genai.configure(api_key=config.GEMINI_API_KEY)

def explain_stock_with_gemini(stock_data):
    prompt = f"""
    You are a financial analyst AI. Based on the following data for {stock_data['symbol']}:
    - Market Cap: {stock_data['market_cap']}
    - ROE: {stock_data['roe']}
    - PEG Ratio: {stock_data['peg_ratio']}
    - Price: {stock_data['price']}
    Provide a concise investment recommendation.
    """
    response = genai.generate_text(model="gemini-2.5-flash", prompt=prompt)
    return response.result
