@echo off
REM Parse Game Packet V2 - Protobuf Based
REM Usage: parse-pcap-v2.bat <pcap_file>

echo ========================================
echo Game Packet Parser V2 (Protobuf)
echo ========================================
echo.

REM Check if pcap file is provided
if "%~1"=="" (
    echo Error: No pcap file specified
    echo.
    echo Usage: parse-pcap-v2.bat ^<pcap_file^>
    echo.
    echo Example:
    echo   parse-pcap-v2.bat capture.pcap
    echo.
    echo Drag and drop a .pcap file onto this batch file!
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
if exist ..\venv\Scripts\activate.bat (
    call ..\venv\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    echo Please run quick-install.bat first.
    pause
    exit /b 1
)

REM Run the parser
echo Parsing file: %~1
echo.

if exist tools\packet_parser_v2.py (
    python tools\packet_parser_v2.py "%~1"
) else if exist packet_parser_v2.py (
    python packet_parser_v2.py "%~1"
) else (
    echo ERROR: packet_parser_v2.py not found
    pause
    exit /b 1
)

echo.
pause
