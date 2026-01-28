@echo off
REM Debug PCAP Parser - Shows detailed packet analysis
REM Usage: debug-pcap.bat <pcap_file>

echo ========================================
echo DEBUG Packet Parser
echo ========================================
echo.

REM Check if pcap file is provided
if "%~1"=="" (
    echo Error: No pcap file specified
    echo.
    echo Usage: debug-pcap.bat ^<pcap_file^>
    echo.
    echo Example:
    echo   debug-pcap.bat capture.pcap
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

REM Run debug parser
echo Running debug parser...
echo.

REM Check if running from project root or tools directory
if exist tools\packet_parser_debug.py (
    python tools\packet_parser_debug.py "%~1"
) else if exist packet_parser_debug.py (
    python packet_parser_debug.py "%~1"
) else (
    echo ERROR: packet_parser_debug.py not found
    echo Please run from project root or tools directory
    pause
    exit /b 1
)

echo.
pause
