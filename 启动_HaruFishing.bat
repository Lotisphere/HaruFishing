@echo off
title HaruFishing Start Wizard
color 0D

echo ===================================================
echo       Welcome to HaruFishing Auto Starter!
echo ===================================================
echo.

echo [0/4] API Key Configuration...
choice /C YN /M "Do you want to configure your Gemini API Key now? (Y/N)"
if errorlevel 2 goto skip_api_key
if errorlevel 1 goto set_api_key

:set_api_key
set /p USER_API_KEY="Please paste your Gemini API Key here and press Enter: "
echo GEMINI_API_KEY=%USER_API_KEY%> .env
echo [OK] API Key saved to .env file!
echo.
goto check_python

:skip_api_key
echo [INFO] Skipped. Please enter your API Key in the Web UI later.
echo.

:check_python
echo [1/4] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    choice /C YN /M "Do you want to open Python download page?"
    if errorlevel 2 goto exit_script
    if errorlevel 1 (
        echo Opening download page...
        echo Please make sure to check "Add Python to PATH" during installation!
        start https://www.python.org/downloads/
        pause
        exit /b
    )
)
echo [OK] Python is installed.
echo.

choice /C YN /M "Do you want to check and install missing dependencies? (Press Y for first run)"
if errorlevel 2 goto run_app
echo.

echo [2/4] Checking UI and Graphing tools (Streamlit, Pyvis)...
python -c "import streamlit, pyvis" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing UI and Graphing tools...
    python -m pip install streamlit pyvis
    echo [OK] Tools installed!
) else (
    echo [OK] Streamlit and Pyvis are already installed.
)
echo.

echo [3/4] Checking AI and Document dependencies...
python -c "import google.generativeai, pydantic, tenacity, dotenv, pypdf, docx" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing required packages...
    python -m pip install google-generativeai pydantic tenacity python-dotenv pypdf python-docx
    echo [OK] Dependencies installed!
) else (
    echo [OK] Dependencies are already installed.
)
echo.

:run_app
echo [4/4] Starting the engine...
echo ===================================================
echo       Launching HaruFishing Web UI...
echo ===================================================
echo Notes:
echo 1. Your browser will open automatically.
echo 2. If not, copy the "Local URL" into your browser.
echo 3. Close this window to stop the application.
echo.

python -m streamlit run ui/web_app.py

:exit_script
pause