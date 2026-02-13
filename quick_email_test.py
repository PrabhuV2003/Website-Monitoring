"""
Quick Email Test - Run a monitoring check and send PDF report immediately
This simulates what the scheduler does but runs instantly for testing
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from main import WordPressMonitor
from utils.reporting import ReportGenerator
from utils.alerts import create_alert_manager
from utils.config_loader import ConfigLoader

print("=" * 70)
print("QUICK EMAIL TEST - Automatic PDF Report Sending")
print("=" * 70)
print("")
print("This will:")
print("  1. Run a quick website check")
print("  2. Generate PDF report")
print("  3. Send email with PDF attachment")
print("")
print("=" * 70)

try:
    # Load config
    print("\n[1/5] Loading configuration...")
    config = ConfigLoader('config/config.yaml')
    website_url = config.get_website_url()
    website_name = config.get('website', 'name', default='WordPress Site')
    
    email_config = config.get('alerts', 'email', default={})
    recipients = email_config.get('recipients', [])
    
    print(f"      Website: {website_name}")
    print(f"      URL: {website_url}")
    print(f"      Recipients: {', '.join(recipients)}")
    
    # Run monitoring check (quick mode - only homepage)
    print("\n[2/5] Running quick website check...")
    print("      This may take 10-30 seconds...")
    monitor = WordPressMonitor('config/config.yaml')
    
    # Run a fast check - only check homepage
    result = monitor.run_link_check_only(
        pages=['/'],  # Only check homepage
        limit=10,     # Only check first 10 links
        generate_report=True
    )
    
    issues_found = result.get('total_issues', 0)
    print(f"      Check completed!")
    print(f"      Issues found: {issues_found}")
    
    # Get report path
    report_html = result.get('report_path')
    if not report_html:
        print("\n[ERROR] No report generated!")
        sys.exit(1)
    
    print(f"\n[3/5] HTML report created: {report_html}")
    
    # Generate PDF
    print("\n[4/5] Converting to PDF...")
    print("      This may take 5-10 seconds...")
    report_gen = ReportGenerator()
    pdf_path = report_gen.convert_html_to_pdf(report_html)
    
    if not pdf_path:
        print("\n[ERROR] Failed to generate PDF!")
        print("      Make sure Playwright is installed:")
        print("      pip install playwright")
        print("      playwright install chromium")
        sys.exit(1)
    
    print(f"      PDF created: {pdf_path}")
    
    # Send email
    print("\n[5/5] Sending email with PDF attachment...")
    alert_mgr = create_alert_manager(config.to_dict())
    
    report_summary = {
        'critical_issues': result.get('critical_issues', 0),
        'high_issues': result.get('high_issues', 0),
        'medium_issues': result.get('medium_issues', 0),
        'low_issues': result.get('low_issues', 0),
        'total_issues': result.get('total_issues', 0),
        'avg_response_time': result.get('avg_response_time', 0),
        'uptime_percentage': result.get('uptime_percentage', 100),
        'pages_checked': result.get('pages_checked', 0)
    }
    
    email_result = alert_mgr.send_report_email(
        recipient_emails=recipients,
        pdf_path=pdf_path,
        report_summary=report_summary,
        website_name=website_name,
        website_url=website_url
    )
    
    # Show results
    print("")
    print("=" * 70)
    if email_result.get('status') == 'success':
        print("SUCCESS! Email sent successfully!")
        print("=" * 70)
        print("")
        print("Email Details:")
        print(f"  To: {', '.join(email_result.get('recipients', []))}")
        print(f"  Subject: Website Health Report - {website_name}")
        print(f"  Attachment: {Path(pdf_path).name}")
        print("")
        print("Check your inbox:")
        for recipient in email_result.get('recipients', []):
            print(f"  - {recipient}")
        print("")
        print("The email includes:")
        print("  - Health score with emoji indicator")
        print("  - Issue summary (Critical, High, Medium, Low)")
        print("  - Performance metrics")
        print("  - PDF report attachment")
        print("")
    else:
        print("FAILED to send email")
        print("=" * 70)
        print("")
        print(f"Error: {email_result.get('message')}")
        print("")
        print("Common issues:")
        print("  1. Gmail App Password incorrect")
        print("  2. SMTP blocked by firewall")
        print("  3. Internet connection issue")
        print("")
        sys.exit(1)
    
    print("=" * 70)
    print("")
    print("Next Steps:")
    print("  1. Check your email inbox")
    print("  2. Open the PDF attachment")
    print("  3. If working, start scheduler: python scheduler.py")
    print("")
    
except Exception as e:
    print("")
    print("=" * 70)
    print("ERROR occurred during test")
    print("=" * 70)
    print("")
    print(f"Error: {str(e)}")
    print("")
    import traceback
    traceback.print_exc()
    print("")
    sys.exit(1)
