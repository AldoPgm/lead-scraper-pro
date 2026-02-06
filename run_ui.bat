@echo off
echo ==========================================
echo      LEAD SCRAPER - DIAGNOSTIC LAUNCHER
echo ==========================================

echo [1/4] Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python command not found!
    echo Please install Python from python.org and check "Add to PATH".
    pause
    exit /b
)

echo.
echo [2/4] Checking/Installing Pip...
python -m ensurepip --default-pip
python -m pip install --upgrade pip

echo.
echo [3/4] Installing dependencies...
python -m pip install streamlit pandas duckduckgo-search

echo.
echo [4/4] Launching Application...
echo The browser should open automatically...
python -m streamlit run app.py

echo.
echo ==========================================
echo If the app closed, read the errors above.
echo ==========================================
pause
