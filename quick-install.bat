@echo off
REM Quick installation script with error handling

echo ========================================
echo Star Resonance Market Analyzer
echo Quick Installation
echo ========================================
echo.

REM Find best Python version (3.10 REQUIRED)
call find-python.bat
set PYTHON_CHECK=%errorlevel%

if "%PYTHON_CMD%"=="" (
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

if %PYTHON_CHECK% equ 0 (
    echo ========================================
    echo ✓ Python 3.10.x detected! (PERFECT)
    echo ========================================
    %PYTHON_CMD% --version
    echo.
) else (
    echo ========================================
    echo WARNING: Python 3.10 not found!
    echo ========================================
    echo.
    echo Current Python: %PYTHON_CMD%
    %PYTHON_CMD% --version
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
    echo Creating virtual environment with %PYTHON_CMD%...
    %PYTHON_CMD% -m venv venv
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

REM Try to install with binary wheels (no build required)
pip install --only-binary :all: sqlalchemy==2.0.25 fastapi==0.109.0 uvicorn==0.27.0 pydantic==2.5.3 2>nul
if %errorlevel% neq 0 (
    echo Binary installation failed, trying without pydantic...
    pip install --no-cache-dir sqlalchemy==2.0.25 fastapi==0.109.0 uvicorn==0.27.0
    
    REM Install compatible pydantic version
    echo.
    echo Installing compatible pydantic version...
    pip install pydantic --prefer-binary
    
    if %errorlevel% neq 0 (
        echo Failed to install core dependencies
        echo.
        echo Troubleshooting:
        echo 1. Your Python version may be too new
        echo 2. Try: python --version
        echo 3. Recommended: Python 3.10 or 3.11
        pause
        exit /b 1
    )
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
