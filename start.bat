@echo off
REM Star Resonance Market Analyzer - Windows Startup Script

echo ========================================
echo Star Resonance Market Analyzer
echo ========================================
echo.

REM Find best Python version
setlocal enabledelayedexpansion
call find-python.bat
set PYTHON_CHECK=%errorlevel%

if "!PYTHON_CMD!"=="" (
    echo ========================================
    echo ERROR: No Python installation found!
    echo ========================================
    echo.
    echo Please install Python 3.10.11 from:
    echo https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
    echo.
    pause
    exit /b 1
)

if !PYTHON_CHECK! equ 0 (
    echo ✓ Using Python 3.10.x: !PYTHON_CMD!
) else (
    echo ========================================
    echo WARNING: Python 3.10 not found!
    echo ========================================
    echo.
    echo Current Python: !PYTHON_CMD!
    !PYTHON_CMD! --version
    echo.
    echo Python 3.10 is STRONGLY RECOMMENDED for best compatibility.
    echo Some packages may fail to install with other versions.
    echo.
    echo Download Python 3.10.11:
    echo https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
    echo.
    echo Continue anyway? (Y/N)
    set /p choice=Choice: 
    if /i not "!choice!"=="Y" exit /b 1
)

echo.
!PYTHON_CMD! --version
echo.

REM Check for virtual environment
if not exist venv (
    echo Virtual environment not found. Creating with !PYTHON_CMD!...
    !PYTHON_CMD! -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Checking dependencies...
echo Installing packages (this may take a moment)...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo Error installing dependencies. Trying alternative installation...
    pip install fastapi uvicorn[standard] pydantic pydantic-settings sqlalchemy alembic aiosqlite scapy pandas numpy python-multipart python-jose[cryptography] passlib[bcrypt] python-json-logger prometheus-client pytest pytest-asyncio httpx black flake8 mypy jinja2 aiofiles python-dotenv schedule websockets
)
echo.

REM Check for database
if not exist bpsr_market.db (
    echo Database not found. Starting setup...
    python -m src.database.setup
    echo.
    
    echo Would you like to import sample data? (Y/N^)
    set /p choice=Choice: 
    if /i "%choice%"=="Y" (
        python scripts/import_sample_data.py
        echo.
    )
)

REM Start API server
echo Starting API server...
echo Open your browser and navigate to http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python -m src.api.main

pause
