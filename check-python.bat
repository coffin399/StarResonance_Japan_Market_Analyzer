@echo off
REM Check Python compatibility

echo ========================================
echo Python Compatibility Check
echo ========================================
echo.

python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.10 or 3.11 from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo.
echo Checking Python version details...
python -c "import sys; print(f'Version: {sys.version}'); print(f'Major: {sys.version_info.major}'); print(f'Minor: {sys.version_info.minor}'); print(f'Micro: {sys.version_info.micro}')"

echo.
echo Checking compatibility...
python -c "import sys; major, minor = sys.version_info[:2]; print('✓ Compatible' if (major == 3 and 10 <= minor <= 13) else '⚠ May have compatibility issues')"

echo.
echo Recommended versions:
echo   ✓ Python 3.10.x - Fully tested
echo   ✓ Python 3.11.x - Fully tested
echo   ⚠ Python 3.12.x - May work
echo   ⚠ Python 3.13.x - May have issues
echo   ✗ Python 3.14.x - Not supported yet
echo.

echo Checking if pip is available...
python -m pip --version
if %errorlevel% neq 0 (
    echo ERROR: pip is not available
    echo Try: python -m ensurepip
    pause
    exit /b 1
)

echo.
echo Checking if venv is available...
python -m venv --help >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: venv is not available
    pause
    exit /b 1
)

echo.
echo ========================================
echo Check Complete!
echo ========================================
echo.

REM Suggest installation method
python -c "import sys; exit(0 if (sys.version_info.major == 3 and 10 <= sys.version_info.minor <= 11) else 1)"
if %errorlevel% equ 0 (
    echo Your Python version is perfect!
    echo.
    echo Recommended installation:
    echo   quick-install.bat
) else (
    echo Your Python version may have compatibility issues.
    echo.
    echo Recommended actions:
    echo 1. Install Python 3.10 or 3.11 from: https://www.python.org/downloads/
    echo 2. Or try minimal installation: install-minimal.bat
    echo 3. Or use Docker: docker-compose up -d
)

echo.
pause
