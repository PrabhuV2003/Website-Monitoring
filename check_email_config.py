"""
Simple Email Test - No fancy output, just test functionality
"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.config_loader import ConfigLoader
from utils.alerts import create_alert_manager

print("=" * 60)
print("EMAIL CONFIGURATION TEST")
print("=" * 60)

# Load configuration
config = ConfigLoader('config/config.yaml')

# Check email configuration
email_config = config.get('alerts', 'email', default={})
enabled = email_config.get('enabled', False)
recipients = email_config.get('recipients', [])

print("\nEmail Settings:")
print(f"  Enabled: {enabled}")
print(f"  SMTP Server: {email_config.get('smtp_server', 'Not configured')}")
print(f"  SMTP Port: {email_config.get('smtp_port', 'Not configured')}")
print(f"  From Email: {email_config.get('from_email', 'Not configured')}")
print(f"  Recipients: {', '.join(recipients) if recipients else 'None configured'}")

# Check environment variables
smtp_user = os.getenv('SMTP_USERNAME') or email_config.get('smtp_username')
smtp_pass = os.getenv('SMTP_PASSWORD') or email_config.get('smtp_password')

print("\nEnvironment Variables:")
print(f"  SMTP_USERNAME: {'SET (' + smtp_user + ')' if smtp_user else 'NOT SET'}")
print(f"  SMTP_PASSWORD: {'SET (hidden)' if smtp_pass else 'NOT SET'}")

# Check if credentials are in config file
config_user = email_config.get('smtp_username')
config_pass = email_config.get('smtp_password')

if config_user and config_pass:
    print("\nCredentials Source: config.yaml")
else:
    print("\nCredentials Source: Environment Variables")

# Check if ready
if not enabled:
    print("\n[ERROR] Email is DISABLED in config.yaml")
    sys.exit(1)

if not recipients:
    print("\n[ERROR] No recipients configured")
    sys.exit(1)

if not smtp_user or not smtp_pass:
    print("\n[ERROR] SMTP credentials not set in environment variables")
    sys.exit(1)

print("\n[SUCCESS] Email configuration is complete!")
print("\nYou can now:")
print("  1. Run scheduler: python scheduler.py")
print("  2. It will automatically send PDF reports to:")
for r in recipients:
    print(f"     - {r}")

print("\n" + "=" * 60)
