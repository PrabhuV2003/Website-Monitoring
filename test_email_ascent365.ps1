# Quick Email Test - Ascent365
# ==============================
# Tests if email sending works for Ascent365

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  EMAIL TEST - ASCENT365" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Testing email configuration..." -ForegroundColor Yellow
Write-Host "FROM: ascent365.monitor@gmail.com" -ForegroundColor Gray
Write-Host "TO: prabhuofficial2003@gmail.com" -ForegroundColor Gray
Write-Host ""

# Run quick check and send email
python -c @"
from main import WordPressMonitor
from utils.config_loader import ConfigLoader
from utils.alerts import create_alert_manager
from pathlib import Path

print('Running quick check...')
monitor = WordPressMonitor('config/ascent365.yaml')
result = monitor.run_all_checks(use_browser=False, headless=True)

print('\nGenerating report...')
report_html = result.get('report_path')

if report_html:
    print(f'Report: {report_html}')
    
    # Generate PDF
    from utils.reporting import ReportGenerator
    report_gen = ReportGenerator('reports/ascent365')
    pdf_path = report_gen.convert_html_to_pdf(report_html)
    
    if pdf_path and Path(pdf_path).exists():
        print(f'PDF: {pdf_path}')
        
        # Send test email
        config = ConfigLoader('config/ascent365.yaml')
        alert_mgr = create_alert_manager(config.to_dict())
        
        print('\nSending test email...')
        email_result = alert_mgr.send_report_email(
            recipient_emails=['prabhuofficial2003@gmail.com'],
            pdf_path=pdf_path,
            report_summary={
                'critical_issues': result.get('critical_issues', 0),
                'high_issues': result.get('high_issues', 0),
                'medium_issues': result.get('medium_issues', 0),
                'low_issues': result.get('low_issues', 0),
                'total_issues': result.get('total_issues', 0),
                'avg_response_time': result.get('avg_response_time', 0),
                'uptime_percentage': result.get('uptime_percentage', 100),
                'pages_checked': result.get('pages_checked', 0),
            },
            website_name='Ascent Innovation',
            website_url='https://www.ascent365.com'
        )
        
        print('\n' + '='*40)
        if email_result.get('status') == 'success':
            print('SUCCESS! Email sent!')
            print('='*40)
            print('Check the inbox for:')
            print('  - prabhuofficial2003@gmail.com')
        else:
            print('FAILED! Email not sent!')
            print('='*40)
            print(f'Error: {email_result.get(\"message\")}')
            print('\nPossible issues:')
            print('  1. Wrong Gmail credentials in config/ascent365.yaml')
            print('  2. Wrong App Password')
            print('  3. 2-Step Verification not enabled')
    else:
        print('ERROR: PDF generation failed')
else:
    print('ERROR: Report generation failed')
"@

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

pause
