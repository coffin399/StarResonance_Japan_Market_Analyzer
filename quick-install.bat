@echo off
REM Quick installation script - Python 3.10 REQUIRED

echo ========================================
echo Star Resonance Market Analyzer
echo Quick Installation
echo ========================================
echo.

REM Test Python 3.10 directly
py -3.10 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ========================================
    echo ERROR: Python 3.10 not found!
    echo ========================================
    echo.
    echo This tool requires Python 3.10.x
    echo.
    echo Download Python 3.10.11:
    echo https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
    echo.
    echo After installation, make sure to check:
    echo [X] Add Python 3.10 to PATH
    echo.
    pause
    exit /b 1
)

echo Python 3.10.x detected!
py -3.10 --version
echo.

REM Create virtual environment
if not exist venv (
    echo Creating virtual environment...
    py -3.10 -m venv venv
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo.

REM Install dependencies
echo Installing dependencies...
echo.
pip install -r requirements-dev.txt
if %errorlevel% neq 0 (
    echo.
    echo Failed to install dependencies
    echo.
    pause
    exit /b 1
)
echo Dependencies installed!
echo.

REM Setup database
echo Setting up database...
python -m src.database.setup
if %errorlevel% neq 0 (
    echo Failed to setup database
    pause
    exit /b 1
)
echo.

REM Import sample data
echo Would you like to import sample data? (Y/N)
set /p choice=Choice: 
if /i "%choice%"=="Y" (
    python scripts/import_sample_data.py
    echo.
)

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To start the server, run:
echo   start.bat
echo.
echo Or manually:
echo   venv\Scripts\activate
echo   python -m src.api.main
echo.
pause
