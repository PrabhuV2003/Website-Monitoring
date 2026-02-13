"""
Test Email Functionality - Send a test PDF report to verify email configuration
"""
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.config_loader import ConfigLoader
from utils.alerts import create_alert_manager
from utils.reporting import ReportGenerator


def test_email_with_pdf():
    """Test sending an email with a PDF report."""
    
    print("=" * 60)
    print("📧 EMAIL CONFIGURATION TEST")
    print("=" * 60)
    
    # Load configuration
    config = ConfigLoader('config/config.yaml')
    
    # Check email configuration
    email_config = config.get('alerts', 'email', default={})
    enabled = email_config.get('enabled', False)
    recipients = email_config.get('recipients', [])
    
    print(f"\n📋 Email Settings:")
    print(f"   Enabled: {enabled}")
    print(f"   SMTP Server: {email_config.get('smtp_server', 'Not configured')}")
    print(f"   SMTP Port: {email_config.get('smtp_port', 'Not configured')}")
    print(f"   From Email: {email_config.get('from_email', 'Not configured')}")
    print(f"   Recipients: {', '.join(recipients) if recipients else 'None configured'}")
    
    # Check environment variables
    smtp_user = os.getenv('SMTP_USERNAME')
    smtp_pass = os.getenv('SMTP_PASSWORD')
    
    print(f"\n🔐 Environment Variables:")
    print(f"   SMTP_USERNAME: {'✅ Set' if smtp_user else '❌ Not set'}")
    print(f"   SMTP_PASSWORD: {'✅ Set' if smtp_pass else '❌ Not set'}")
    
    # Check if ready to send
    if not enabled:
        print("\n❌ Email is DISABLED in config.yaml")
        print("   Enable it by setting: alerts.email.enabled: true")
        return False
    
    if not recipients:
        print("\n❌ No recipients configured")
        print("   Add recipients in config.yaml under alerts.email.recipients")
        return False
    
    if not smtp_user or not smtp_pass:
        print("\n❌ SMTP credentials not set")
        print("   Set environment variables:")
        print("   - SMTP_USERNAME")
        print("   - SMTP_PASSWORD")
        return False
    
    print("\n✅ Email configuration is complete!")
    
    # Ask for confirmation
    print("\n" + "=" * 60)
    print("📨 READY TO SEND TEST EMAIL")
    print("=" * 60)
    print(f"\nThis will send a test PDF report to:")
    for recipient in recipients:
        print(f"  • {recipient}")
    
    response = input("\nProceed? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n❌ Test cancelled by user")
        return False
    
    print("\n🚀 Sending test email...")
    
    # Create test report data
    test_data = {
        'stats': {
            'website_url': config.get_website_url(),
            'website_name': config.get('website', 'name', default='WordPress Site'),
            'critical_issues': 1,
            'high_issues': 2,
            'medium_issues': 3,
            'low_issues': 5,
            'total_issues': 11,
            'avg_response_time': 450,
            'uptime_percentage': 99.8,
            'pages_checked': 5,
            'links_checked': 42
        },
        'issues': [
            {
                'severity': 'critical',
                'message': 'SSL certificate expires in 5 days',
                'monitor': 'uptime',
                'url': config.get_website_url(),
                'details': {}
            },
            {
                'severity': 'high',
                'message': '3 broken links found',
                'monitor': 'links',
                'url': config.get_website_url() + '/',
                'details': {
                    'broken_links': [
                        {'link_url': '/broken-page', 'link_text': 'Old Page', 'status_code': 404, 'status_message': 'Not Found', 'found_on_page': '/'}
                    ]
                }
            }
        ]
    }
    
    # Generate HTML report
    print("   📄 Generating HTML report...")
    report_gen = ReportGenerator()
    html_path = report_gen.generate_report('test_email', test_data, format='html')
    
    if not html_path:
        print("   ❌ Failed to generate HTML report")
        return False
    
    print(f"   ✅ HTML report created: {html_path}")
    
    # Generate PDF
    print("   📄 Converting to PDF...")
    pdf_path = report_gen.convert_html_to_pdf(html_path)
    
    if not pdf_path:
        print("   ❌ Failed to generate PDF")
        print("   Make sure Playwright is installed:")
        print("   pip install playwright")
        print("   playwright install chromium")
        return False
    
    print(f"   ✅ PDF created: {pdf_path}")
    
    # Send email
    print("   📧 Sending email...")
    alert_mgr = create_alert_manager(config.to_dict())
    
    report_summary = {
        'critical_issues': test_data['stats']['critical_issues'],
        'high_issues': test_data['stats']['high_issues'],
        'medium_issues': test_data['stats']['medium_issues'],
        'low_issues': test_data['stats']['low_issues'],
        'total_issues': test_data['stats']['total_issues'],
        'avg_response_time': test_data['stats']['avg_response_time'],
        'uptime_percentage': test_data['stats']['uptime_percentage'],
        'pages_checked': test_data['stats']['pages_checked']
    }
    
    email_result = alert_mgr.send_report_email(
        recipient_emails=recipients,
        pdf_path=pdf_path,
        report_summary=report_summary,
        website_name=test_data['stats']['website_name'],
        website_url=test_data['stats']['website_url']
    )
    
    if email_result.get('status') == 'success':
        print(f"\n✅ SUCCESS! Test email sent to:")
        for recipient in email_result.get('recipients', []):
            print(f"   ✉️  {recipient}")
        print("\n📬 Check your inbox for the test report!")
        return True
    else:
        print(f"\n❌ FAILED to send email")
        print(f"   Error: {email_result.get('message')}")
        return False


if __name__ == '__main__':
    print("\n")
    success = test_email_with_pdf()
    print("\n" + "=" * 60)
    if success:
        print("✅ EMAIL TEST COMPLETE - Configuration is working!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Check the recipient inbox")
        print("2. Verify PDF is attached and readable")
        print("3. Start the scheduler: python scheduler.py")
    else:
        print("❌ EMAIL TEST FAILED - Please fix the issues above")
        print("=" * 60)
        print("\nFor help, see: AUTOMATED_EMAIL_SETUP.md")
    print("\n")
