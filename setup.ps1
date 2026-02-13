# WordPress Monitor - Setup Script
# Run this to install dependencies and configure the tool

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  WordPress Monitor - Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create directories
Write-Host ""
Write-Host "Creating directories..." -ForegroundColor Yellow
$dirs = @("logs", "reports", "screenshots", "data", "data\baselines")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "Created: $dir" -ForegroundColor Gray
    }
}

# Check config
Write-Host ""
Write-Host "Checking configuration..." -ForegroundColor Yellow
if (Test-Path "config\config.yaml") {
    Write-Host "Configuration file exists" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Edit config\config.yaml to set your website URL!" -ForegroundColor Yellow
} else {
    Write-Host "Configuration file not found!" -ForegroundColor Red
}

# Create .env from example
if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env file from template" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Edit config\config.yaml with your website URL"
Write-Host "2. Edit .env with your email/Slack credentials"
Write-Host "3. Run: python cli.py check --url https://your-site.com"
Write-Host ""
Write-Host "Or run the interactive setup:"
Write-Host "  python cli.py init"
Write-Host ""
