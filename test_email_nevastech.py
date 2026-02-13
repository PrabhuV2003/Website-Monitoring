"""
Quick Email Test - Nevastech
Send a test email without running full website check
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.config_loader import ConfigLoader
from utils.alerts import create_alert_manager
from utils.reporting import ReportGenerator


def quick_test():
    """Quick email test without website check."""
    
    print("=" * 60)
    print(" QUICK EMAIL TEST - NEVASTECH")
    print("=" * 60)
    
    # Load config
    config = ConfigLoader('config/config.yaml')
    email_config = config.get('alerts', 'email', default={})
    
    print(f"\n Configuration:")
    print(f"   FROM: {email_config.get('smtp_username', 'Not set')}")
    print(f"   TO: {', '.join(email_config.get('recipients', []))}")
    
    # Check if credentials are set
    username = email_config.get('smtp_username', '')
    password = email_config.get('smtp_password', '')
    
    if not username or username == 'nevastech.monitor@gmail.com':
        print("\n DUMMY CREDENTIALS DETECTED")
        print("   Update config/config.yaml with real Gmail account")
        return False
    
    if not password or password == 'your-app-password-here':
        print("\n DUMMY PASSWORD DETECTED")
        print("   Update config/config.yaml with real App Password")
        return False
    
    print("\n Credentials configured")
    
    # Confirm
    response = input("\n Send test email now? (yes/no): ").strip().lower()
    if response not in ['yes', 'y']:
        print(" Cancelled")
        return False
    
    # Create dummy report
    print("\n Creating test report...")
    test_data = {
        'stats': {
            'website_url': 'https://www.nevastech.com',
            'website_name': 'Nevas Technologies',
            'critical_issues': 0,
            'high_issues': 1,
            'medium_issues': 2,
            'low_issues': 3,
            'total_issues': 6,
            'avg_response_time': 520,
            'uptime_percentage': 100.0,
            'pages_checked': 3
        },
        'issues': [
            {
                'severity': 'high',
                'message': 'Slow page load detected',
                'monitor': 'performance',
                'url': 'https://www.nevastech.com/',
                'details': {}
            }
        ]
    }
    
    report_gen = ReportGenerator()
    html_path = report_gen.generate_report('test', test_data, format='html')
    
    if not html_path:
        print(" Report generation failed")
        return False
    
    print(f" Report: {html_path}")
    
    # Generate PDF
    print(" Creating PDF...")
    pdf_path = report_gen.convert_html_to_pdf(html_path)
    
    if not pdf_path:
        print(" PDF generation failed")
        return False
    
    print(f" PDF: {pdf_path}")
    
    # Send email
    print(" Sending email...")
    alert_mgr = create_alert_manager(config.to_dict())
    
    email_result = alert_mgr.send_report_email(
        recipient_emails=email_config.get('recipients', []),
        pdf_path=pdf_path,
        report_summary=test_data['stats'],
        website_name='Nevas Technologies',
        website_url='https://www.nevastech.com'
    )
    
    print("\n" + "=" * 60)
    if email_result.get('status') == 'success':
        print(" SUCCESS! Email sent!")
        print("=" * 60)
        for r in email_result.get('recipients', []):
            print(f"     {r}")
        print("\n Check inbox for test email!")
        return True
    else:
        print(" FAILED!")
        print("=" * 60)
        print(f"Error: {email_result.get('message')}")
        print("\nPossible issues:")
        print("  1. Wrong Gmail credentials in config/config.yaml")
        print("  2. Wrong App Password (must be 16 chars from Gmail)")
        print("  3. 2-Step Verification not enabled")
        return False


if __name__ == '__main__':
    print("\n")
    success = quick_test()
    print("\n" + "=" * 60)
    if success:
        print(" EMAIL TEST PASSED")
    else:
        print(" EMAIL TEST FAILED")
    print("=" * 60)
    print("\n")
