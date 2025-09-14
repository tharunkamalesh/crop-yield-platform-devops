@echo off
echo 🌾 AI Crop Yield Prediction & Advisory Platform
echo ================================================
echo.

echo 🚀 Starting application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo 💡 Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    echo 💡 Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)

echo ✅ Dependencies check passed
echo.

REM Start the Python launcher
echo 🚀 Launching services...
python start_app.py

if errorlevel 1 (
    echo.
    echo ❌ Failed to start application
    pause
    exit /b 1
)

pause
