@echo off
REM Minimal installation - Python 3.10 REQUIRED

echo ========================================
echo Star Resonance Market Analyzer
echo Minimal Installation
echo ========================================
echo.

REM Test Python 3.10 directly
py -3.10 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python 3.10 not found!
    echo.
    echo Download: https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
    pause
    exit /b 1
)

echo Using Python 3.10
py -3.10 --version
echo.

REM Create venv
if not exist venv (
    echo Creating virtual environment...
    py -3.10 -m venv venv
)

call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing core packages only...
pip install sqlalchemy fastapi uvicorn[standard] pydantic alembic aiosqlite jinja2 python-dotenv websockets

if %errorlevel% neq 0 (
    echo Installation failed
    pause
    exit /b 1
)

echo.
echo Setting up database...
python -m src.database.setup

echo.
echo ========================================
echo Minimal Installation Complete!
echo ========================================
echo.
echo To start the server:
echo   start.bat
echo.
pause
