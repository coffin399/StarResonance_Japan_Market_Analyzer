@echo off
REM Check Python compatibility

echo ========================================
echo Python Compatibility Check
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

echo ========================================
if !PYTHON_CHECK! equ 0 (
    echo PERFECT: Python 3.10.x found!
) else (
    echo WARNING: Python 3.10 not found
)
echo ========================================
echo.
echo Found Python: !PYTHON_CMD!
!PYTHON_CMD! --version

echo.
echo Checking Python version details...
!PYTHON_CMD! -c "import sys; print(f'Version: {sys.version}'); print(f'Major: {sys.version_info.major}'); print(f'Minor: {sys.version_info.minor}'); print(f'Micro: {sys.version_info.micro}')"

echo.
echo Checking compatibility...
!PYTHON_CMD! -c "import sys; major, minor = sys.version_info[:2]; print('Compatible' if (major == 3 and 10 <= minor <= 13) else 'May have compatibility issues')"

echo.
echo Checking if pip is available...
!PYTHON_CMD! -m pip --version
if !errorlevel! neq 0 (
    echo ERROR: pip is not available
    echo Try: !PYTHON_CMD! -m ensurepip
    pause
    exit /b 1
)

echo.
echo Checking if venv is available...
!PYTHON_CMD! -m venv --help >nul 2>&1
if !errorlevel! neq 0 (
    echo ERROR: venv is not available
    pause
    exit /b 1
)

echo.
echo All checks passed!
echo.

REM Suggest installation method
!PYTHON_CMD! -c "import sys; exit(0 if (sys.version_info.major == 3 and 10 <= sys.version_info.minor <= 11) else 1)"
if !errorlevel! equ 0 (
    echo ========================================
    echo Your Python version is PERFECT!
    echo ========================================
    echo.
    echo Recommended installation:
    echo   quick-install.bat
) else (
    echo ========================================
    echo Your Python version may have compatibility issues
    echo ========================================
    echo.
    echo Recommended actions:
    echo 1. Install Python 3.10.11 from:
    echo    https://www.python.org/downloads/release/python-31011/
    echo.
    echo 2. Or try minimal installation:
    echo    install-minimal.bat
    echo.
    echo 3. Or use Docker (most reliable):
    echo    docker-compose up -d
)

echo.
pause
