# VPS Deployment - Quick Reference

## 🚀 **Quick Deploy Steps**

### **1. Connect to VPS**
```bash
ssh root@your-vps-ip
```

### **2. Install Dependencies**
```bash
apt update && apt install python3 python3-pip python3-venv chromium-browser git -y
```

### **3. Upload Project**
```bash
# Option A: From Windows using SCP
scp -r C:\Users\Nevas\.gemini\antigravity\scratch\wordpress-monitor root@your-vps-ip:/home/

# Option B: On VPS using Git
cd /home
git clone your-repo-url wordpress-monitor
```

### **4. Setup Python**
```bash
cd /home/wordpress-monitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
playwright install-deps
```

### **5. Create Services**

**Nevastech Service:**
```bash
sudo nano /etc/systemd/system/monitor-nevastech.service
```
Paste from DEPLOY_TO_VPS.md Step 7

**Ascent365 Service:**
```bash
sudo nano /etc/systemd/system/monitor-ascent365.service
```
Paste from DEPLOY_TO_VPS.md Step 7

### **6. Start Everything**
```bash
sudo systemctl daemon-reload
sudo systemctl enable monitor-nevastech monitor-ascent365
sudo systemctl start monitor-nevastech monitor-ascent365
sudo systemctl status monitor-nevastech monitor-ascent365
```

---

## 📊 **Daily Commands**

### **Check Status:**
```bash
sudo systemctl status monitor-nevastech
sudo systemctl status monitor-ascent365
```

### **View Logs:**
```bash
# Scheduler logs
tail -f /home/wordpress-monitor/logs/ascent365_scheduler.log

# Service logs
journalctl -u monitor-ascent365 -f
```

### **Restart Services:**
```bash
sudo systemctl restart monitor-nevastech
sudo systemctl restart monitor-ascent365
```

---

## 🔧 **Troubleshooting**

### **Service Won't Start:**
```bash
journalctl -u monitor-ascent365 -n 100
cat /home/wordpress-monitor/logs/service-ascent365-error.log
```

### **Test Manually:**
```bash
cd /home/wordpress-monitor
source venv/bin/activate
python scheduler_ascent365.py
```

### **Check Email:**
```bash
cd /home/wordpress-monitor
source venv/bin/activate
python test_email_ascent365.py
```

---

## 📁 **File Locations**

| File | Path |
|------|------|
| Project | `/home/wordpress-monitor/` |
| Configs | `/home/wordpress-monitor/config/` |
| Logs | `/home/wordpress-monitor/logs/` |
| Reports | `/home/wordpress-monitor/reports/` |
| Services | `/etc/systemd/system/monitor-*.service` |

---

## ⚡ **Quick Actions**

| Task | Command |
|------|---------|
| Start services | `systemctl start monitor-nevastech monitor-ascent365` |
| Stop services | `systemctl stop monitor-nevastech monitor-ascent365` |
| Restart services | `systemctl restart monitor-nevastech monitor-ascent365` |
| Check status | `systemctl status monitor-nevastech` |
| View logs | `tail -f logs/ascent365_scheduler.log` |
| Edit config | `nano config/ascent365.yaml` |
| Test email | `python test_email_ascent365.py` |

---

**Full guide:** See `DEPLOY_TO_VPS.md`
