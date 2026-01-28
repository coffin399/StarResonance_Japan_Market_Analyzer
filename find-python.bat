@echo off
REM Find the best Python version (3.10 or 3.11 preferred)
REM Sets PYTHON_CMD environment variable

setlocal enabledelayedexpansion

REM Try Python 3.10 first (most compatible)
for %%v in (3.10.11 3.10.10 3.10.9 3.10.8 3.10.7 3.10.6 3.10.5 3.10.4 3.10.3 3.10.2 3.10.1 3.10.0) do (
    py -%%v --version >nul 2>&1
    if !errorlevel! equ 0 (
        endlocal
        set "PYTHON_CMD=py -%%v"
        exit /b 0
    )
)

REM Try Python 3.10 generic
py -3.10 --version >nul 2>&1
if %errorlevel% equ 0 (
    endlocal
    set "PYTHON_CMD=py -3.10"
    exit /b 0
)

REM Try Python 3.11 as second choice
for %%v in (3.11.8 3.11.7 3.11.6 3.11.5 3.11.4 3.11.3 3.11.2 3.11.1 3.11.0) do (
    py -%%v --version >nul 2>&1
    if !errorlevel! equ 0 (
        endlocal
        set "PYTHON_CMD=py -%%v"
        exit /b 0
    )
)

REM Try Python 3.11 generic
py -3.11 --version >nul 2>&1
if %errorlevel% equ 0 (
    endlocal
    set "PYTHON_CMD=py -3.11"
    exit /b 0
)

REM Try Python 3 generic
py -3 --version >nul 2>&1
if %errorlevel% equ 0 (
    endlocal
    set "PYTHON_CMD=py -3"
    exit /b 0
)

REM Try python command
python --version >nul 2>&1
if %errorlevel% equ 0 (
    endlocal
    set "PYTHON_CMD=python"
    exit /b 0
)

REM Try python3 command
python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    endlocal
    set "PYTHON_CMD=python3"
    exit /b 0
)

REM No suitable Python found
endlocal
set "PYTHON_CMD="
exit /b 1
