@echo off
chcp 65001 >nul
echo ========================================
echo   BaoStock Data Browser Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://www.python.org/
    pause
    exit /b 1
)

echo [INFO] Python detected
echo.

REM Check if required packages are installed
echo [INFO] Checking dependencies...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo [WARN] Dependencies not found. Installing...
    echo [INFO] Upgrading pip first...
    python -m pip install --upgrade pip
    echo.
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install dependencies with requirements.txt
        echo [INFO] Trying alternative installation method...
        pip install streamlit baostock pandas
        if errorlevel 1 (
            echo [ERROR] Installation failed. Please try manually:
            echo   pip install --upgrade pip
            echo   pip install streamlit baostock pandas
            pause
            exit /b 1
        )
    )
    echo [SUCCESS] Dependencies installed successfully
) else (
    echo [SUCCESS] Dependencies already installed
)
echo.

REM Run the Streamlit app
echo [INFO] Starting BaoStock Data Browser...
echo [INFO] The browser will open automatically at http://localhost:8501
echo [INFO] Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

streamlit run baostock_browser.py

REM If streamlit command fails
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to start the application
    echo Please check if all dependencies are installed correctly
    pause
    exit /b 1
)
