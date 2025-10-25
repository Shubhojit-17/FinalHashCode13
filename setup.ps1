# EADA Pro - Quick Setup Script for Windows
# Run this with Python 3.10 or 3.11

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "EADA Pro - Quick Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "Found: $pythonVersion" -ForegroundColor Green

# Parse version
if ($pythonVersion -match "Python (\d+)\.(\d+)") {
    $major = [int]$matches[1]
    $minor = [int]$matches[2]
    
    if ($major -eq 3 -and ($minor -eq 10 -or $minor -eq 11)) {
        Write-Host "✓ Python version is compatible!" -ForegroundColor Green
    } else {
        Write-Host "✗ Python $major.$minor detected" -ForegroundColor Red
        Write-Host "EADA Pro requires Python 3.10 or 3.11" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install Python 3.10 or 3.11 and try again." -ForegroundColor Yellow
        Write-Host "See INSTALL.md for detailed instructions." -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "⚠ Could not determine Python version" -ForegroundColor Yellow
}

Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists." -ForegroundColor Yellow
    $response = Read-Host "Do you want to recreate it? (y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Host "Removing old virtual environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force venv
    } else {
        Write-Host "Using existing virtual environment." -ForegroundColor Green
        Write-Host ""
        Write-Host "To activate it, run:" -ForegroundColor Cyan
        Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
        exit 0
    }
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to create virtual environment" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Virtual environment created" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Cyan
Write-Host ""

# Install in stages for better error handling
Write-Host "[1/5] Installing core libraries..." -ForegroundColor Cyan
pip install numpy==1.24.3 --quiet
if ($LASTEXITCODE -ne 0) { Write-Host "✗ Failed to install numpy" -ForegroundColor Red; exit 1 }

pip install opencv-python==4.8.1.78 --quiet
if ($LASTEXITCODE -ne 0) { Write-Host "✗ Failed to install opencv" -ForegroundColor Red; exit 1 }

pip install mediapipe==0.10.9 --quiet
if ($LASTEXITCODE -ne 0) { Write-Host "✗ Failed to install mediapipe" -ForegroundColor Red; exit 1 }

Write-Host "✓ Core libraries installed" -ForegroundColor Green

Write-Host "[2/5] Installing audio libraries..." -ForegroundColor Cyan
pip install sounddevice==0.4.6 scipy==1.11.4 --quiet
if ($LASTEXITCODE -ne 0) { Write-Host "⚠ Audio libraries installation had issues" -ForegroundColor Yellow }
else { Write-Host "✓ Audio libraries installed" -ForegroundColor Green }

Write-Host "[3/5] Installing system control..." -ForegroundColor Cyan
pip install screen-brightness-control==0.21.0 --quiet
pip install comtypes==1.2.0 --quiet
pip install pycaw==20230407 --quiet
Write-Host "✓ System control installed" -ForegroundColor Green

Write-Host "[4/5] Installing web framework..." -ForegroundColor Cyan
pip install fastapi==0.104.1 uvicorn==0.24.0 --quiet
Write-Host "✓ Web framework installed" -ForegroundColor Green

Write-Host "[5/5] Installing utilities..." -ForegroundColor Cyan
pip install requests==2.31.0 Pillow==10.1.0 --quiet
Write-Host "✓ Utilities installed" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run tests: python test.py" -ForegroundColor White
Write-Host "  2. Run EADA Pro: python run.py" -ForegroundColor White
Write-Host ""
Write-Host "Note: If you closed this window, activate the environment with:" -ForegroundColor Cyan
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
