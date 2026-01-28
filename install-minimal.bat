@echo off
REM Minimal installation without problematic packages
REM Use this if quick-install.bat fails

echo ========================================
echo Star Resonance Market Analyzer
echo Minimal Installation
echo ========================================
echo.

REM Find best Python version
setlocal enabledelayedexpansion
call find-python.bat
set PYTHON_CHECK=%errorlevel%

if "!PYTHON_CMD!"=="" (
    echo ERROR: No Python installation found
    echo.
    echo Please install Python 3.10.11:
    echo https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
    pause
    exit /b 1
)

if !PYTHON_CHECK! equ 0 (
    echo ========================================
    echo ✓ Using Python 3.10.x: !PYTHON_CMD!
    echo ========================================
    !PYTHON_CMD! --version
    echo.
) else (
    echo ========================================
    echo WARNING: Python 3.10 not found
    echo ========================================
    echo Using: !PYTHON_CMD!
    !PYTHON_CMD! --version
    echo.
    
    echo Checking Python version compatibility...
    !PYTHON_CMD! -c "import sys; exit(0 if sys.version_info < (3, 14) else 1)"
    if !errorlevel! neq 0 (
        echo.
        echo WARNING: Python 3.14+ detected
        echo Some packages may not work correctly
        echo Recommended: Python 3.10 or 3.11
        echo.
        echo Continue anyway? (Y/N)
        set /p choice=Choice: 
        if /i not "!choice!"=="Y" exit /b 1
    )
    echo.
)

REM Create venv
if not exist venv (
    echo Creating virtual environment with !PYTHON_CMD!...
    !PYTHON_CMD! -m venv venv
)

call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install packages one by one with error handling
echo.
echo Installing packages (this may take a while)...
echo.

echo [1/10] SQLAlchemy...
pip install sqlalchemy
if %errorlevel% neq 0 goto error

echo [2/10] FastAPI...
pip install fastapi
if %errorlevel% neq 0 goto error

echo [3/10] Uvicorn...
pip install uvicorn
if %errorlevel% neq 0 goto error

echo [4/10] Pydantic (may show warnings, this is normal)...
pip install "pydantic>=2.0" --prefer-binary
if %errorlevel% neq 0 (
    echo Trying older version...
    pip install "pydantic<2.0"
    if %errorlevel% neq 0 goto error
)

echo [5/10] Pydantic Settings...
pip install pydantic-settings
if %errorlevel% neq 0 goto error

echo [6/10] Alembic...
pip install alembic
if %errorlevel% neq 0 goto error

echo [7/10] Aiosqlite...
pip install aiosqlite
if %errorlevel% neq 0 goto error

echo [8/10] Jinja2...
pip install jinja2
if %errorlevel% neq 0 goto error

echo [9/10] Python-dotenv...
pip install python-dotenv
if %errorlevel% neq 0 goto error

echo [10/10] Websockets...
pip install websockets
if %errorlevel% neq 0 goto error

echo.
echo ========================================
echo Core packages installed successfully!
echo ========================================
echo.

REM Setup database
echo Setting up database...
python -m src.database.setup
if %errorlevel% neq 0 (
    echo Database setup failed
    echo This might be due to missing packages
    echo Try running: python -m src.database.setup
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Optional: Import sample data?
set /p choice=Import sample data? (Y/N): 
if /i "%choice%"=="Y" (
    python scripts/import_sample_data.py
)

echo.
echo To start the server:
echo   venv\Scripts\activate
echo   python -m src.api.main
echo.
echo Or simply run:
echo   start.bat
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo Installation failed at package: %errorlevel%
echo ========================================
echo.
echo Troubleshooting:
echo 1. Check your Python version: python --version
echo 2. Recommended: Python 3.10 or 3.11
echo 3. Try downloading Python from: https://www.python.org/downloads/
echo.
echo Alternative: Use Docker
echo   docker-compose up -d
echo.
pause
exit /b 1
