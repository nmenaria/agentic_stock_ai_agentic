@echo off
echo Setting up Agentic Stock AI environment...
echo.
echo Please enter your Gemini API key:
set /p GEMINI_API_KEY=API Key: 
echo.
echo Setting environment variable...
set GEMINI_API_KEY=%GEMINI_API_KEY%
echo.
echo Testing setup...
.\.venv\Scripts\python.exe test_setup.py
echo.
echo If tests pass, you can now run:
echo   streamlit run streamlit_app.py
echo.
pause