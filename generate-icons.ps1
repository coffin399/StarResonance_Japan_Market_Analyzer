# StarResonance Market Analyzer - Icon Generator
# This script generates all required icon files from a source image

$ErrorActionPreference = "Stop"

Write-Host "============================================"
Write-Host "StarResonance Market Analyzer"
Write-Host "Icon Generator"
Write-Host "============================================"
Write-Host ""

# Check if ImageMagick is installed
$magick = Get-Command "magick" -ErrorAction SilentlyContinue
if (-not $magick) {
    Write-Host "[ERROR] ImageMagick is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install ImageMagick from:"
    Write-Host "https://imagemagick.org/script/download.php"
    Write-Host ""
    Write-Host "Or use the online icon generator:"
    Write-Host "https://icon.kitchen/"
    Write-Host ""
    pause
    exit 1
}

Write-Host "[OK] ImageMagick found" -ForegroundColor Green
Write-Host ""

# Source image (you need to provide this)
$sourceImage = "app-icon-source.png"

if (-not (Test-Path $sourceImage)) {
    Write-Host "[WARNING] Source image not found: $sourceImage" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please create a square PNG image (1024x1024 or larger)"
    Write-Host "and save it as 'app-icon-source.png' in the project root"
    Write-Host ""
    Write-Host "Design guidelines:"
    Write-Host "  - Simple, recognizable design"
    Write-Host "  - Clear at small sizes"
    Write-Host "  - Transparent background recommended"
    Write-Host "  - Use bright, distinctive colors"
    Write-Host ""
    Write-Host "Quick icon creation tools:"
    Write-Host "  - Canva: https://www.canva.com/"
    Write-Host "  - Figma: https://www.figma.com/"
    Write-Host "  - GIMP: https://www.gimp.org/"
    Write-Host "  - Icon Kitchen: https://icon.kitchen/"
    Write-Host ""
    pause
    exit 1
}

Write-Host "[INFO] Generating icons from: $sourceImage"
Write-Host ""

# Create icons directory if it doesn't exist
$iconsDir = "src-tauri\icons"
if (-not (Test-Path $iconsDir)) {
    New-Item -ItemType Directory -Path $iconsDir | Out-Null
}

# Generate PNG icons
Write-Host "Generating PNG icons..."
& magick convert $sourceImage -resize 32x32 "$iconsDir\32x32.png"
& magick convert $sourceImage -resize 128x128 "$iconsDir\128x128.png"
& magick convert $sourceImage -resize 256x256 "$iconsDir\128x128@2x.png"
& magick convert $sourceImage -resize 512x512 "$iconsDir\icon.png"

Write-Host "[OK] PNG icons generated" -ForegroundColor Green

# Generate ICO file (Windows)
Write-Host "Generating Windows ICO file..."
& magick convert $sourceImage -define icon:auto-resize=256,128,96,64,48,32,16 "$iconsDir\icon.ico"
Write-Host "[OK] Windows ICO generated" -ForegroundColor Green

# Generate ICNS file (macOS) - optional
$icnsSupported = $true
try {
    $iconset = "icon.iconset"
    if (Test-Path $iconset) {
        Remove-Item -Recurse -Force $iconset
    }
    New-Item -ItemType Directory -Path $iconset | Out-Null
    
    Write-Host "Generating macOS ICNS file..."
    & magick convert $sourceImage -resize 16x16 "$iconset\icon_16x16.png"
    & magick convert $sourceImage -resize 32x32 "$iconset\icon_16x16@2x.png"
    & magick convert $sourceImage -resize 32x32 "$iconset\icon_32x32.png"
    & magick convert $sourceImage -resize 64x64 "$iconset\icon_32x32@2x.png"
    & magick convert $sourceImage -resize 128x128 "$iconset\icon_128x128.png"
    & magick convert $sourceImage -resize 256x256 "$iconset\icon_128x128@2x.png"
    & magick convert $sourceImage -resize 256x256 "$iconset\icon_256x256.png"
    & magick convert $sourceImage -resize 512x512 "$iconset\icon_256x256@2x.png"
    & magick convert $sourceImage -resize 512x512 "$iconset\icon_512x512.png"
    & magick convert $sourceImage -resize 1024x1024 "$iconset\icon_512x512@2x.png"
    
    # Note: Converting to ICNS requires macOS or additional tools
    Write-Host "[INFO] ICNS iconset created (requires macOS to convert to .icns)" -ForegroundColor Yellow
} catch {
    Write-Host "[WARNING] Could not generate ICNS (macOS only)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================"
Write-Host "Icon generation completed!"
Write-Host "============================================"
Write-Host ""
Write-Host "Generated files:"
Write-Host "  - src-tauri\icons\32x32.png"
Write-Host "  - src-tauri\icons\128x128.png"
Write-Host "  - src-tauri\icons\128x128@2x.png"
Write-Host "  - src-tauri\icons\icon.png"
Write-Host "  - src-tauri\icons\icon.ico (Windows)"
Write-Host ""
Write-Host "You can now build the application!"
Write-Host ""
pause
