# Deploy WordPress Monitor to Hostinger VPS

## 🚀 Complete Deployment Guide

This guide will help you deploy both website monitors (Nevastech & Ascent365) to your Hostinger VPS server so they run 24/7 automatically.

---

## 📋 **Prerequisites**

- ✅ Hostinger VPS with SSH access
- ✅ Ubuntu/Debian Linux (most Hostinger VPS use Ubuntu)
- ✅ Root or sudo access
- ✅ Gmail credentials configured in config files

---

## 🔧 **Step 1: Connect to Your VPS**

### **From Windows:**

```powershell
# Using PowerShell
ssh root@your-vps-ip-address

# Or if you have a username:
ssh username@your-vps-ip-address
```

**Example:**
```powershell
ssh root@192.168.1.100
# Enter password when prompted
```

---

## 📦 **Step 2: Install Dependencies on VPS**

Once connected to your VPS, run these commands:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+ and pip
sudo apt install python3 python3-pip python3-venv -y

# Install required system packages
sudo apt install git wget curl chromium-browser -y

# Verify Python version (needs 3.11+)
python3 --version
```

---

## 📁 **Step 3: Upload Project to VPS**

### **Option A: Using Git (Recommended)**

If your project is on GitHub:

```bash
# On VPS
cd /home
git clone https://github.com/your-username/wordpress-monitor.git
cd wordpress-monitor
```

### **Option B: Using SCP (From Windows)**

Upload from your Windows computer:

```powershell
# On your Windows machine
scp -r C:\Users\Nevas\.gemini\antigravity\scratch\wordpress-monitor root@your-vps-ip:/home/wordpress-monitor
```

### **Option C: Using FileZilla**

1. Download FileZilla: https://filezilla-project.org/
2. Connect to your VPS using SFTP
3. Upload the `wordpress-monitor` folder to `/home/`

---

## 🐍 **Step 4: Set Up Python Environment**

```bash
# On VPS, navigate to project
cd /home/wordpress-monitor

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
playwright install-deps
```

---

## ⚙️ **Step 5: Configure Environment Variables**

```bash
# Create/edit .env file
nano .env
```

**Make sure these are commented out:**
```env
# SMTP_USERNAME=
# SMTP_PASSWORD=
```

**Save and exit:** Ctrl+X, then Y, then Enter

---

## 🔒 **Step 6: Secure Config Files**

```bash
# Set proper permissions
chmod 600 config/config.yaml
chmod 600 config/ascent365.yaml
chmod 600 .env

# Create necessary directories
mkdir -p reports/ascent365
mkdir -p data
mkdir -p logs
```

---

## 🔄 **Step 7: Create Systemd Services**

These will make the schedulers run automatically and restart on failure.

### **Service 1: Nevastech Monitor**

```bash
sudo nano /etc/systemd/system/monitor-nevastech.service
```

**Paste this:**
```ini
[Unit]
Description=WordPress Monitor - Nevastech
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/wordpress-monitor
Environment="PATH=/home/wordpress-monitor/venv/bin"
ExecStart=/home/wordpress-monitor/venv/bin/python /home/wordpress-monitor/scheduler_nevastech.py
Restart=always
RestartSec=10
StandardOutput=append:/home/wordpress-monitor/logs/service-nevastech.log
StandardError=append:/home/wordpress-monitor/logs/service-nevastech-error.log

[Install]
WantedBy=multi-user.target
```

**Save:** Ctrl+X, Y, Enter

### **Service 2: Ascent365 Monitor**

```bash
sudo nano /etc/systemd/system/monitor-ascent365.service
```

**Paste this:**
```ini
[Unit]
Description=WordPress Monitor - Ascent365
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/wordpress-monitor
Environment="PATH=/home/wordpress-monitor/venv/bin"
ExecStart=/home/wordpress-monitor/venv/bin/python /home/wordpress-monitor/scheduler_ascent365.py
Restart=always
RestartSec=10
StandardOutput=append:/home/wordpress-monitor/logs/service-ascent365.log
StandardError=append:/home/wordpress-monitor/logs/service-ascent365-error.log

[Install]
WantedBy=multi-user.target
```

**Save:** Ctrl+X, Y, Enter

---

## ▶️ **Step 8: Start Services**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services to start on boot
sudo systemctl enable monitor-nevastech
sudo systemctl enable monitor-ascent365

# Start services now
sudo systemctl start monitor-nevastech
sudo systemctl start monitor-ascent365

# Check status
sudo systemctl status monitor-nevastech
sudo systemctl status monitor-ascent365
```

**You should see:** `Active: active (running)`

---

## 📊 **Step 9: Monitor & Verify**

### **Check Service Status:**
```bash
# Check if running
sudo systemctl status monitor-nevastech
sudo systemctl status monitor-ascent365
```

### **View Logs:**
```bash
# Real-time logs
tail -f /home/wordpress-monitor/logs/ascent365_scheduler.log

# Service logs
journalctl -u monitor-ascent365 -f
```

### **Check Scheduled Jobs:**
```bash
# View scheduler logs
cat /home/wordpress-monitor/logs/ascent365_scheduler.log
cat /home/wordpress-monitor/logs/scheduler.log
```

---

## 🛠️ **Useful Commands**

### **Start/Stop/Restart Services:**
```bash
# Start
sudo systemctl start monitor-nevastech
sudo systemctl start monitor-ascent365

# Stop
sudo systemctl stop monitor-nevastech
sudo systemctl stop monitor-ascent365

# Restart
sudo systemctl restart monitor-nevastech
sudo systemctl restart monitor-ascent365

# Check status
sudo systemctl status monitor-nevastech
sudo systemctl status monitor-ascent365
```

### **View Logs:**
```bash
# All Nevastech logs
tail -100 /home/wordpress-monitor/logs/scheduler.log

# All Ascent365 logs
tail -100 /home/wordpress-monitor/logs/ascent365_scheduler.log

# Service logs (last 50 lines)
sudo journalctl -u monitor-ascent365 -n 50

# Follow logs in real-time
sudo journalctl -u monitor-ascent365 -f
```

### **Update Configuration:**
```bash
# Edit config
nano /home/wordpress-monitor/config/ascent365.yaml

# After editing, restart service
sudo systemctl restart monitor-ascent365
```

---

## 🔐 **Security Best Practices**

### **1. Create Dedicated User:**
```bash
# Create monitor user
sudo useradd -m -s /bin/bash monitoruser

# Move project
sudo mv /home/wordpress-monitor /home/monitoruser/
sudo chown -R monitoruser:monitoruser /home/monitoruser/wordpress-monitor

# Update service files to use monitoruser instead of root
```

### **2. Firewall Setup:**
```bash
# If you need dashboard access
sudo ufw allow 5000/tcp  # For Nevastech dashboard
sudo ufw allow 5001/tcp  # For Ascent365 dashboard
sudo ufw enable
```

### **3. Secure Permissions:**
```bash
chmod 700 /home/wordpress-monitor
chmod 600 /home/wordpress-monitor/.env
chmod 600 /home/wordpress-monitor/config/*.yaml
```

---

## 📧 **Email Testing on VPS**

```bash
# Activate venv
cd /home/wordpress-monitor
source venv/bin/activate

# Test email
python test_email_ascent365.py
```

---

## ⚡ **Troubleshooting**

### **Service Won't Start:**
```bash
# Check service logs
sudo journalctl -u monitor-ascent365 -n 100

# Check Python errors
cat /home/wordpress-monitor/logs/service-ascent365-error.log

# Test manually
cd /home/wordpress-monitor
source venv/bin/activate
python scheduler_ascent365.py
```

### **PDF Generation Fails:**
```bash
# Install Chromium dependencies
sudo apt install -y \
    libnss3 \
    libxss1 \
    libasound2 \
    libxrandr2 \
    libatk1.0-0 \
    libgtk-3-0

# Reinstall Playwright
pip install --force-reinstall playwright
playwright install chromium
playwright install-deps
```

### **Email Not Sending:**
```bash
# Check network connectivity
ping smtp.gmail.com

# Check config
cat /home/wordpress-monitor/config/ascent365.yaml | grep smtp

# Test email manually
python test_email_ascent365.py
```

---

## 🔄 **Updating the Code**

### **If Using Git:**
```bash
cd /home/wordpress-monitor
git pull origin main
sudo systemctl restart monitor-nevastech
sudo systemctl restart monitor-ascent365
```

### **If Using SCP:**
```powershell
# From Windows
scp -r C:\Users\Nevas\.gemini\antigravity\scratch\wordpress-monitor\* root@your-vps-ip:/home/wordpress-monitor/

# Then on VPS
sudo systemctl restart monitor-nevastech
sudo systemctl restart monitor-ascent365
```

---

## 📊 **Dashboard Access (Optional)**

If you want to access the dashboard from anywhere:

### **1. Enable Dashboard in Configs:**

**Edit config/config.yaml:**
```yaml
dashboard:
  enabled: true
  host: "0.0.0.0"  # Listen on all interfaces
  port: 5000
```

**Edit config/ascent365.yaml:**
```yaml
dashboard:
  enabled: true
  host: "0.0.0.0"
  port: 5001
```

### **2. Open Firewall:**
```bash
sudo ufw allow 5000/tcp
sudo ufw allow 5001/tcp
```

### **3. Access Dashboards:**
- Nevastech: `http://your-vps-ip:5000`
- Ascent365: `http://your-vps-ip:5001`

---

## ✅ **Verification Checklist**

After deployment, verify:

- [ ] Both services running: `systemctl status monitor-nevastech monitor-ascent365`
- [ ] No errors in logs: `tail -100 /home/wordpress-monitor/logs/*.log`
- [ ] Test email sent successfully: `python test_email_ascent365.py`
- [ ] Services start on boot: `systemctl is-enabled monitor-nevastech`
- [ ] Scheduled jobs configured: Check logs for "Next run" messages
- [ ] Reports being generated: `ls -lh /home/wordpress-monitor/reports/`
- [ ] Emails arriving at correct times

---

## 🎯 **Quick Start Summary**

```bash
# 1. Connect to VPS
ssh root@your-vps-ip

# 2. Install dependencies
apt update && apt install python3 python3-pip python3-venv chromium-browser -y

# 3. Upload project (use SCP or Git)

# 4. Setup environment
cd /home/wordpress-monitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# 5. Create systemd services (see Step 7)

# 6. Start services
systemctl daemon-reload
systemctl enable monitor-nevastech monitor-ascent365
systemctl start monitor-nevastech monitor-ascent365

# 7. Verify
systemctl status monitor-nevastech monitor-ascent365
tail -f logs/ascent365_scheduler.log
```

---

## 📞 **Support & Maintenance**

### **Monthly Maintenance:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Update Python packages
cd /home/wordpress-monitor
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Restart services
sudo systemctl restart monitor-nevastech monitor-ascent365
```

### **Backup Important Files:**
```bash
# Backup configs
tar -czf monitor-backup-$(date +%Y%m%d).tar.gz \
  config/ \
  .env \
  data/

# Download backup to Windows
scp root@your-vps-ip:/home/wordpress-monitor/monitor-backup-*.tar.gz ./
```

---

**Your WordPress Monitor is now running 24/7 on your VPS!** 🎉

Both websites will be monitored automatically at their scheduled times, and emails will be sent with reports!
