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
    echo Using Python 3.10.x: !PYTHON_CMD!
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
