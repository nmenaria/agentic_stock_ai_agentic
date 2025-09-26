# Agentic Stock AI

An intelligent stock screening and watchlist management agent powered by Google Gemini and Yahoo Finance data.

## 🔧 Setup

### 1. Clone and Install Dependencies
```bash
git clone <repository-url>
cd agentic_stock_ai_agentic
pip install -r requirements.txt
```

### 2. Get Google Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/apikey)
2. Create a new API key
3. Copy the API key (starts with `AIzaSy...`)

### 3. Configure Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API key
# .env file will be ignored by git for security
GEMINI_API_KEY=your_actual_api_key_here
```

**Alternative: Set environment variable directly**
```powershell
# Windows PowerShell
$env:GEMINI_API_KEY="your_api_key_here"
```

```bash
# Linux/Mac
export GEMINI_API_KEY="your_api_key_here"
```

### 4. Quick Setup (Recommended)
```bash
python setup.py
```
This will:
- Create `.env` file from template
- Guide you through API key setup
- Run tests to verify everything works

### 5. Manual Setup
If you prefer manual setup:
```bash
python test_setup.py
```

### 6. Test Setup
```bash
python test_setup.py
```

### 7. Run the App
```bash
streamlit run streamlit_app.py
```

## 🚀 Features

### Available Tools
- **Get Symbol**: Find stock ticker from company name
- **Get Fundamentals**: Fetch ROE and PEG ratios
- **Add to Watchlist**: Add stocks to persistent watchlist
- **Show Watchlist**: Display current watchlist
- **Screen and Add**: Automatically screen companies and add if they pass thresholds
- **Set Thresholds**: Update ROE/PEG screening criteria
- **Get Thresholds**: View current screening thresholds

### Example Queries
- "Screen Apple and Tesla and show watchlist"
- "Set thresholds to ROE 20%, PEG 1.5"
- "Find the symbol for Microsoft and add it to watchlist"
- "Show me companies with ROE > 15% and PEG < 2"

## 📁 Files

- `agentic_app.py` - Main agent logic with LangChain integration
- `tools.py` - Stock data fetching and screening tools
- `streamlit_app.py` - Web interface
- `test_setup.py` - Setup verification script
- `watchlist.json` - Persistent watchlist storage
- `thresholds.json` - Screening criteria storage

## 🔍 Troubleshooting

### Common Issues

1. **"DefaultCredentialsError"**
   - Your GEMINI_API_KEY is not set
   - Run: `$env:GEMINI_API_KEY="your_key"`

2. **"Import could not be resolved"**
   - Dependencies not installed
   - Run: `pip install -r requirements.txt`

3. **"Resource quota exceeded"**
   - You've hit Gemini's free tier limits
   - Wait a few minutes or upgrade to paid plan

4. **Yahoo Finance data issues**
   - Some symbols may not have complete fundamental data
   - Try different companies or check symbol spelling

### Debug Steps
1. Run `python test_setup.py` to verify setup
2. Check if API key is set: `echo $env:GEMINI_API_KEY`
3. Try running individual tools from `tools.py`
4. Check the Streamlit logs for detailed error messages

## 🎯 Usage Tips

- Start with well-known companies (Apple, Microsoft, Google)
- Set realistic thresholds (ROE > 10%, PEG < 3)
- Use specific company names, not generic terms
- The agent can handle multiple requests in one query
- Watchlist and thresholds persist between sessions

## 📊 Default Settings

- **ROE Threshold**: 15% (companies must have Return on Equity > 15%)
- **PEG Threshold**: 2.0 (companies must have PEG ratio < 2.0)
- **Model**: gemini-1.5-flash (free tier)
- **Temperature**: 0.3 (balanced creativity/accuracy)