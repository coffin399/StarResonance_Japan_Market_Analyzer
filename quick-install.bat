@echo off
REM Quick installation script with error handling

echo ========================================
echo Star Resonance Market Analyzer
echo Quick Installation
echo ========================================
echo.

REM Find best Python version (3.10 REQUIRED)
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
    echo Direct download (Windows 64-bit, recommended)
    pause
    exit /b 1
)

if !PYTHON_CHECK! equ 0 (
    echo ========================================
    echo ✓ Python 3.10.x detected! (PERFECT)
    echo ========================================
    !PYTHON_CMD! --version
    echo.
) else (
    echo ========================================
    echo WARNING: Python 3.10 not found!
    echo ========================================
    echo.
    echo Current Python: !PYTHON_CMD!
    !PYTHON_CMD! --version
    echo.
    echo Python 3.10 is REQUIRED for reliable installation.
    echo Other versions may cause build errors with pydantic-core.
    echo.
    echo Download Python 3.10.11 (RECOMMENDED):
    echo https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
    echo.
    echo Continue with current version? (Y/N)
    set /p choice=Choice: 
    if /i not "!choice!"=="Y" (
        echo Installation cancelled.
        pause
        exit /b 1
    )
    echo.
)

REM Create virtual environment
if not exist venv (
    echo Creating virtual environment with !PYTHON_CMD!...
    !PYTHON_CMD! -m venv venv
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
echo.
echo Note: If you see "Failed building wheel for pydantic-core",
echo this is normal and we'll install the binary version instead.
echo.

REM Install from requirements-dev.txt (includes all dependencies with versions)
pip install -r requirements-dev.txt
if !errorlevel! neq 0 (
    echo.
    echo Failed to install dependencies from requirements-dev.txt
    echo.
    echo Troubleshooting:
    echo 1. Your Python version may be incompatible
    echo 2. Current Python: !PYTHON_CMD!
    echo 3. Recommended: Python 3.10.x
    echo.
    pause
    exit /b 1
)
echo Core dependencies installed!
echo.

REM Dependencies already installed from requirements-dev.txt
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
