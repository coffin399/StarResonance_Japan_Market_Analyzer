@echo off
chcp 65001 >nul
:: StarResonance Market Analyzer - Build Script
:: Create release build

echo ============================================
echo StarResonance Market Analyzer
echo Release Build
echo ============================================
echo.

:: Check administrator privileges (not required for build, but show warning)
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [WARNING] Not running as administrator
    echo Build will work, but administrator privileges required to run the app
    echo.
)

:: Check Node.js
where node >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Node.js is not installed
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
    pause
    exit /b 1
)
echo [OK] Rust: 
rustc --version
echo.

:: Install dependencies
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
if not exist "src-tauri\WinDivert64.dll" (
    echo [ERROR] WinDivert64.dll not found
    echo Please refer to src-tauri\README_WINDIVERT.md
    pause
    exit /b 1
)
echo [OK] WinDivert files are present
echo.

:: Execute build
echo ============================================
echo Starting release build...
echo ============================================
echo.
echo This may take a few minutes.
echo.

call npm run tauri build

if %errorLevel% neq 0 (
    echo.
    echo [ERROR] Build failed
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo Build completed!
echo ============================================
echo.
echo Build output location:
echo   src-tauri\target\release\StarResonance-Market-Analyzer.exe
echo   src-tauri\target\release\bundle\msi\
echo.
echo When distributing the installer, please include:
echo   - WinDivert files (.dll, .sys)
echo   - LICENSE
echo   - LICENSE_NOTES.md
echo.
pause
