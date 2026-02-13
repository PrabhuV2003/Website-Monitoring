# Start All Website Monitors
# ===========================
# This script starts schedulers for both monitored websites

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  WordPress Monitor - Multi-Site Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Website 1: Nevastech
Write-Host "[1] Website 1: Nevas Technologies" -ForegroundColor Green
Write-Host "    URL: https://www.nevastech.com" -ForegroundColor Gray
Write-Host "    Email: renderthaniks@gmail.com, prabhu@nevastech.com" -ForegroundColor Gray
Write-Host "    Schedule: Daily at 4:30 PM" -ForegroundColor Gray
Write-Host ""

# Website 2: Ascent365
Write-Host "[2] Website 2: Ascent Innovation" -ForegroundColor Green
Write-Host "    URL: https://www.ascent365.com" -ForegroundColor Gray
Write-Host "    Email: prabhuofficial2003@gmail.com" -ForegroundColor Gray
Write-Host "    Schedule: Daily at 6:00 AM" -ForegroundColor Gray
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found! Please install Python first." -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "Starting both schedulers..." -ForegroundColor Yellow
Write-Host ""

# Start Nevastech scheduler in new window
Write-Host "Starting Nevastech scheduler..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "cd '$PWD'; Write-Host ''; Write-Host '========================================' -ForegroundColor Magenta; Write-Host '  NEVASTECH MONITOR' -ForegroundColor Magenta; Write-Host '  https://www.nevastech.com' -ForegroundColor Magenta; Write-Host '  Schedule: Daily at 4:30 PM' -ForegroundColor Magenta; Write-Host '========================================' -ForegroundColor Magenta; Write-Host ''; python scheduler_nevastech.py"

# Wait a moment
Start-Sleep -Seconds 2

# Start Ascent365 scheduler in new window
Write-Host "Starting Ascent365 scheduler..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "cd '$PWD'; Write-Host ''; Write-Host '========================================' -ForegroundColor Green; Write-Host '  ASCENT365 MONITOR' -ForegroundColor Green; Write-Host '  https://www.ascent365.com' -ForegroundColor Green; Write-Host '  Schedule: Daily at 6:00 AM' -ForegroundColor Green; Write-Host '========================================' -ForegroundColor Green; Write-Host ''; python scheduler_ascent365.py"

# Wait a moment
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "[OK] Both schedulers started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor Yellow
Write-Host "  - Nevastech: Runs daily at 4:30 PM" -ForegroundColor White
Write-Host "  - Ascent365: Runs daily at 6:00 AM" -ForegroundColor White
Write-Host ""
Write-Host "TIP: Each scheduler has its own window" -ForegroundColor Cyan
Write-Host "     Press Ctrl+C in each window to stop them" -ForegroundColor Cyan
Write-Host ""
Write-Host "Email Reports:" -ForegroundColor Yellow
Write-Host "  - Nevastech  -> renderthaniks@gmail.com, prabhu@nevastech.com" -ForegroundColor White
Write-Host "  - Ascent365 -> prabhuofficial2003@gmail.com" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

pause
