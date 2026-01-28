@echo off
REM Parse Game Packet - Batch Script
REM Usage: parse-pcap.bat <pcap_file>

echo ========================================
echo Game Packet Parser
echo ========================================
echo.

REM Check if pcap file is provided
if "%~1"=="" (
    echo Error: No pcap file specified
    echo.
    echo Usage: parse-pcap.bat ^<pcap_file^>
    echo.
    echo Example:
    echo   parse-pcap.bat capture.pcap
    echo   parse-pcap.bat "C:\Users\YourName\capture.pcap"
    echo.
    echo Drag and drop a .pcap file onto this batch file to parse it!
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

REM Activate virtual environment first (REQUIRED)
if exist ..\venv\Scripts\activate.bat (
    call ..\venv\Scripts\activate.bat
    set "USE_VENV=1"
) else if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    set "USE_VENV=1"
) else (
    echo ========================================
    echo ERROR: Virtual environment not found!
    echo ========================================
    echo.
    echo Please run quick-install.bat first to set up the environment.
    echo This tool requires Python dependencies.
    echo.
    pause
    exit /b 1
)

REM Find best Python version (3.10 preferred)
if exist ..\find-python.bat (
    call ..\find-python.bat
) else if exist find-python.bat (
    call find-python.bat
) else (
    set "PYTHON_CMD=python"
)

if "%PYTHON_CMD%"=="" (
    set "PYTHON_CMD=python"
)

REM Run the parser
echo Parsing file: %~1
echo.

if "%USE_VENV%"=="1" (
    python tools\packet_parser.py "%~1"
) else (
    %PYTHON_CMD% tools\packet_parser.py "%~1"
)

REM Check result
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Parsing completed successfully!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Parsing failed with errors
    echo ========================================
)

echo.
pause
