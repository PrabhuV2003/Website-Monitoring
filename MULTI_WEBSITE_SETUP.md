# Multi-Website Monitoring Setup

## 📋 **Overview**

You can monitor multiple websites by creating separate configuration files for each site.

### **What You'll Have:**

```
wordpress-monitor/
├── config/
│   ├── site1.yaml          # Website 1 config
│   ├── site2.yaml          # Website 2 config
│   └── config.yaml         # Default (backup)
├── scheduler_site1.py      # Scheduler for site 1
├── scheduler_site2.py      # Scheduler for site 2
└── main.py
```

---

## 🌐 **Website 1 Configuration**

### **Create:** `config/site1.yaml`

```yaml
# Website 1: Nevastech (Example)
website:
  name: "Nevastech"
  url: "https://www.nevastech.com"

# Critical pages to monitor
critical_pages:
  - "/"
  - "/about/"
  - "/services/"
  - "/contact/"

# Forms to test (Website 1 specific)
forms:
  - name: "Contact Form"
    url: "/contact/"
    fields:
      name: "John Doe"
      email: "test@example.com"
      message: "Test message"
    submit_button: "button[type='submit']"

# Link checker settings
link_checker:
  enabled: true
  max_links_per_page: 100
  timeout: 10

# Image checker settings
image_checker:
  enabled: true
  max_images_per_page: 50
  slow_threshold_ms: 3000

# Email settings for Website 1
alerts:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    smtp_username: "your-email@gmail.com"  # FROM email
    from_email: "your-email@gmail.com"
    recipients:
      - "client1@example.com"  # TO email for Website 1

# Report settings
reports:
  output_dir: "reports/site1"
  format: "html"
  pdf_enabled: true
  cleanup_after_days: 30

# Database
database:
  path: "data/monitor_site1.db"

# Logging
logging:
  file: "logs/site1.log"
  level: "INFO"
```

---

## 🌐 **Website 2 Configuration**

### **Create:** `config/site2.yaml`

```yaml
# Website 2: Another Site (Example)
website:
  name: "My Second Website"
  url: "https://www.example2.com"

# Critical pages (different from site 1)
critical_pages:
  - "/"
  - "/products/"
  - "/pricing/"
  - "/support/"
  - "/blog/"

# Forms to test (Website 2 specific)
forms:
  - name: "Newsletter Signup"
    url: "/"
    fields:
      email: "newsletter@test.com"
    submit_button: "#subscribe-button"
  
  - name: "Support Ticket"
    url: "/support/"
    fields:
      subject: "Test Support Request"
      description: "Testing support form"
      email: "support@test.com"
    submit_button: ".submit-ticket"

# Link checker (different settings)
link_checker:
  enabled: true
  max_links_per_page: 50
  timeout: 15

# Image checker
image_checker:
  enabled: true
  max_images_per_page: 75
  slow_threshold_ms: 4000

# Email settings for Website 2 (DIFFERENT recipients)
alerts:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    smtp_username: "your-email@gmail.com"  # Same FROM or different
    from_email: "your-email@gmail.com"
    recipients:
      - "client2@example.com"  # TO email for Website 2
      - "manager2@example.com"  # Multiple recipients

# Report settings (separate folder)
reports:
  output_dir: "reports/site2"
  format: "html"
  pdf_enabled: true
  cleanup_after_days: 30

# Database (separate database)
database:
  path: "data/monitor_site2.db"

# Logging (separate log file)
logging:
  file: "logs/site2.log"
  level: "INFO"
```

---

## ⏰ **Scheduler for Website 1**

### **Create:** `scheduler_site1.py`

```python
"""
Scheduler for Website 1
Runs at 10:00 AM daily
"""
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import scheduler module
from scheduler import run_scheduler

if __name__ == "__main__":
    # Use site1 config
    run_scheduler(config_path="config/site1.yaml")
```

### **Schedule:** Daily at **10:00 AM**

Edit `config/site1.yaml` and add:

```yaml
# Scheduler settings for Website 1
scheduler:
  enabled: true
  schedule: "0 10 * * *"  # 10:00 AM daily
  timezone: "Asia/Kolkata"
```

---

## ⏰ **Scheduler for Website 2**

### **Create:** `scheduler_site2.py`

```python
"""
Scheduler for Website 2
Runs at 2:00 PM daily
"""
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import scheduler module
from scheduler import run_scheduler

if __name__ == "__main__":
    # Use site2 config
    run_scheduler(config_path="config/site2.yaml")
```

### **Schedule:** Daily at **2:00 PM**

Edit `config/site2.yaml` and add:

```yaml
# Scheduler settings for Website 2
scheduler:
  enabled: true
  schedule: "0 14 * * *"  # 2:00 PM daily
  timezone: "Asia/Kolkata"
```

---

## 🚀 **How to Run**

### **Option 1: Run Both Schedulers Together (Recommended)**

Create a master script `start_all_schedulers.ps1`:

```powershell
# Start both schedulers at once
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python scheduler_site1.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python scheduler_site2.py"

Write-Host "Both schedulers started!" -ForegroundColor Green
Write-Host "Site 1: Runs daily at 10:00 AM" -ForegroundColor Cyan
Write-Host "Site 2: Runs daily at 2:00 PM" -ForegroundColor Cyan
```

**Run:**
```powershell
.\start_all_schedulers.ps1
```

### **Option 2: Run Individually**

**Terminal 1:** Website 1
```powershell
python scheduler_site1.py
```

**Terminal 2:** Website 2
```powershell
python scheduler_site2.py
```

---

## 📧 **Email Delivery**

### **Website 1:**
- **Time:** 10:00 AM daily
- **From:** `your-email@gmail.com`
- **To:** `client1@example.com`
- **Subject:** `🌐 Website Health Report — Nevastech (2026-02-13)`
- **Report:** `reports/site1/report_XXX.pdf`

### **Website 2:**
- **Time:** 2:00 PM daily
- **From:** `your-email@gmail.com`
- **To:** `client2@example.com`, `manager2@example.com`
- **Subject:** `🌐 Website Health Report — My Second Website (2026-02-13)`
- **Report:** `reports/site2/report_XXX.pdf`

---

## 🔧 **Manual Checks**

Run checks manually for each site:

### **Website 1:**
```powershell
python -c "from main import WordPressMonitor; m = WordPressMonitor('config/site1.yaml'); m.run_all_checks()"
```

### **Website 2:**
```powershell
python -c "from main import WordPressMonitor; m = WordPressMonitor('config/site2.yaml'); m.run_all_checks()"
```

---

## 📁 **Folder Structure**

```
wordpress-monitor/
├── config/
│   ├── site1.yaml         ← Website 1 config
│   ├── site2.yaml         ← Website 2 config
│
├── data/
│   ├── monitor_site1.db   ← Website 1 database
│   ├── monitor_site2.db   ← Website 2 database
│
├── logs/
│   ├── site1.log          ← Website 1 logs
│   ├── site2.log          ← Website 2 logs
│
├── reports/
│   ├── site1/             ← Website 1 reports
│   │   ├── report_XXX.html
│   │   ├── report_XXX.pdf
│   │
│   ├── site2/             ← Website 2 reports
│       ├── report_XXX.html
│       ├── report_XXX.pdf
│
├── scheduler_site1.py     ← Scheduler for site 1
├── scheduler_site2.py     ← Scheduler for site 2
└── start_all_schedulers.ps1  ← Start both at once
```

---

## ✅ **Setup Checklist**

- [ ] Create `config/site1.yaml` with Website 1 details
- [ ] Create `config/site2.yaml` with Website 2 details
- [ ] Create `scheduler_site1.py`
- [ ] Create `scheduler_site2.py`
- [ ] Create `start_all_schedulers.ps1`
- [ ] Test Website 1 manually
- [ ] Test Website 2 manually
- [ ] Start both schedulers
- [ ] Verify emails arrive at correct times

---

## 🎯 **Quick Start**

I'll create all the files for you! Just tell me:

1. **Website 1:**
   - URL: ?
   - Name: ?
   - Email TO: ?
   - Schedule time: ?
   - Forms to test: ?

2. **Website 2:**
   - URL: ?
   - Name: ?
   - Email TO: ?
   - Schedule time: ?
   - Forms to test: ?

I'll generate all the config files and schedulers for you! 🚀
