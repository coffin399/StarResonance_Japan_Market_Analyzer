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
    echo Using Python 3.10.x: !PYTHON_CMD!
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

REM Check dependencies
echo Checking dependencies...
python -c "import fastapi" 2>nul
if %errorlevel% neq 0 (
    echo Dependencies not installed. Please run quick-install.bat first.
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
