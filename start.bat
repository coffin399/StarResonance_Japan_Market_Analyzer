@echo off
REM Star Resonance Market Analyzer - Windows Startup Script

echo ========================================
echo Star Resonance Market Analyzer
echo ========================================
echo.

REM Check for virtual environment
if not exist venv (
    echo Virtual environment not found. Starting setup...
    python -m venv venv
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
