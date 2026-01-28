@echo off
REM Quick installation script with error handling

echo ========================================
echo Star Resonance Market Analyzer
echo Quick Installation
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo Python found!
echo.

REM Create virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo.

REM Install core dependencies first
echo Installing core dependencies...
pip install --no-cache-dir sqlalchemy==2.0.25 fastapi==0.109.0 uvicorn[standard]==0.27.0 pydantic==2.5.3
if %errorlevel% neq 0 (
    echo Failed to install core dependencies
    pause
    exit /b 1
)
echo Core dependencies installed!
echo.

REM Install remaining dependencies
echo Installing remaining dependencies...
pip install --no-cache-dir pydantic-settings==2.1.0 alembic==1.13.1 aiosqlite==0.19.0
pip install --no-cache-dir pandas==2.1.4 numpy==1.26.3 python-multipart==0.0.6
pip install --no-cache-dir jinja2==3.1.3 aiofiles==23.2.1 python-dotenv==1.0.0
pip install --no-cache-dir websockets==12.0

echo.
echo Optional: Installing packet analysis tools...
echo (Press Ctrl+C to skip if you don't need packet capture)
timeout /t 5
pip install --no-cache-dir scapy==2.5.0
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
