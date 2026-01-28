@echo off
setlocal enabledelayedexpansion

echo ================================================================================
echo JSON Encoding Fixer
echo ================================================================================
echo.

REM Check if virtual environment exists
if not exist "%~dp0..\venv\Scripts\python.exe" (
    echo Error: Virtual environment not found!
    echo Please run quick-install.bat first.
    echo.
    pause
    exit /b 1
)

REM Check if file argument provided
if "%~1"=="" (
    echo Usage: fix-json-encoding.bat input_file.json
    echo.
    echo Or drag and drop a JSON file onto this batch file.
    echo.
    pause
    exit /b 1
)

REM Get the script directory and input file
set SCRIPT_DIR=%~dp0
set INPUT_FILE=%~1

REM Change to project root
cd /d "%SCRIPT_DIR%.."

REM Run the fix script
echo Fixing encoding for: %INPUT_FILE%
echo.
venv\Scripts\python.exe tools\fix_json_encoding.py "%INPUT_FILE%"

echo.
pause
