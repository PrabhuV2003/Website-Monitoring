# Deploying WordPress Monitor to Hostinger VPS

## 🎯 Complete Step-by-Step Deployment Guide

---

## 📋 **VPS Requirements**

### **Minimum Specifications:**
| Requirement | Minimum | Recommended |
|------------|---------|-------------|
| **RAM** | 1 GB | 2 GB or more |
| **CPU** | 1 Core | 2 Cores |
| **Storage** | 10 GB | 20 GB |
| **OS** | Ubuntu 20.04+ | Ubuntu 22.04 LTS |
| **Bandwidth** | 1 TB/month | Unlimited |

### **Why These Requirements?**
- **RAM**: Headless browser needs ~500 MB during checks
- **Storage**: For logs, reports, screenshots
- **OS**: Ubuntu for compatibility with Playwright

---

## 🚀 **STEP-BY-STEP DEPLOYMENT**

---

### **STEP 1: Connect to Your VPS**

#### **Get Your VPS Details from Hostinger:**
- IP Address (e.g., `123.45.67.89`)
- Username (usually `root`)
- Password or SSH key

#### **Connect via SSH:**

**Windows (PowerShell):**
```powershell
ssh root@YOUR_VPS_IP
# Enter password when prompted
```

**Or use PuTTY:**
- Download: https://www.putty.org/
- Enter IP address
- Click "Open"
- Login with credentials

---

### **STEP 2: Update System & Install Prerequisites**

Once connected, run these commands:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.10+ and pip
sudo apt install -y python3 python3-pip python3-venv

# Install Git
sudo apt install -y git

# Install system dependencies for Playwright
sudo apt install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2

# Verify Python version (should be 3.8+)
python3 --version
```

---

### **STEP 3: Create a Dedicated User (Security Best Practice)**

```bash
# Create a user for the monitor
sudo adduser wpmonitor
# Enter password when prompted

# Add to sudo group (optional, for admin tasks)
sudo usermod -aG sudo wpmonitor

# Switch to the new user
su - wpmonitor
```

---

### **STEP 4: Upload Your Project to VPS**

#### **Option A: Using Git (Recommended if you have a repo)**

```bash
# Clone your repository
cd ~
git clone https://github.com/yourusername/wordpress-monitor.git
cd wordpress-monitor
```

#### **Option B: Manual Upload via SCP (Your Current Method)**

**From your Windows machine:**

```powershell
# Navigate to your project folder
cd C:\Users\Nevas\.gemini\antigravity\scratch\wordpress-monitor

# Upload to VPS (replace YOUR_VPS_IP)
scp -r * wpmonitor@YOUR_VPS_IP:/home/wpmonitor/wordpress-monitor/
```

**Or use WinSCP (GUI tool):**
1. Download: https://winscp.net/
2. Connect to your VPS
3. Drag & drop your entire `wordpress-monitor` folder

#### **Option C: Create Project Folder and Upload Manually**

On VPS:
```bash
# Create project directory
mkdir -p ~/wordpress-monitor
cd ~/wordpress-monitor
```

Then upload files using WinSCP or SCP.

---

### **STEP 5: Install Python Dependencies**

```bash
# Navigate to project directory
cd ~/wordpress-monitor

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Install Playwright system dependencies
playwright install-deps chromium
```

---

### **STEP 6: Configure Environment Variables**

```bash
# Create .env file
nano .env
```

**Add your credentials:**
```env
# SMTP Configuration (Required for email reports)
SMTP_USERNAME=nevasai2025@gmail.com
SMTP_PASSWORD=your-gmail-app-password-here

# Dashboard secret key
DASHBOARD_SECRET_KEY=your-random-secret-key-here

# Optional configurations
PAGESPEED_API_KEY=
SLACK_WEBHOOK_URL=
DISCORD_WEBHOOK_URL=
```

**Save and exit:** Press `Ctrl+X`, then `Y`, then `Enter`

---

### **STEP 7: Configure config.yaml**

```bash
# Edit configuration
nano config/config.yaml
```

**Verify/update these settings:**
```yaml
schedule:
  check_interval: "daily"
  check_time: "03:00"      # 3 AM daily (adjust as needed)
  timezone: "Asia/Kolkata"

alerts:
  email:
    enabled: true
    recipients:
      - "nevasai2025@gmail.com"
      - "client@example.com"

# Make sure browser is enabled for comprehensive checks
```

**Save and exit:** `Ctrl+X`, `Y`, `Enter`

---

### **STEP 8: Test the Setup**

```bash
# Activate virtual environment (if not already)
source ~/wordpress-monitor/venv/bin/activate

# Run a manual check to verify everything works
python cli.py check --browser --headless

# If successful, you should see the check running
# Wait for it to complete and verify:
# - PDF generated in reports/
# - Email sent (if configured)
```

**Expected output:**
```
✓ All checks completed
✓ Report generated: reports/report_xxxxx.html
✓ PDF created: reports/report_xxxxx.pdf
✓ Email sent to: nevasai2025@gmail.com
```

---

### **STEP 9: Create Systemd Service (Auto-Start on Boot)**

This makes the scheduler run automatically and restart if it crashes.

```bash
# Create service file
sudo nano /etc/systemd/system/wordpress-monitor.service
```

**Paste this configuration:**
```ini
[Unit]
Description=WordPress Monitor Scheduler
After=network.target

[Service]
Type=simple
User=wpmonitor
WorkingDirectory=/home/wpmonitor/wordpress-monitor
Environment="PATH=/home/wpmonitor/wordpress-monitor/venv/bin"
ExecStart=/home/wpmonitor/wordpress-monitor/venv/bin/python scheduler.py
Restart=always
RestartSec=10
StandardOutput=append:/home/wpmonitor/wordpress-monitor/logs/service.log
StandardError=append:/home/wpmonitor/wordpress-monitor/logs/service-error.log

[Install]
WantedBy=multi-user.target
```

**Save and exit:** `Ctrl+X`, `Y`, `Enter`

---

### **STEP 10: Enable and Start the Service**

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable wordpress-monitor

# Start the service now
sudo systemctl start wordpress-monitor

# Check service status
sudo systemctl status wordpress-monitor
```

**You should see:**
```
● wordpress-monitor.service - WordPress Monitor Scheduler
   Loaded: loaded (/etc/systemd/system/wordpress-monitor.service; enabled)
   Active: active (running) since Wed 2026-02-12 15:00:00 IST
```

---

### **STEP 11: Verify It's Running**

```bash
# View live logs
tail -f ~/wordpress-monitor/logs/scheduler.log

# You should see:
# "Starting WordPress Monitor Scheduler"
# "Scheduler started and running..."
# "Next run at: [scheduled time]"
```

Press `Ctrl+C` to stop viewing logs (service keeps running).

---

### **STEP 12: Configure Firewall (Optional but Recommended)**

```bash
# Install UFW firewall
sudo apt install -y ufw

# Allow SSH (IMPORTANT - do this first!)
sudo ufw allow 22/tcp

# Allow dashboard if you want web access (optional)
sudo ufw allow 5000/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

## 🎯 **MANAGEMENT COMMANDS**

### **View Service Status**
```bash
sudo systemctl status wordpress-monitor
```

### **Stop the Scheduler**
```bash
sudo systemctl stop wordpress-monitor
```

### **Start the Scheduler**
```bash
sudo systemctl start wordpress-monitor
```

### **Restart the Scheduler**
```bash
sudo systemctl restart wordpress-monitor
```

### **View Logs**
```bash
# Live logs (Ctrl+C to exit)
tail -f ~/wordpress-monitor/logs/scheduler.log

# Last 50 lines
tail -n 50 ~/wordpress-monitor/logs/scheduler.log

# Service logs
journalctl -u wordpress-monitor -f
```

### **Disable Auto-Start (if needed)**
```bash
sudo systemctl disable wordpress-monitor
```

---

## 📊 **MONITORING & MAINTENANCE**

### **Check Disk Space**
```bash
df -h
```

### **Check Memory Usage**
```bash
free -h
```

### **View All Reports**
```bash
ls -lh ~/wordpress-monitor/reports/
```

### **Clean Old Reports (older than 30 days)**
```bash
find ~/wordpress-monitor/reports/ -type f -mtime +30 -delete
```

### **Update Configuration**
```bash
# Edit config
nano ~/wordpress-monitor/config/config.yaml

# Restart service to apply changes
sudo systemctl restart wordpress-monitor
```

---

## 🔄 **UPDATING THE CODE**

### **If you make changes on your local machine:**

```bash
# From your local machine (Windows)
cd C:\Users\Nevas\.gemini\antigravity\scratch\wordpress-monitor
scp scheduler.py wpmonitor@YOUR_VPS_IP:/home/wpmonitor/wordpress-monitor/

# On VPS - restart service
sudo systemctl restart wordpress-monitor
```

### **Or use Git:**
```bash
# On VPS
cd ~/wordpress-monitor
git pull origin main
sudo systemctl restart wordpress-monitor
```

---

## 🛡️ **SECURITY BEST PRACTICES**

### ✅ **Do's:**
1. ✅ Use a dedicated user (`wpmonitor`) instead of `root`
2. ✅ Keep `.env` file with restricted permissions:
   ```bash
   chmod 600 ~/.env
   ```
3. ✅ Enable UFW firewall
4. ✅ Use SSH keys instead of passwords (advanced)
5. ✅ Keep system updated:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

### ❌ **Don'ts:**
1. ❌ Don't commit `.env` to Git
2. ❌ Don't run as root user
3. ❌ Don't expose dashboard publicly without authentication
4. ❌ Don't ignore security updates

---

## 🐛 **TROUBLESHOOTING**

### **Service won't start:**
```bash
# Check logs for errors
sudo journalctl -u wordpress-monitor -n 50

# Check permissions
ls -la ~/wordpress-monitor/scheduler.py

# Verify Python path
which python3
```

### **Browser not found:**
```bash
# Reinstall Playwright
source ~/wordpress-monitor/venv/bin/activate
playwright install chromium
playwright install-deps chromium
```

### **Email not sending:**
```bash
# Verify .env file
cat ~/wordpress-monitor/.env

# Test email manually
python test_email.py
```

### **High memory usage:**
```bash
# Check running processes
htop

# Restart service
sudo systemctl restart wordpress-monitor
```

---

## 📦 **BACKUP STRATEGY**

### **Backup Important Files:**
```bash
# Create backup directory
mkdir -p ~/backups

# Backup configuration and environment
tar -czf ~/backups/wpmonitor-$(date +%Y%m%d).tar.gz \
    ~/wordpress-monitor/config/ \
    ~/wordpress-monitor/.env \
    ~/wordpress-monitor/data/

# Download backup to local machine (from Windows)
scp wpmonitor@YOUR_VPS_IP:~/backups/wpmonitor-*.tar.gz C:\Backups\
```

---

## 🎉 **SUCCESS CHECKLIST**

After deployment, verify:

- [ ] Service is running: `sudo systemctl status wordpress-monitor`
- [ ] Logs show scheduler started: `tail ~/wordpress-monitor/logs/scheduler.log`
- [ ] First check completed successfully
- [ ] PDF report generated in `reports/` folder
- [ ] Email received at configured address
- [ ] Service survives reboot: `sudo reboot` (then check again)
- [ ] Logs are being written
- [ ] Disk space is sufficient

---

## 💰 **COST ESTIMATION (Hostinger VPS)**

| VPS Plan | Price/Month | Suitable For |
|----------|-------------|--------------|
| **VPS 1** (1 GB RAM) | ~$4-6 | Testing only |
| **VPS 2** (2 GB RAM) | ~$6-10 | ✅ **Recommended** |
| **VPS 3** (4 GB RAM) | ~$12-18 | Multiple monitors |

**Recommended:** VPS 2 (2 GB RAM) for reliable 24/7 monitoring

---

## 📞 **QUICK REFERENCE COMMANDS**

```bash
# Start service
sudo systemctl start wordpress-monitor

# Stop service
sudo systemctl stop wordpress-monitor

# Restart service
sudo systemctl restart wordpress-monitor

# View logs
tail -f ~/wordpress-monitor/logs/scheduler.log

# Check status
sudo systemctl status wordpress-monitor

# Run manual check
cd ~/wordpress-monitor && source venv/bin/activate && python cli.py check --browser --headless
```

---

## 🎯 **SUMMARY**

1. ✅ Connect to VPS via SSH
2. ✅ Install Python, dependencies, Playwright
3. ✅ Upload your project code
4. ✅ Configure `.env` and `config.yaml`
5. ✅ Test manually
6. ✅ Create systemd service
7. ✅ Enable auto-start
8. ✅ Monitor logs

**Your WordPress monitor will now run 24/7 automatically!** 🚀

**Estimated Setup Time:** 30-60 minutes  
**Monthly Cost:** ~$6-10 USD  
**Uptime:** 99.9% with systemd auto-restart
