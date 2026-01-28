@echo off
REM Test Python Installation

echo ========================================
echo Python Installation Test
echo ========================================
echo.

echo Testing: py -3.10
py -3.10 --version
echo Exit code: %errorlevel%
echo.

echo Testing: py -3.11
py -3.11 --version
echo Exit code: %errorlevel%
echo.

echo Testing: py -3
py -3 --version
echo Exit code: %errorlevel%
echo.

echo Testing: py
py --version
echo Exit code: %errorlevel%
echo.

echo Testing: python
python --version
echo Exit code: %errorlevel%
echo.

echo Testing: python3
python3 --version
echo Exit code: %errorlevel%
echo.

echo ========================================
echo Listing all Python installations:
echo ========================================
py --list
echo.

pause
