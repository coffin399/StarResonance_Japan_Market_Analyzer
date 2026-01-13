# StarResonance Market Analyzer - Simple Icon Creator
# Creates a basic placeholder icon without ImageMagick

$ErrorActionPreference = "Stop"

Write-Host "============================================"
Write-Host "StarResonance Market Analyzer"
Write-Host "Simple Icon Creator"
Write-Host "============================================"
Write-Host ""
Write-Host "This script creates a simple SVG icon and converts it to PNG/ICO"
Write-Host ""

# Check if Inkscape is available (for SVG conversion)
$inkscape = Get-Command "inkscape" -ErrorAction SilentlyContinue

if (-not $inkscape) {
    Write-Host "[WARNING] Inkscape not found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "For best results, install Inkscape from:"
    Write-Host "https://inkscape.org/release/"
    Write-Host ""
    Write-Host "Alternatively, you can:"
    Write-Host "1. Use online icon generator: https://icon.kitchen/"
    Write-Host "2. Create icons manually with GIMP/Photoshop"
    Write-Host "3. Use the Windows built-in Paint 3D"
    Write-Host ""
}

# Create a simple SVG icon
$svgContent = @"
<?xml version="1.0" encoding="UTF-8"?>
<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <!-- Background -->
  <rect width="512" height="512" fill="#667eea" rx="80"/>
  
  <!-- Star shape -->
  <path d="M256 100 L290 200 L400 210 L330 280 L350 390 L256 330 L162 390 L182 280 L112 210 L222 200 Z" 
        fill="#ffffff" 
        stroke="#764ba2" 
        stroke-width="4"/>
  
  <!-- Inner circle -->
  <circle cx="256" cy="256" r="50" fill="#764ba2" opacity="0.8"/>
  
  <!-- Market graph line (simplified) -->
  <path d="M150 350 L200 320 L250 340 L300 300 L350 320" 
        stroke="#ffffff" 
        stroke-width="6" 
        fill="none" 
        stroke-linecap="round"/>
</svg>
"@

# Save SVG
$svgPath = "app-icon.svg"
$svgContent | Out-File -FilePath $svgPath -Encoding UTF8
Write-Host "[OK] SVG icon created: $svgPath" -ForegroundColor Green

# Create icons directory
$iconsDir = "src-tauri\icons"
if (-not (Test-Path $iconsDir)) {
    New-Item -ItemType Directory -Path $iconsDir | Out-Null
}

if ($inkscape) {
    Write-Host ""
    Write-Host "[INFO] Converting SVG to PNG formats..."
    
    # Convert SVG to various PNG sizes
    & inkscape $svgPath --export-type="png" --export-filename="$iconsDir\32x32.png" -w 32 -h 32
    & inkscape $svgPath --export-type="png" --export-filename="$iconsDir\128x128.png" -w 128 -h 128
    & inkscape $svgPath --export-type="png" --export-filename="$iconsDir\128x128@2x.png" -w 256 -h 256
    & inkscape $svgPath --export-type="png" --export-filename="$iconsDir\icon.png" -w 512 -h 512
    
    Write-Host "[OK] PNG icons generated" -ForegroundColor Green
    
    # Try to create ICO (may require additional tools)
    $magick = Get-Command "magick" -ErrorAction SilentlyContinue
    if ($magick) {
        Write-Host ""
        Write-Host "[INFO] Creating Windows ICO file..."
        & magick convert "$iconsDir\icon.png" -define icon:auto-resize=256,128,96,64,48,32,16 "$iconsDir\icon.ico"
        Write-Host "[OK] Windows ICO generated" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "[WARNING] ImageMagick not found - cannot create ICO file" -ForegroundColor Yellow
        Write-Host "Please use an online converter:"
        Write-Host "  - https://convertio.co/png-ico/"
        Write-Host "  - https://cloudconvert.com/png-to-ico"
        Write-Host ""
        Write-Host "Or install ImageMagick from:"
        Write-Host "  - https://imagemagick.org/script/download.php"
    }
} else {
    Write-Host ""
    Write-Host "[INFO] Please use one of these methods to convert SVG to PNG/ICO:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Method 1: Online Converter"
    Write-Host "  1. Upload app-icon.svg to https://icon.kitchen/"
    Write-Host "  2. Download the generated icons"
    Write-Host "  3. Place them in src-tauri\icons\"
    Write-Host ""
    Write-Host "Method 2: Manual Conversion"
    Write-Host "  1. Open app-icon.svg in Inkscape or Adobe Illustrator"
    Write-Host "  2. Export to PNG at different sizes (32, 128, 256, 512)"
    Write-Host "  3. Use an ICO converter for icon.ico"
    Write-Host ""
    Write-Host "Method 3: Install Tools"
    Write-Host "  1. Install Inkscape: https://inkscape.org/"
    Write-Host "  2. Install ImageMagick: https://imagemagick.org/"
    Write-Host "  3. Re-run this script"
}

Write-Host ""
Write-Host "============================================"
Write-Host "Icon creation completed!"
Write-Host "============================================"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Review the generated SVG: app-icon.svg"
Write-Host "  2. Convert to PNG/ICO if needed"
Write-Host "  3. Place all icons in src-tauri\icons\"
Write-Host "  4. Run build.bat to build the application"
Write-Host ""
pause
