# WordPress Monitor - Prepare for VPS Deployment
# Run this script to prepare your files for upload to VPS

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "WordPress Monitor - VPS Preparation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (Test-Path ".env") {
    Write-Host "✓ .env file found" -ForegroundColor Green
    
    # Check for SMTP credentials
    $envContent = Get-Content ".env" -Raw
    if ($envContent -match "SMTP_USERNAME=" -and $envContent -match "SMTP_PASSWORD=") {
        Write-Host "✓ SMTP credentials configured" -ForegroundColor Green
    } else {
        Write-Host "⚠ .env file missing SMTP credentials" -ForegroundColor Yellow
        Write-Host "  Please run: .\setup_env.ps1" -ForegroundColor White
    }
} else {
    Write-Host "✗ .env file not found!" -ForegroundColor Red
    Write-Host "  Please run: .\setup_env.ps1" -ForegroundColor White
}

Write-Host ""

# Check requirements.txt
if (Test-Path "requirements.txt") {
    Write-Host "✓ requirements.txt exists" -ForegroundColor Green
} else {
    Write-Host "✗ requirements.txt not found!" -ForegroundColor Red
}

Write-Host ""

# Check config.yaml
if (Test-Path "config\config.yaml") {
    Write-Host "✓ config.yaml exists" -ForegroundColor Green
    
    # Check schedule configuration
    $configContent = Get-Content "config\config.yaml" -Raw
    if ($configContent -match "check_time:") {
        Write-Host "  Schedule configured" -ForegroundColor White
    }
} else {
    Write-Host "✗ config.yaml not found!" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Pre-Deployment Checklist" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠ Python not found in PATH" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Files ready for upload:" -ForegroundColor Yellow
Write-Host "  - config/config.yaml" -ForegroundColor White
Write-Host "  - .env (IMPORTANT: Contains credentials)" -ForegroundColor White
Write-Host "  - requirements.txt" -ForegroundColor White
Write-Host "  - All .py files" -ForegroundColor White
Write-Host "  - All subdirectories (utils/, monitors/, etc.)" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VPS Information Needed" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Prompt for VPS details
Write-Host "Please have ready from Hostinger:" -ForegroundColor Yellow
Write-Host "  1. VPS IP Address (e.g., 123.45.67.89)" -ForegroundColor White
Write-Host "  2. SSH Username (usually 'root')" -ForegroundColor White
Write-Host "  3. SSH Password or Key" -ForegroundColor White
Write-Host "  4. VPS Plan (should have 2GB+ RAM)" -ForegroundColor White
Write-Host ""

$continue = Read-Host "Do you have your VPS details ready? (y/n)"

if ($continue -eq "y") {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Next Steps" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "OPTION 1 - Using WinSCP (Easiest):" -ForegroundColor Cyan
    Write-Host "  1. Download WinSCP: https://winscp.net/" -ForegroundColor White
    Write-Host "  2. Connect to your VPS" -ForegroundColor White
    Write-Host "  3. Upload entire 'wordpress-monitor' folder" -ForegroundColor White
    Write-Host ""
    Write-Host "OPTION 2 - Using Command Line:" -ForegroundColor Cyan
    Write-Host "  Read: VPS_DEPLOYMENT.md (Step 4)" -ForegroundColor White
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Full Guide: Open VPS_DEPLOYMENT.md" -ForegroundColor Green
    Write-Host "Quick Checklist: Open DEPLOYMENT_CHECKLIST.md" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    # Ask if they want to open the deployment guide
    $openGuide = Read-Host "Open VPS_DEPLOYMENT.md now? (y/n)"
    if ($openGuide -eq "y") {
        Start-Process "VPS_DEPLOYMENT.md"
    }
    
} else {
    Write-Host ""
    Write-Host "Please gather your VPS information from Hostinger first." -ForegroundColor Yellow
    Write-Host "Then run this script again." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host ""
Write-Host "Good luck with your deployment! 🚀" -ForegroundColor Cyan
Write-Host ""
