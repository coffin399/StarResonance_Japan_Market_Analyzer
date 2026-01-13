@echo off
chcp 65001 >nul
:: StarResonance Market Analyzer - Development Mode Launcher
:: This batch file starts the development server with administrator privileges

echo ============================================
echo StarResonance Market Analyzer
echo Development Mode Launcher
echo ============================================
echo.

:: Check administrator privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with administrator privileges
    echo.
) else (
    echo [ERROR] Administrator privileges required!
    echo.
    echo Please right-click this batch file and
    echo select "Run as administrator"
    echo.
    pause
    exit /b 1
)

:: Check Node.js
where node >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Node.js is not installed
    echo Please download from https://nodejs.org/
    echo.
    pause
    exit /b 1
)
echo [OK] Node.js: 
node --version
echo.

:: Check Rust
where cargo >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Rust is not installed
    echo Please install from https://rustup.rs/
    echo.
    pause
    exit /b 1
)
echo [OK] Rust: 
rustc --version
echo.

:: Check dependencies
if not exist "node_modules" (
    echo [INFO] Installing dependencies...
    call npm install
    if %errorLevel% neq 0 (
        echo [ERROR] npm install failed
        pause
        exit /b 1
    )
    echo.
)

:: Check WinDivert files
echo [INFO] Checking WinDivert files...
set MISSING_FILES=0

if not exist "src-tauri\WinDivert.dll" (
    echo [WARNING] WinDivert.dll not found
    set MISSING_FILES=1
)

if not exist "src-tauri\WinDivert64.dll" (
    echo [WARNING] WinDivert64.dll not found
    set MISSING_FILES=1
)

if not exist "src-tauri\WinDivert64.sys" (
    echo [WARNING] WinDivert64.sys not found
    set MISSING_FILES=1
)

if %MISSING_FILES% equ 1 (
    echo.
    echo [ERROR] Missing WinDivert files
    echo Please refer to src-tauri\README_WINDIVERT.md
    echo.
    pause
    exit /b 1
)

echo [OK] All WinDivert files are present
echo.

:: Start development server
echo ============================================
echo Starting development server...
echo ============================================
echo.
echo [INFO] Press Ctrl+C to exit
echo.

npm run tauri dev

echo.
echo ============================================
echo Development server stopped
echo ============================================
pause
