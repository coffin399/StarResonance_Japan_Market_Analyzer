@echo off
REM Star Resonance Market Analyzer - Windows Startup Script

echo ========================================
echo Star Resonance Market Analyzer
echo ========================================
echo.

REM Test Python 3.10 directly
py -3.10 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python 3.10 not found!
    echo.
    echo Please install Python 3.10.11:
    echo https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
    echo.
    pause
    exit /b 1
)

echo Using Python 3.10
py -3.10 --version
echo.

REM Check for virtual environment
if not exist venv (
    echo Virtual environment not found!
    echo Please run quick-install.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check dependencies
echo Checking dependencies...
python -c "import fastapi" 2>nul
if %errorlevel% neq 0 (
    echo Dependencies not installed!
    echo Please run quick-install.bat first.
    pause
    exit /b 1
)

REM Start the API server
echo Starting API server...
echo.
echo Server will be available at:
echo   http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.
python -m src.api.main
