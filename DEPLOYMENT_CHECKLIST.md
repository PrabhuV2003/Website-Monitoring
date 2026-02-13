# VPS Deployment Quick Checklist

## ✅ Pre-Deployment Checklist (Do on Windows)

- [ ] Test monitor locally: `python cli.py check --browser --headless`
- [ ] Verify email works: `python test_email.py`
- [ ] Configure `config/config.yaml` with correct schedule
- [ ] Create `.env` file with SMTP credentials
- [ ] Have VPS IP, username, password ready
- [ ] Download WinSCP: https://winscp.net/ (for easy file upload)

---

## 🚀 VPS Setup Checklist (Do on VPS)

### **Phase 1: Initial Setup (15 min)**
- [ ] Connect to VPS via SSH
- [ ] Update system: `sudo apt update && sudo apt upgrade -y`
- [ ] Install Python: `sudo apt install -y python3 python3-pip python3-venv git`
- [ ] Install Playwright deps: (see full command in VPS_DEPLOYMENT.md)
- [ ] Create user: `sudo adduser wpmonitor`
- [ ] Switch to user: `su - wpmonitor`

### **Phase 2: Upload Project (10 min)**
- [ ] Upload files via WinSCP or SCP
- [ ] Create folder: `mkdir ~/wordpress-monitor`
- [ ] Navigate: `cd ~/wordpress-monitor`
- [ ] Verify files uploaded: `ls -la`

### **Phase 3: Install Dependencies (10 min)**
- [ ] Create venv: `python3 -m venv venv`
- [ ] Activate: `source venv/bin/activate`
- [ ] Install packages: `pip install -r requirements.txt`
- [ ] Install Playwright: `playwright install chromium`
- [ ] Install browser deps: `playwright install-deps chromium`

### **Phase 4: Configuration (5 min)**
- [ ] Copy .env file or create: `nano .env`
- [ ] Add SMTP credentials
- [ ] Verify config.yaml: `nano config/config.yaml`
- [ ] Check schedule time is correct

### **Phase 5: Test (5 min)**
- [ ] Run manual check: `python cli.py check --browser --headless`
- [ ] Verify PDF created: `ls reports/`
- [ ] Verify email sent
- [ ] Check logs: `tail logs/monitor.log`

### **Phase 6: Create Service (10 min)**
- [ ] Create service file: `sudo nano /etc/systemd/system/wordpress-monitor.service`
- [ ] Copy service configuration (from VPS_DEPLOYMENT.md)
- [ ] Reload systemd: `sudo systemctl daemon-reload`
- [ ] Enable service: `sudo systemctl enable wordpress-monitor`
- [ ] Start service: `sudo systemctl start wordpress-monitor`
- [ ] Check status: `sudo systemctl status wordpress-monitor`

### **Phase 7: Verify (5 min)**
- [ ] Service is running: Green "active (running)"
- [ ] View logs: `tail -f ~/wordpress-monitor/logs/scheduler.log`
- [ ] Wait for next scheduled run
- [ ] Reboot test: `sudo reboot` then reconnect and check

---

## 🎯 Essential Commands Reference

```bash
# Service Management
sudo systemctl start wordpress-monitor    # Start
sudo systemctl stop wordpress-monitor     # Stop
sudo systemctl restart wordpress-monitor  # Restart
sudo systemctl status wordpress-monitor   # Status

# View Logs
tail -f ~/wordpress-monitor/logs/scheduler.log  # Live logs

# Manual Check
cd ~/wordpress-monitor
source venv/bin/activate
python cli.py check --browser --headless
```

---

## ⚡ Quick Upload (Windows to VPS)

### **Using WinSCP:**
1. Open WinSCP
2. Enter VPS IP, username: `wpmonitor`, password
3. Drag entire `wordpress-monitor` folder from local to `/home/wpmonitor/`

### **Using Command Line:**
```powershell
cd C:\Users\Nevas\.gemini\antigravity\scratch\wordpress-monitor
scp -r * wpmonitor@YOUR_VPS_IP:/home/wpmonitor/wordpress-monitor/
```

---

## 🐛 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Service won't start | Check logs: `journalctl -u wordpress-monitor` |
| Browser not found | `playwright install chromium` |
| Permission denied | `chmod +x scheduler.py` |
| Email fails | Verify `.env` file: `cat .env` |

---

## 📊 Expected Timeline

| Phase | Time | Cumulative |
|-------|------|------------|
| VPS Setup | 15 min | 15 min |
| Upload Files | 10 min | 25 min |
| Install Deps | 10 min | 35 min |
| Configure | 5 min | 40 min |
| Test | 5 min | 45 min |
| Create Service | 10 min | 55 min |
| Verify | 5 min | **60 min** |

**Total Time: ~1 hour**

---

## ✅ Success Criteria

After deployment, you should have:

1. ✅ Service running: `sudo systemctl status wordpress-monitor` shows green
2. ✅ Logs active: `tail ~/wordpress-monitor/logs/scheduler.log` shows activity
3. ✅ Auto-start enabled: Service starts after reboot
4. ✅ Email working: Test email received
5. ✅ Reports generating: Files appear in `reports/` folder

---

## 🔗 Helpful Links

- **WinSCP Download**: https://winscp.net/
- **PuTTY Download**: https://www.putty.org/
- **Hostinger VPS Guide**: https://www.hostinger.com/tutorials/vps
- **Full Deployment Guide**: See `VPS_DEPLOYMENT.md`

---

**Ready to deploy? Follow VPS_DEPLOYMENT.md for detailed instructions!** 🚀
