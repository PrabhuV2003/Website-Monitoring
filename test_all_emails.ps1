# Test Both Emails
# =================
# Tests email sending for both websites

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  EMAIL TEST - BOTH WEBSITES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test Nevastech
Write-Host "[1/2] Testing Nevastech Email..." -ForegroundColor Yellow
Write-Host "      FROM: nevastech.monitor@gmail.com" -ForegroundColor Gray
Write-Host "      TO: renderthaniks@gmail.com, prabhu@nevastech.com" -ForegroundColor Gray
Write-Host ""

.\test_email_nevastech.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test Ascent365
Write-Host "[2/2] Testing Ascent365 Email..." -ForegroundColor Yellow
Write-Host "      FROM: ascent365.monitor@gmail.com" -ForegroundColor Gray
Write-Host "      TO: prabhuofficial2003@gmail.com" -ForegroundColor Gray
Write-Host ""

.\test_email_ascent365.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ALL TESTS COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Check inboxes for test emails!" -ForegroundColor Yellow
Write-Host ""

pause
