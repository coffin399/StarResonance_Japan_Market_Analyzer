@echo off
REM Enrich parsed items with names from master data
REM Usage: enrich-items.bat <parsed_items.json>

echo ========================================
echo Item Name Enrichment
echo ========================================
echo.

REM Check if json file is provided
if "%~1"=="" (
    echo Error: No JSON file specified
    echo.
    echo Usage: enrich-items.bat ^<parsed_items.json^>
    echo.
    echo Example:
    echo   enrich-items.bat parsed_items_20260128_123456.json
    echo.
    pause
    exit /b 1
)

REM Check if file exists
if not exist "%~1" (
    echo Error: File not found: %~1
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else if exist ..\venv\Scripts\activate.bat (
    call ..\venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    echo Please run quick-install.bat first.
    pause
    exit /b 1
)

REM Run enrichment
if exist tools\enrich_items.py (
    python tools\enrich_items.py "%~1"
) else if exist enrich_items.py (
    python enrich_items.py "%~1"
) else (
    echo ERROR: enrich_items.py not found
    pause
    exit /b 1
)

echo.
echo You can manually add item names to data\item_master.json
echo Then run this script again to update the names.
echo.
pause
