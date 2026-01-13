@echo off
chcp 65001 >nul
:: StarResonance Market Analyzer - Auto-Elevate Launcher
:: This batch file automatically restarts with administrator privileges

:: Check administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    :: Already running as administrator -> start dev server
    call "%~dp0start-dev.bat"
) else (
    :: No administrator privileges -> restart as administrator
    echo Restarting with administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit
)
