@echo off
chcp 65001 >nul
:: StarResonance Market Analyzer - Quick Run Script
:: Run the built application with administrator privileges

echo ============================================
echo StarResonance Market Analyzer
echo Quick Run
echo ============================================
echo.

:: Check administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with administrator privileges
    echo.
) else (
    echo [WARNING] No administrator privileges
    echo Restarting with administrator privileges...
    echo.
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit
)

:: Find executable
set EXE_PATH=src-tauri\target\release\StarResonance-Market-Analyzer.exe

if exist "%EXE_PATH%" (
    echo [INFO] Starting application...
    echo.
    start "" "%EXE_PATH%"
    echo [OK] Application started
    echo.
    timeout /t 3 /nobreak >nul
    exit
) else (
    echo [ERROR] Executable not found
    echo.
    echo Please run one of the following:
    echo   1. build.bat - to build the application
    echo   2. start-dev.bat - to run in development mode
    echo.
    pause
    exit /b 1
)
