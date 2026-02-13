# ✅ Multi-Website Setup Complete!

## 🎉 **SUCCESS!** Both websites are now configured for monitoring!

---

## 🌐 **Your Monitored Websites**

### **Website 1: Nevas Technologies**
- ✅ URL: https://www.nevastech.com
- ✅ Schedule: **Daily at 4:30 PM**
- ✅ Email: renderthaniks@gmail.com, prabhu@nevastech.com
- ✅ Config: `config/config.yaml`
- ✅ Scheduler: `scheduler_nevastech.py`

### **Website 2: Ascent Innovation**  
- ✅ URL: https://www.ascent365.com
- ✅ Schedule: **Daily at 6:00 AM**
- ✅ Email: prabhuofficial2003@gmail.com
- ✅ Pages: `/`, `/about/`
- ✅ Config: `config/ascent365.yaml`
- ✅ Scheduler: `scheduler_ascent365.py`

---

## 🚀 **How to Start (3 Easy Steps)**

### **Step 1: Make sure your `.env` file has SMTP credentials**

Check file: `.env`

```env
SMTP_USERNAME=nevasai2025@gmail.com
SMTP_PASSWORD=your-gmail-app-password
```

### **Step 2: Start both schedulers**

**Option A: Start Both at Once (Recommended)**
```powershell
.\start_all_monitors.ps1
```

**Option B: Start Individually**
```powershell
# Terminal 1
python scheduler_nevastech.py

# Terminal 2 (separate window)
python scheduler_ascent365.py
```

### **Step 3: Done!**

Both schedulers are now running and will automatically:
- ✅ Check websites at scheduled times
- ✅ Generate reports  
- ✅ Send emails with PDF attachments

---

## 📧 **Email Delivery Schedule**

| Time | Website | Recipient |
|------|---------|-----------|
| **6:00 AM** | Ascent Innovation | prabhuofficial2003@gmail.com |
| **4:30 PM** | Nevas Technologies | renderthaniks@gmail.com<br>prabhu@nevastech.com |

---

## 📊 **What Each Email Contains**

✅ **Subject:** `🌐 Website Health Report — [Site Name] (2026-02-13)`

✅ **Body:** Beautiful HTML email with:
- Health Score (0-100)
- Issue Summary (Critical, High, Medium, Low)
- Performance metrics
- Uptime percentage

✅ **Attachment:** Full PDF report with all details

---

## 📁 **Files Created**

```
wordpress-monitor/
├── config/
│   ├── config.yaml              ← Nevastech config ✅
│   └── ascent365.yaml           ← Ascent365 config ✅ NEW
│
├── reports/
│   ├── (nevastech reports)
│   └── ascent365/               ← Ascent365 reports ✅ NEW
│
├── data/
│   ├── monitor.db               ← Nevastech DB
│   └── monitor_ascent365.db     ← Ascent365 DB ✅ NEW
│
├── logs/
│   ├── monitor.log
│   ├── scheduler.log
│   ├── ascent365.log            ← Ascent365 logs ✅ NEW
│   └── ascent365_scheduler.log  ← Ascent365 scheduler logs ✅ NEW
│
├── scheduler_nevastech.py       ← Nevastech scheduler ✅
├── scheduler_ascent365.py       ← Ascent365 scheduler ✅ NEW
├── start_all_monitors.ps1       ← Start both ✅ NEW
└── MULTI_SITE_QUICK_REFERENCE.md ← This guide ✅ NEW
```

---

## 🧪 **Test Before Scheduled Time**

Don't wait! Test both websites now:

### **Test Nevastech:**
```powershell
python -c "from main import WordPressMonitor; m = WordPressMonitor('config/config.yaml'); result = m.run_all_checks(); print('Report:', result.get('report_path'))"
```

### **Test Ascent365:**
```powershell
python -c "from main import WordPressMonitor; m = WordPressMonitor('config/ascent365.yaml'); result = m.run_all_checks(); print('Report:', result.get('report_path'))"
```

---

## 🛑 **How to Stop**

1. Go to each scheduler window
2. Press **Ctrl+C**
3. Scheduler stops gracefully

---

## ⚙️ **Need to Change Something?**

### **Change Schedule Time:**
Edit the config file:
- Nevastech: `config/config.yaml` → `check_time: "16:30"`
- Ascent365: `config/ascent365.yaml` → `check_time: "06:00"`

### **Change Email Recipients:**
Edit the config file:
- Nevastech: `config/config.yaml` → `recipients:` section
- Ascent365: `config/ascent365.yaml` → `recipients:` section

### **Add More Pages:**
Edit the config file:
- Ascent365: `config/ascent365.yaml` → `critical_pages:` section

**After any change, restart the scheduler!**

---

## 📖 **Documentation**

- **Quick Reference:** `MULTI_SITE_QUICK_REFERENCE.md`
- **Full Setup Guide:** `MULTI_WEBSITE_SETUP.md`
- **Troubleshooting:** See Quick Reference

---

## ✨ **Features (Both Websites)**

✅ Uptime monitoring  
✅ Broken link detection  
✅ Image monitoring (broken & slow)  
✅ Video monitoring (YouTube, Vimeo, HTML5)  
✅ SEO checks (meta tags, sitemaps, robots.txt)  
✅ Performance monitoring  
✅ Content checks  
✅ Beautiful PDF reports  
✅ Automatic email delivery  

---

## 🎯 **Success Checklist**

- [x] Website 1 (Nevastech) configured
- [x] Website 2 (Ascent365) configured
- [x] Separate schedulers created
- [x] Email recipients set
- [x] Schedule times set
- [x] Folders created
- [x] Documentation created
- [ ] **YOU:** Test both websites manually
- [ ] **YOU:** Start both schedulers
- [ ] **YOU:** Verify emails arrive

---

## 🚀 **Next Steps**

1. **Test both websites manually** (see commands above)
2. **Start both schedulers:**
   ```powershell
   .\start_all_monitors.ps1
   ```
3. **Wait for scheduled times and verify emails arrive**

---

**✅ Setup is COMPLETE! Your multi-website monitoring is ready!** 🎉

**Tomorrow:**
- 6:00 AM → Ascent365 report email 📧
- 4:30 PM → Nevastech report email 📧

**Both automatic. Zero manual work needed!** ✨
