@echo off
chcp 65001 >nul
:: StarResonance Market Analyzer - Dummy Icon Creator
:: Creates minimal valid icon files for building

echo ============================================
echo StarResonance Market Analyzer
echo Dummy Icon Creator
echo ============================================
echo.
echo [INFO] Creating minimal valid icon files for building...
echo.
echo [WARNING] These are placeholder icons only!
echo Please create proper icons later using:
echo   - Online: https://icon.kitchen/
echo   - Script: .\create-simple-icon.ps1
echo   - Manual: See ICONS_GUIDE.md
echo.

:: Create icons directory
if not exist "src-tauri\icons" mkdir "src-tauri\icons"

:: Create a minimal 16x16 ICO file using PowerShell
powershell -Command "$bytes = [Convert]::FromBase64String('AAABAAEAEBAAAAEAIABoBAAAFgAAACgAAAAQAAAAIAAAAAEAIAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=='); Set-Content -Path 'src-tauri\icons\icon.ico' -Value $bytes -Encoding Byte"

echo [OK] Created: src-tauri\icons\icon.ico

:: Create minimal PNG files using PowerShell
:: 32x32 PNG (1x1 pixel placeholder scaled)
powershell -Command "Add-Type -AssemblyName System.Drawing; $bmp = New-Object System.Drawing.Bitmap(32,32); $g = [System.Drawing.Graphics]::FromImage($bmp); $g.Clear([System.Drawing.Color]::FromArgb(102,126,234)); $brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White); $g.FillEllipse($brush, 6, 6, 20, 20); $bmp.Save('src-tauri\icons\32x32.png', [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()"

echo [OK] Created: src-tauri\icons\32x32.png

:: 128x128 PNG
powershell -Command "Add-Type -AssemblyName System.Drawing; $bmp = New-Object System.Drawing.Bitmap(128,128); $g = [System.Drawing.Graphics]::FromImage($bmp); $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias; $g.Clear([System.Drawing.Color]::FromArgb(102,126,234)); $brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White); $g.FillEllipse($brush, 24, 24, 80, 80); $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(118,75,162), 4); $g.DrawLine($pen, 30, 90, 50, 70); $g.DrawLine($pen, 50, 70, 64, 85); $g.DrawLine($pen, 64, 85, 78, 60); $g.DrawLine($pen, 78, 60, 98, 75); $bmp.Save('src-tauri\icons\128x128.png', [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()"

echo [OK] Created: src-tauri\icons\128x128.png

:: 256x256 PNG (128x128@2x)
powershell -Command "Add-Type -AssemblyName System.Drawing; $bmp = New-Object System.Drawing.Bitmap(256,256); $g = [System.Drawing.Graphics]::FromImage($bmp); $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias; $g.Clear([System.Drawing.Color]::FromArgb(102,126,234)); $brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White); $g.FillEllipse($brush, 48, 48, 160, 160); $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(118,75,162), 8); $g.DrawLine($pen, 60, 180, 100, 140); $g.DrawLine($pen, 100, 140, 128, 170); $g.DrawLine($pen, 128, 170, 156, 120); $g.DrawLine($pen, 156, 120, 196, 150); $bmp.Save('src-tauri\icons\128x128@2x.png', [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()"

echo [OK] Created: src-tauri\icons\128x128@2x.png

:: 512x512 PNG (icon.png)
powershell -Command "Add-Type -AssemblyName System.Drawing; $bmp = New-Object System.Drawing.Bitmap(512,512); $g = [System.Drawing.Graphics]::FromImage($bmp); $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias; $g.Clear([System.Drawing.Color]::FromArgb(102,126,234)); $brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White); $g.FillEllipse($brush, 96, 96, 320, 320); $pen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(118,75,162), 16); $g.DrawLine($pen, 120, 360, 200, 280); $g.DrawLine($pen, 200, 280, 256, 340); $g.DrawLine($pen, 256, 340, 312, 240); $g.DrawLine($pen, 312, 240, 392, 300); $font = New-Object System.Drawing.Font('Arial', 32, [System.Drawing.FontStyle]::Bold); $textBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(118,75,162)); $g.DrawString('SR', $font, $textBrush, 220, 220); $bmp.Save('src-tauri\icons\icon.png', [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose(); $font.Dispose()"

echo [OK] Created: src-tauri\icons\icon.png

echo.
echo ============================================
echo Dummy icons created successfully!
echo ============================================
echo.
echo [WARNING] These are basic placeholder icons
echo.
echo For production, create proper icons:
echo   1. Use https://icon.kitchen/ (easiest)
echo   2. Run .\create-simple-icon.ps1
echo   3. Follow ICONS_GUIDE.md
echo.
echo You can now build the application!
echo.
pause
