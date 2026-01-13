@echo off
chcp 65001 >nul
:: StarResonance Market Analyzer - Clean Script
:: Clean build cache and node_modules

echo ============================================
echo StarResonance Market Analyzer
echo Clean Build Cache
echo ============================================
echo.

echo [WARNING] This will delete:
echo   - node_modules
echo   - src-tauri\target
echo   - .svelte-kit
echo   - build
echo.

choice /M "Continue?"
if %errorLevel% neq 1 goto :cancel

echo.
echo [INFO] Cleaning up...
echo.

:: Node.js related
if exist "node_modules" (
    echo Removing node_modules...
    rmdir /s /q "node_modules"
)

if exist ".svelte-kit" (
    echo Removing .svelte-kit...
    rmdir /s /q ".svelte-kit"
)

if exist "build" (
    echo Removing build...
    rmdir /s /q "build"
)

:: Rust related
if exist "src-tauri\target" (
    echo Removing src-tauri\target...
    rmdir /s /q "src-tauri\target"
)

echo.
echo ============================================
echo Cleanup completed!
echo ============================================
echo.
echo Dependencies will be reinstalled on next build
echo.
pause
exit /b 0

:cancel
echo.
echo Cancelled
pause
exit /b 0
