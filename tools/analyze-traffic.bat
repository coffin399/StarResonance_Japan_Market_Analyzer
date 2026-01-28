@echo off
REM Analyze Game Traffic - Interactive Tool
REM Helps identify the correct packets to capture

echo ========================================
echo Game Traffic Analyzer
echo ========================================
echo.

REM Activate virtual environment first (REQUIRED for scapy)
if exist ..\venv\Scripts\activate.bat (
    call ..\venv\Scripts\activate.bat
    set "USE_VENV=1"
    echo Virtual environment activated
    echo.
) else if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    set "USE_VENV=1"
    echo Virtual environment activated
    echo.
) else (
    echo ========================================
    echo ERROR: Virtual environment not found!
    echo ========================================
    echo.
    echo Please run quick-install.bat first to set up the environment.
    echo This tool requires scapy and other dependencies.
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

echo This tool will help you analyze game traffic to find trading center packets.
echo.
echo Options:
echo   1. Analyze existing pcap file
echo   2. List network interfaces (for live capture)
echo   3. Capture packets in real-time (requires admin)
echo   4. Search for magic bytes in pcap
echo   5. Exit
echo.

set /p choice=Enter your choice (1-5): 

if "%choice%"=="1" goto analyze_pcap
if "%choice%"=="2" goto list_interfaces
if "%choice%"=="3" goto live_capture
if "%choice%"=="4" goto search_magic
if "%choice%"=="5" goto end

echo Invalid choice
pause
exit /b 1

:analyze_pcap
echo.
set /p pcap_file=Enter pcap file path: 
if not exist "%pcap_file%" (
    echo File not found: %pcap_file%
    pause
    exit /b 1
)
if "%USE_VENV%"=="1" (
    python tools\packet_parser.py "%pcap_file%"
) else (
    %PYTHON_CMD% tools\packet_parser.py "%pcap_file%"
)
pause
exit /b 0

:list_interfaces
echo.
echo Listing network interfaces...
if "%USE_VENV%"=="1" (
    python -c "from scapy.all import get_if_list; print('\n'.join(get_if_list()))"
) else (
    %PYTHON_CMD% -c "from scapy.all import get_if_list; print('\n'.join(get_if_list()))"
)
echo.
echo Use one of these interface names for live capture.
pause
exit /b 0

:live_capture
echo.
echo WARNING: This requires administrator privileges
echo.
set /p duration=Enter capture duration in seconds (default 60): 
if "%duration%"=="" set duration=60

echo.
echo Starting live capture for %duration% seconds...
echo Open the game and browse the trading center now!
echo.

if "%USE_VENV%"=="1" (
    python -c "from scapy.all import sniff; pkts = sniff(timeout=%duration%, filter='tcp'); from scapy.all import wrpcap; wrpcap('live_capture.pcap', pkts); print(f'Captured {len(pkts)} packets to live_capture.pcap')"
) else (
    %PYTHON_CMD% -c "from scapy.all import sniff; pkts = sniff(timeout=%duration%, filter='tcp'); from scapy.all import wrpcap; wrpcap('live_capture.pcap', pkts); print(f'Captured {len(pkts)} packets to live_capture.pcap')"
)

if exist live_capture.pcap (
    echo.
    echo Capture complete! Analyzing...
    if "%USE_VENV%"=="1" (
        python tools\packet_parser.py live_capture.pcap
    ) else (
        %PYTHON_CMD% tools\packet_parser.py live_capture.pcap
    )
)
pause
exit /b 0

:search_magic
echo.
set /p pcap_file=Enter pcap file path: 
if not exist "%pcap_file%" (
    echo File not found: %pcap_file%
    pause
    exit /b 1
)

echo.
echo Searching for magic bytes...
if "%USE_VENV%"=="1" (
    python -c "import sys; data = open(r'%pcap_file%', 'rb').read(); magics = [b'\x00\x63\x33\x53\x42\x00', b'\x63\x33\x53\x42', b'c3SB']; [print(f'Found {m.hex()} at position {data.find(m)}') if data.find(m) != -1 else None for m in magics]"
) else (
    %PYTHON_CMD% -c "import sys; data = open(r'%pcap_file%', 'rb').read(); magics = [b'\x00\x63\x33\x53\x42\x00', b'\x63\x33\x53\x42', b'c3SB']; [print(f'Found {m.hex()} at position {data.find(m)}') if data.find(m) != -1 else None for m in magics]"
)

pause
exit /b 0

:end
echo Goodbye!
exit /b 0
