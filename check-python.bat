@echo off
REM Check Python 3.10 installation

echo ========================================
echo Python 3.10 Compatibility Check
echo ========================================
echo.

REM Test Python 3.10
echo Testing: py -3.10 --version
py -3.10 --version
set result=%errorlevel%
echo.

if %result% equ 0 (
    echo ========================================
    echo SUCCESS: Python 3.10 found!
    echo ========================================
    echo.
    
    echo Checking details...
    py -3.10 -c "import sys; print(f'Version: {sys.version}'); print(f'Path: {sys.executable}')"
    echo.
    
    echo Checking pip...
    py -3.10 -m pip --version
    echo.
    
    echo Checking venv...
    py -3.10 -m venv --help >nul 2>&1
    if %errorlevel% equ 0 (
        echo venv: OK
    ) else (
        echo venv: NOT FOUND
    )
    echo.
    
    echo ========================================
    echo Ready to install!
    echo Run: quick-install.bat
    echo ========================================
) else (
    echo ========================================
    echo ERROR: Python 3.10 not found!
    echo ========================================
    echo.
    echo Please install Python 3.10.11 from:
    echo https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
    echo.
    echo Important:
    echo 1. Run the installer
    echo 2. Check [X] Add Python 3.10 to PATH
    echo 3. Complete installation
    echo 4. Restart command prompt
    echo 5. Run this script again
    echo.
)

pause
