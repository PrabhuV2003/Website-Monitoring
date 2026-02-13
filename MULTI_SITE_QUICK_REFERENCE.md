# Multi-Website Monitoring - Quick Reference
# ===========================================

## 🌐 Your Monitored Websites

### **Website 1: Nevas Technologies**
- **URL:** https://www.nevastech.com
- **Config:** `config/config.yaml`
- **Scheduler:** `scheduler_nevastech.py`
- **Schedule:** Daily at **4:30 PM** (Asia/Kolkata)
- **Email TO:** 
  - renderthaniks@gmail.com
  - prabhu@nevastech.com
- **Reports:** `reports/` folder
- **Database:** `data/monitor.db`
- **Logs:** `logs/monitor.log`, `logs/scheduler.log`

### **Website 2: Ascent Innovation**
- **URL:** https://www.ascent365.com
- **Config:** `config/ascent365.yaml`
- **Scheduler:** `scheduler_ascent365.py`
- **Schedule:** Daily at **6:00 AM** (Asia/Kolkata)
- **Email TO:** prabhuofficial2003@gmail.com
- **Pages Monitored:** `/`, `/about/`
- **Reports:** `reports/ascent365/` folder
- **Database:** `data/monitor_ascent365.db`
- **Logs:** `logs/ascent365.log`, `logs/ascent365_scheduler.log`

---

## 🚀 How to Start

### **Option 1: Start Both Websites (Recommended)**

```powershell
.\start_all_monitors.ps1
```

This opens **2 windows**:
- Window 1: Nevastech scheduler (4:30 PM)
- Window 2: Ascent365 scheduler (6:00 AM)

### **Option 2: Start Individually**

**Nevastech only:**
```powershell
python scheduler_nevastech.py
```

**Ascent365 only:**
```powershell
python scheduler_ascent365.py
```

---

## 📧 Email Schedule

| Time | Website | Recipients |
|------|---------|-----------|
| **6:00 AM** | Ascent365 | prabhuofficial2003@gmail.com |
| **4:30 PM** | Nevastech | renderthaniks@gmail.com, prabhu@nevastech.com |

Both send:
- ✅ Subject: `🌐 Website Health Report — [Site Name] (Date)`
- ✅ Professional HTML email with health score
- ✅ PDF attachment with full details

---

## 🧪 Manual Testing

### **Test Nevastech:**
```powershell
python -c "from main import WordPressMonitor; m = WordPressMonitor('config/config.yaml'); m.run_all_checks()"
```

### **Test Ascent365:**
```powershell
python -c "from main import WordPressMonitor; m = WordPressMonitor('config/ascent365.yaml'); m.run_all_checks()"
```

---

## 📁 File Structure

```
wordpress-monitor/
│
├── config/
│   ├── config.yaml           ← Nevastech config
│   └── ascent365.yaml        ← Ascent365 config
│
├── data/
│   ├── monitor.db            ← Nevastech database
│   └── monitor_ascent365.db  ← Ascent365 database
│
├── logs/
│   ├── monitor.log                ← Nevastech check logs
│   ├── scheduler.log              ← Nevastech scheduler logs
│   ├── ascent365.log              ← Ascent365 check logs
│   └── ascent365_scheduler.log    ← Ascent365 scheduler logs
│
├── reports/
│   ├── report_*.html/pdf          ← Nevastech reports
│   └── ascent365/
│       └── report_*.html/pdf      ← Ascent365 reports
│
├── scheduler_nevastech.py    ← Nevastech scheduler
├── scheduler_ascent365.py    ← Ascent365 scheduler
└── start_all_monitors.ps1    ← Start both at once
```

---

## 🛑 How to Stop

### **Stop Both:**
- Go to each scheduler window
- Press **Ctrl+C** in each window
- Both schedulers will stop gracefully

### **Stop One:**
- Find the window for that website
- Press **Ctrl+C**
- Only that scheduler stops

---

## 📊 View Reports

### **Nevastech Reports:**
- Open folder: `reports/`
- Files: `report_*.html` or `report_*.pdf`

### **Ascent365 Reports:**
- Open folder: `reports/ascent365/`
- Files: `report_*.html` or `report_*.pdf`

---

## ⚙️ Configuration Updates

### **Change Schedule Time:**

**Nevastech:** Edit `config/config.yaml`
```yaml
schedule:
  check_time: "16:30"  # Change to desired time (24-hour format)
```

**Ascent365:** Edit `config/ascent365.yaml`
```yaml
schedule:
  check_time: "06:00"  # Change to desired time (24-hour format)
```

After changing, **restart the scheduler**.

### **Change Email Recipients:**

**Nevastech:** Edit `config/config.yaml`
```yaml
alerts:
  email:
    recipients:
      - "new-email@example.com"
```

**Ascent365:** Edit `config/ascent365.yaml`
```yaml
alerts:
  email:
    recipients:
      - "prabhuofficial2003@gmail.com"
      - "another-email@example.com"  # Add more
```

### **Add More Pages:**

**Ascent365:** Edit `config/ascent365.yaml`
```yaml
critical_pages:
  - "/"
  - "/about/"
  - "/services/"  # Add new pages
  - "/contact/"
```

---

## 🔧 Troubleshooting

### **Email not sending?**
1. Check `.env` file has SMTP credentials:
   ```
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```
2. Gmail App Password required (not regular password)

### **Scheduler not running?**
1. Check Python is installed: `python --version`
2. Check dependencies: `pip install -r requirements.txt`
3. Check logs in `logs/` folder

### **Wrong schedule time?**
1. Edit config file (`check_time` field)
2. Restart scheduler
3. Check timezone is correct: `Asia/Kolkata`

---

## ✨ Features

### **Both Websites Monitor:**
- ✅ Uptime (site accessibility)
- ✅ Links (broken link detection)
- ✅ Images (broken & slow images)
- ✅ Videos (YouTube, Vimeo, HTML5)
- ✅ SEO (meta tags, sitemaps, robots.txt)
- ✅ Performance (response times)
- ✅ Content (mixed content, spell check)

### **Both Send:**
- ✅ Beautiful HTML email with health score
- ✅ PDF report with all details
- ✅ Issue breakdown (Critical, High, Medium, Low)
- ✅ Performance metrics
- ✅ Uptime percentage

---

## 📝 Daily Routine

**Every Day:**
1. **6:00 AM** - Ascent365 check runs automatically
   - Email sent to prabhuofficial2003@gmail.com
   
2. **4:30 PM** - Nevastech check runs automatically
   - Email sent to renderthaniks@gmail.com & prabhu@nevastech.com

**No manual intervention needed!** ✅

---

## 🎯 Quick Commands

| Task | Command |
|------|---------|
| Start both | `.\start_all_monitors.ps1` |
| Start Nevastech | `python scheduler_nevastech.py` |
| Start Ascent365 | `python scheduler_ascent365.py` |
| Test Nevastech | `python -c "from main import WordPressMonitor; m = WordPressMonitor('config/config.yaml'); m.run_all_checks()"` |
| Test Ascent365 | `python -c "from main import WordPressMonitor; m = WordPressMonitor('config/ascent365.yaml'); m.run_all_checks()"` |
| Stop | **Ctrl+C** in scheduler window |

---

**✅ Setup Complete! Both websites are now monitored automatically!** 🎉
