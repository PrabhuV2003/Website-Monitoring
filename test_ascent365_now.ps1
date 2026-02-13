# Test Ascent365 Monitor NOW
# Don't wait for scheduled time!

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  ASCENT365 TEST RUN" -ForegroundColor Cyan
Write-Host "  Running check immediately..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Run the check immediately
python -c "from main import WordPressMonitor; m = WordPressMonitor('config/ascent365.yaml'); result = m.run_all_checks(use_browser=False, headless=True); print(''); print('Report:', result.get('report_path')); print('Total Issues:', result.get('total_issues', 0))"

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "  TEST COMPLETE!" -ForegroundColor Green  
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Check the reports/ascent365/ folder for the report!" -ForegroundColor Yellow
Write-Host ""

pause
