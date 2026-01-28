@echo off
REM Debug version of quick-install with verbose output

echo ========================================
echo Star Resonance Market Analyzer
echo DEBUG Installation
echo ========================================
echo.

echo Step 1: Finding Python...
echo.

REM Test Python commands directly
echo Testing: py -3.10 --version
py -3.10 --version
echo Exit code: %errorlevel%
echo.

echo Testing: py -3 --version
py -3 --version
echo Exit code: %errorlevel%
echo.

echo Testing: python --version
python --version
echo Exit code: %errorlevel%
echo.

echo Step 2: Calling find-python.bat...
setlocal enabledelayedexpansion
call find-python.bat
set PYTHON_CHECK=!errorlevel!

echo.
echo Find-python.bat returned: !PYTHON_CHECK!
echo PYTHON_CMD is: "!PYTHON_CMD!"
echo PYTHON_FOUND is: "!PYTHON_FOUND!"
echo.

if "!PYTHON_CMD!"=="" (
    echo ERROR: PYTHON_CMD is empty!
    echo Python was not detected by find-python.bat
    echo.
    pause
    exit /b 1
) else (
    echo SUCCESS: Python found!
    echo Command: !PYTHON_CMD!
    echo.
    echo Testing the command:
    !PYTHON_CMD! --version
    echo.
)

echo Step 3: Checking errorlevel...
if !PYTHON_CHECK! equ 0 (
    echo Python 3.10.x detected!
) else (
    echo Python 3.10 not found, using alternative
)

echo.
echo Debug complete!
pause
