# Automated Email with PDF Reports - Setup Guide

## Overview
The WordPress Monitor now **automatically sends PDF reports via email** to configured clients after each scheduled monitoring check completes.

## Features
✅ Automatic PDF generation after each check  
✅ Professional HTML email with health score summary  
✅ PDF report attached to email  
✅ Sends to multiple recipients  
✅ Configurable schedule (daily, hourly, custom)  

---

## Configuration

### 1. Email Settings (Required)

Edit `config/config.yaml` and configure the email settings:

```yaml
# Alert Configuration
alerts:
  email:
    enabled: true  # MUST be true for auto-email to work
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    smtp_username: ""  # Set via environment variable SMTP_USERNAME
    smtp_password: ""  # Set via environment variable SMTP_PASSWORD
    from_email: "monitor@yourcompany.com"
    recipients:  # Add your client email addresses here
      - "client@example.com"
      - "manager@example.com"
      - "support@yourcompany.com"
```

### 2. SMTP Credentials (Environment Variables)

Set your SMTP credentials as environment variables (recommended for security):

**For Gmail:**
1. Enable 2-Step Verification in your Google Account
2. Go to: Google Account → Security → 2-Step Verification → App passwords
3. Generate an app password for "Mail"
4. Set the environment variables:

```bash
# Windows PowerShell
$env:SMTP_USERNAME = "your-email@gmail.com"
$env:SMTP_PASSWORD = "your-app-password"

# Windows Command Prompt
set SMTP_USERNAME=your-email@gmail.com
set SMTP_PASSWORD=your-app-password

# Linux/Mac
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"
```

**For Other Email Providers:**
- **Outlook/Office 365**: Use `smtp.office365.com` port `587`
- **Yahoo**: Use `smtp.mail.yahoo.com` port `587`
- **Custom SMTP**: Configure your server details

### 3. Schedule Configuration

Set when the automated checks should run:

```yaml
schedule:
  check_interval: "daily"  # Options: daily, hourly, or cron expression
  check_time: "11:07"      # Time in 24-hour format (HH:MM)
  timezone: "Asia/Kolkata" # Your timezone
```

**Examples:**
- Daily at 3 AM: `check_interval: "daily"`, `check_time: "03:00"`
- Every hour: `check_interval: "hourly"`
- Every 30 minutes: `check_interval: "*/30"`
- Custom cron: `check_interval: "0 */6 * * *"` (every 6 hours)

---

## How It Works

### Workflow
1. **Scheduled Check Runs** → Monitor scans the website
2. **HTML Report Generated** → Creates detailed report
3. **PDF Created** → Converts HTML to professional PDF
4. **Email Sent** → PDF attached and sent to all recipients

### What the Email Contains
- **Subject**: `🌐 Website Health Report — [Site Name] (Date)`
- **Health Score**: 0-100 score with emoji indicator (🟢🟡🟠🔴)
- **Issue Summary**: Count of Critical, High, Medium, Low issues
- **Performance Metrics**: Response time, uptime, pages checked
- **PDF Attachment**: Full detailed report

---

## Running the Scheduler

### Start the Scheduler

```bash
# Windows
python scheduler.py

# Or using the batch file
monitor.bat
```

The scheduler will:
- Run an initial check (optional, currently commented out)
- Schedule recurring checks based on your configuration
- Automatically send email with PDF after each check
- Log all activities to `logs/scheduler.log`

### Monitor Logs

```bash
# View scheduler logs
type logs\scheduler.log

# Real-time log monitoring (Windows PowerShell)
Get-Content logs\scheduler.log -Wait -Tail 50
```

---

## Verification Checklist

Before running, verify:

- [ ] `alerts.email.enabled: true` in `config.yaml`
- [ ] `alerts.email.recipients` has at least one email address
- [ ] `SMTP_USERNAME` environment variable is set
- [ ] `SMTP_PASSWORD` environment variable is set
- [ ] `schedule.check_time` is configured
- [ ] PDF dependencies installed: `pip install playwright` + `playwright install chromium`

---

## Testing

### Test Manual Email (Without Scheduler)

```python
from main import WordPressMonitor
from utils.reporting import ReportGenerator
from utils.alerts import create_alert_manager
from utils.config_loader import ConfigLoader

# Run a check
monitor = WordPressMonitor('config/config.yaml')
result = monitor.run_all_checks()

# Generate PDF
report_gen = ReportGenerator()
pdf_path = report_gen.convert_html_to_pdf(result['report_path'])

# Send email
config = ConfigLoader('config/config.yaml')
alert_mgr = create_alert_manager(config.to_dict())
email_result = alert_mgr.send_report_email(
    recipient_emails=['test@example.com'],
    pdf_path=pdf_path,
    report_summary={
        'critical_issues': result['critical_issues'],
        'high_issues': result['high_issues'],
        'medium_issues': result['medium_issues'],
        'low_issues': result['low_issues'],
    },
    website_name=config.get('website', 'name'),
    website_url=config.get_website_url()
)

print(email_result)
```

---

## Troubleshooting

### ❌ Email Not Sending

**Check:**
1. `alerts.email.enabled: true` in config?
2. Environment variables set? Run: `echo $env:SMTP_USERNAME` (PowerShell)
3. Correct SMTP server and port?
4. Using Gmail? Must use App Password, not regular password
5. Check logs: `logs/scheduler.log` for error messages

### ❌ PDF Not Generating

**Check:**
1. Playwright installed? Run: `pip install playwright`
2. Chromium installed? Run: `playwright install chromium`
3. Check logs for PDF generation errors
4. Verify HTML report is created first in `reports/` folder

### ❌ No Recipients Configured

**Fix:**
Add email addresses to `config.yaml`:
```yaml
alerts:
  email:
    recipients:
      - "client@example.com"
```

---

## Example Log Output (Success)

```
2026-02-12 11:07:00 - INFO - Starting scheduled check at 2026-02-12 11:07:00
2026-02-12 11:07:15 - INFO - Check completed: 3 issues found
2026-02-12 11:07:15 - INFO - Report generated: reports/report_chk_20260212_110700_abc123.html
2026-02-12 11:07:18 - INFO - PDF generated: reports/report_chk_20260212_110700_abc123.pdf
2026-02-12 11:07:22 - INFO - Report PDF emailed successfully to: client@example.com, manager@example.com
```

---

## Security Best Practices

1. **Never commit credentials** to config.yaml
2. **Use environment variables** for SMTP credentials
3. **Use App Passwords** for Gmail (not your main password)
4. **Restrict recipient list** to authorized personnel only
5. **Review logs regularly** for failed delivery attempts

---

## Next Steps

1. ✅ Configure email settings in `config.yaml`
2. ✅ Set SMTP environment variables
3. ✅ Test with a manual check first
4. ✅ Start the scheduler: `python scheduler.py`
5. ✅ Verify email delivery
6. ✅ Set up as a Windows Service (optional, for 24/7 operation)

---

## Support

For issues:
- Check `logs/scheduler.log` for errors
- Verify SMTP settings with your email provider
- Test email manually using the test script above
- Ensure all dependencies are installed: `pip install -r requirements.txt`

**Ready to go!** 🚀 Your clients will now receive automated PDF reports after each monitoring check.
