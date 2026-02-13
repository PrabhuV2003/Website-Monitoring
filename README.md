# WordPress Monitor
## Automated Website Monitoring Tool

A comprehensive Python-based monitoring tool for WordPress websites that performs daily checks for bugs, form issues, downtime, broken links, and other common problems.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## Features

### 🔍 **Uptime Monitoring**
- Website accessibility checks
- Response time measurement
- SSL certificate validation
- HTTP status code monitoring
- Automatic downtime alerts

### 📝 **Form Testing**
- Auto-detection of forms
- Form submission testing with Selenium
- Validation verification
- CAPTCHA detection
- Plugin compatibility checks

### 🔗 **Broken Link Detection**
- Async crawling for speed
- Internal and external link validation
- Redirect chain detection
- Image and media file checking
- Configurable depth and limits

### 🔒 **WordPress-Specific Checks**
- Core version detection
- Security vulnerability scanning
- Debug log exposure detection
- REST API verification
- Admin panel accessibility

### ⚡ **Performance Monitoring**
- Time to First Byte (TTFB)
- Google PageSpeed integration
- Console error detection
- Mixed content warnings
- Core Web Vitals (with Selenium)

### 📊 **Content Integrity**
- Hash-based change detection
- Broken image detection
- Navigation verification
- Suspicious content scanning

### 🎯 **SEO & Accessibility**
- Meta tag validation
- Sitemap verification
- robots.txt analysis
- Canonical tag checking
- Structured data detection

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Chrome browser (for Selenium features)

### Quick Start

```bash
# Clone or download the project
cd wordpress-monitor

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure your website
# Edit config/config.yaml with your website URL

# Run your first check
python main.py --url https://your-wordpress-site.com
```

## Configuration

Edit `config/config.yaml`:

```yaml
website:
  url: "https://yourwordpresssite.com"
  name: "My WordPress Site"

alerts:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    recipients:
      - "admin@example.com"
  
  slack:
    enabled: false
    webhook_url: ""  # Use SLACK_WEBHOOK_URL env var

critical_pages:
  - "/"
  - "/contact"
  - "/about"

thresholds:
  response_time_warning: 2000   # ms
  response_time_critical: 3000  # ms
  ssl_expiry_warning: 30        # days
  ssl_expiry_critical: 7        # days
```

### Environment Variables

Store sensitive data in environment variables:

```bash
# Email
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Integrations
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
PAGESPEED_API_KEY=your-google-api-key

# Database (if using MySQL)
DB_USERNAME=dbuser
DB_PASSWORD=dbpassword
```

## Usage

### Command Line Interface

```bash
# Full check
python cli.py check

# Quick uptime check
python cli.py check --quick

# Check specific URL
python cli.py check --url https://example.com

# View status
python cli.py status

# View broken links
python cli.py links

# Start dashboard
python cli.py dashboard

# Initialize new config
python cli.py init
```

### Direct Python

```python
from main import WordPressMonitor

monitor = WordPressMonitor("config/config.yaml")

# Full check
result = monitor.run_all_checks()
print(f"Found {result['total_issues']} issues")

# Quick check
result = monitor.run_quick_check()
```

### Scheduled Checks

```bash
# Run scheduler (checks based on config)
python scheduler.py

# Or use system scheduler:
# Windows Task Scheduler
# Linux: cron job
```

#### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at desired time
4. Action: Start a program
   - Program: `python.exe`
   - Arguments: `C:\path\to\wordpress-monitor\main.py`
   - Start in: `C:\path\to\wordpress-monitor`

#### Linux Cron

```bash
# Edit crontab
crontab -e

# Add daily check at 3 AM
0 3 * * * cd /path/to/wordpress-monitor && python main.py >> logs/cron.log 2>&1
```

## Dashboard

Start the web dashboard:

```bash
python cli.py dashboard --port 5000
```

Access at `http://localhost:5000`

Features:
- Real-time status overview
- Response time charts
- Recent check history
- Manual check trigger
- WebSocket updates

## Project Structure

```
wordpress-monitor/
├── config/
│   └── config.yaml          # Main configuration
├── monitors/
│   ├── __init__.py
│   ├── base_monitor.py      # Base class for monitors
│   ├── uptime_monitor.py    # Uptime and SSL checks
│   ├── form_tester.py       # Form testing
│   ├── link_checker.py      # Broken link detection
│   ├── wordpress_checker.py # WP-specific checks
│   ├── performance_monitor.py
│   ├── content_checker.py
│   └── seo_checker.py
├── utils/
│   ├── __init__.py
│   ├── config_loader.py     # Configuration management
│   ├── database.py          # SQLite/MySQL storage
│   ├── alerts.py            # Email/Slack/Discord alerts
│   ├── reporting.py         # HTML report generation
│   └── logger.py            # Logging setup
├── dashboard/
│   ├── app.py               # Flask dashboard
│   └── templates/
├── logs/                    # Log files
├── reports/                 # Generated reports
├── screenshots/             # Error screenshots
├── data/                    # SQLite database
├── main.py                  # Main application
├── cli.py                   # CLI interface
├── scheduler.py             # Automated scheduling
└── requirements.txt
```

## Alert Configuration

### Email (Gmail)

1. Enable 2-factor authentication
2. Create App Password: Google Account → Security → App Passwords
3. Use app password in config

### Slack

1. Create Slack App: api.slack.com/apps
2. Enable Incoming Webhooks
3. Add webhook to workspace
4. Copy webhook URL

### Discord

1. Server Settings → Integrations → Webhooks
2. Create webhook
3. Copy webhook URL

## Reports

Reports are generated in `reports/` directory:

- **HTML**: Beautiful, interactive reports
- **JSON**: Machine-readable data

Reports include:
- Issue summary by severity
- Performance metrics
- Broken links list
- Screenshots (if enabled)

## Troubleshooting

### Chrome/Selenium Issues

```bash
# Install webdriver-manager
pip install webdriver-manager

# Or disable Selenium features in config
```

### Permission Errors

```bash
# Run as administrator or fix permissions
chmod +x main.py
```

### Database Errors

```bash
# Reset database
rm data/monitor.db
python main.py  # Will recreate
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Adding New Monitor

1. Create `monitors/my_monitor.py`
2. Extend `BaseMonitor` class
3. Implement `name` property and `run()` method
4. Add to `monitors/__init__.py`
5. Add to `main.py` monitor list

## License

MIT License - See LICENSE file

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## Support

- Create an issue for bugs
- Check documentation for common problems
- Review logs in `logs/monitor.log`
