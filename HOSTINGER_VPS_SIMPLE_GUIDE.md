# 🚀 HOSTINGER VPS DEPLOYMENT - SUPER SIMPLE GUIDE

## For Monitoring Nevastech & Ascent365

---

## 📋 **WHAT YOU NEED BEFORE STARTING:**

- ✅ Hostinger VPS account (2GB RAM recommended)
- ✅ VPS IP address (from Hostinger panel)
- ✅ VPS root password (from Hostinger email)
- ✅ 30-60 minutes of your time

---

## 🎯 **WHAT WE'LL DO:**

1. Connect to your VPS
2. Install required software
3. Upload your monitoring tool
4. Set it to run automatically 24/7
5. Done! Emails sent automatically every day!

---

# STEP-BY-STEP GUIDE

---

## **PART 1: CONNECT TO YOUR VPS**

### Step 1.1: Get Your VPS Details

**Log in to Hostinger VPS panel:**
- Find your **IP Address** (looks like: `123.45.67.89`)
- Find your **Root Password** (in welcome email or panel)

### Step 1.2: Connect via SSH

**On your Windows computer:**

**Method A: PowerShell (Built-in)**
```powershell
ssh root@YOUR_VPS_IP
# Replace YOUR_VPS_IP with actual IP like: 123.45.67.89
```

**Method B: Use PuTTY (if PowerShell doesn't work)**
1. Download PuTTY: https://the.earth.li/~sgtatham/putty/latest/w64/putty.exe
2. Open PuTTY
3. Enter IP address in "Host Name"
4. Click "Open"
5. Click "Yes" on security alert
6. Login: `root`
7. Enter password (won't show when typing - that's normal!)

✅ **You're now connected to your VPS!**

---

## **PART 2: INSTALL REQUIRED SOFTWARE**

Copy/paste these commands **one at a time** into your SSH window:

### Step 2.1: Update System

```bash
sudo apt update && sudo apt upgrade -y
```
⏱️ *Takes 2-5 minutes*

### Step 2.2: Install Python

```bash
sudo apt install -y python3 python3-pip python3-venv git
```
⏱️ *Takes 1-2 minutes*

### Step 2.3: Install Browser Dependencies

```bash
sudo apt install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2
```
⏱️ *Takes 1-2 minutes*

### Step 2.4: Verify Installation

```bash
python3 --version
```

You should see: `Python 3.10.x` or higher ✅

---

## **PART 3: CREATE USER & UPLOAD PROJECT**

### Step 3.1: Create Dedicated User

```bash
# Create user
sudo adduser wpmonitor
# Enter password when asked (remember it!)
# Press ENTER for all other questions

# Switch to new user
su - wpmonitor
```

### Step 3.2: Create Project Folder

```bash
mkdir -p ~/wordpress-monitor
cd ~/wordpress-monitor
```

### Step 3.3: Upload Your Files

**Go back to your Windows machine** and run:

**Option A: Use WinSCP (Easiest - GUI)**
1. Download WinSCP: https://winscp.net/download/WinSCP-6.3.5-Setup.exe
2. Install and open WinSCP
3. Connect to your VPS:
   - Protocol: SFTP
   - Host: YOUR_VPS_IP
   - Username: `wpmonitor`
   - Password: (password you just created)
4. Click "Login"
5. Navigate to `/home/wpmonitor/wordpress-monitor/`
6. On left side, navigate to: `C:\Users\Nevas\.gemini\antigravity\scratch\wordpress-monitor\`
7. **Select ALL files** and drag to right side
8. Wait for upload to complete (5-10 minutes)

**Option B: Command Line (SCP)**
```powershell
# On your Windows machine
cd C:\Users\Nevas\.gemini\antigravity\scratch\wordpress-monitor

# Upload everything
scp -r * wpmonitor@YOUR_VPS_IP:/home/wpmonitor/wordpress-monitor/
# Enter password when asked
```

✅ **Files uploaded!**

---

## **PART 4: INSTALL PYTHON PACKAGES**

**Back in your SSH connection:**

```bash
# Make sure you're in the right folder
cd ~/wordpress-monitor

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) before your prompt now

# Install packages
pip install --upgrade pip
pip install -r requirements.txt
```
⏱️ *Takes 5-10 minutes*

### Install Playwright Browser

```bash
# Still in virtual environment
playwright install chromium
playwright install-deps chromium
```
⏱️ *Takes 2-5 minutes*

---

## **PART 5: CONFIGURE FOR YOUR WEBSITES**

### Step 5.1: Update .env File

```bash
nano .env
```

**What you need to edit:**

If using **separate Gmail accounts** (Option 2):
```env
# SMTP Configuration - COMMENTED OUT (using config files)
# SMTP_USERNAME=
# SMTP_PASSWORD=

# Keep these as is
DASHBOARD_SECRET_KEY=your-random-secret-key-here
```

If using **one Gmail account** (current setup):
```env
# SMTP Configuration
SMTP_USERNAME=nevasai2025@gmail.com
SMTP_PASSWORD=bztt zlmc dtfb egjj

DASHBOARD_SECRET_KEY=your-random-secret-key-here
```

**Save:** Press `Ctrl+X`, then `Y`, then `Enter`

### Step 5.2: Verify Config Files

**Check Nevastech config:**
```bash
nano config/config.yaml
```

Verify:
- `check_time: "16:30"` (or your preferred time)
- Email recipients are correct
- `smtp_username` and `smtp_password` (if using separate accounts)

Save: `Ctrl+X`, `Y`, `Enter`

**Check Ascent365 config:**
```bash
nano config/ascent365.yaml
```

Verify:
- `check_time: "06:00"` (or your preferred time)  
- Email recipients are correct
- `smtp_username: "norepliesascent365@gmail.com"`
- `smtp_password: "hkcn ujac suli surz"`

Save: `Ctrl+X`, `Y`, `Enter`

---

## **PART 6: TEST BEFORE GOING LIVE**

### Test Nevastech:

```bash
cd ~/wordpress-monitor
source venv/bin/activate
python test_email_nevastech.py
```

- Enter `yes` when asked
- Wait 1-2 minutes
- Check if email arrived!

### Test Ascent365:

```bash
python test_email_ascent365.py
```

- Enter `yes` when asked
- Wait 1-2 minutes
- Check if email arrived!

✅ **If both emails arrived, you're good!**

---

## **PART 7: CREATE AUTO-START SERVICES**

Now we'll make BOTH schedulers run automatically 24/7!

### Step 7.1: Create Nevastech Service

```bash
sudo nano /etc/systemd/system/wordpress-monitor-nevastech.service
```

**Paste this (copy exactly):**
```ini
[Unit]
Description=WordPress Monitor - Nevastech
After=network.target

[Service]
Type=simple
User=wpmonitor
WorkingDirectory=/home/wpmonitor/wordpress-monitor
Environment="PATH=/home/wpmonitor/wordpress-monitor/venv/bin"
ExecStart=/home/wpmonitor/wordpress-monitor/venv/bin/python scheduler_nevastech.py
Restart=always
RestartSec=10
StandardOutput=append:/home/wpmonitor/wordpress-monitor/logs/nevastech-service.log
StandardError=append:/home/wpmonitor/wordpress-monitor/logs/nevastech-error.log

[Install]
WantedBy=multi-user.target
```

Save: `Ctrl+X`, `Y`, `Enter`

### Step 7.2: Create Ascent365 Service

```bash
sudo nano /etc/systemd/system/wordpress-monitor-ascent365.service
```

**Paste this:**
```ini
[Unit]
Description=WordPress Monitor - Ascent365
After=network.target

[Service]
Type=simple
User=wpmonitor
WorkingDirectory=/home/wpmonitor/wordpress-monitor
Environment="PATH=/home/wpmonitor/wordpress-monitor/venv/bin"
ExecStart=/home/wpmonitor/wordpress-monitor/venv/bin/python scheduler_ascent365.py
Restart=always
RestartSec=10
StandardOutput=append:/home/wpmonitor/wordpress-monitor/logs/ascent365-service.log
StandardError=append:/home/wpmonitor/wordpress-monitor/logs/ascent365-error.log

[Install]
WantedBy=multi-user.target
```

Save: `Ctrl+X`, `Y`, `Enter`

---

## **PART 8: START BOTH SERVICES**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable both services (auto-start on boot)
sudo systemctl enable wordpress-monitor-nevastech
sudo systemctl enable wordpress-monitor-ascent365

# Start both services NOW
sudo systemctl start wordpress-monitor-nevastech
sudo systemctl start wordpress-monitor-ascent365

# Check if they're running
sudo systemctl status wordpress-monitor-nevastech
```

You should see: `Active: active (running)` ✅

```bash
sudo systemctl status wordpress-monitor-ascent365
```

You should see: `Active: active (running)` ✅

Press `q` to exit status view.

---

## **PART 9: VERIFY IT'S WORKING**

### View Nevastech Logs:

```bash
tail -f ~/wordpress-monitor/logs/nevastech-service.log
```

You should see:
```
Starting WordPress Monitor Scheduler
Scheduler started and running...
Next run: Daily at 4:30 PM (Asia/Kolkata)
```

Press `Ctrl+C` to stop viewing (service keeps running)

### View Ascent365 Logs:

```bash
tail -f ~/wordpress-monitor/logs/ascent365-service.log
```

You should see:
```
Starting Ascent365 Monitor Scheduler
Scheduler started and running...
Next run: Daily at 6:00 AM (Asia/Kolkata)
```

Press `Ctrl+C` to stop viewing

---

## 🎉 **YOU'RE DONE!**

---

## ✅ **WHAT HAPPENS NOW:**

### **Every Day Automatically:**

| Time | Website | Email To |
|------|---------|----------|
| **6:00 AM** | Ascent365 checks https://www.ascent365.com | prabhuofficial2003@gmail.com |
| **4:30 PM** | Nevastech checks https://www.nevastech.com | renderthaniks@gmail.com, prabhu@nevastech.com |

### **Each Email Contains:**
- ✅ Health score (0-100)
- ✅ Issues found (Critical, High, Medium, Low)
- ✅ Performance metrics
- ✅ **PDF report attachment**

### **No Manual Work Needed!**
- ✅ Runs automatically 24/7
- ✅ Auto-restarts if it crashes
- ✅ Starts automatically after VPS reboot
- ✅ All logs saved for review

---

## 📋 **HELPFUL COMMANDS**

### **Check if Services are Running:**
```bash
sudo systemctl status wordpress-monitor-nevastech
sudo systemctl status wordpress-monitor-ascent365
```

### **View Live Logs:**
```bash
# Nevastech logs
tail -f ~/wordpress-monitor/logs/nevastech-service.log

# Ascent365 logs
tail -f ~/wordpress-monitor/logs/ascent365-service.log
```

### **Restart a Service:**
```bash
# If you change config files
sudo systemctl restart wordpress-monitor-nevastech
sudo systemctl restart wordpress-monitor-ascent365
```

### **Stop a Service:**
```bash
sudo systemctl stop wordpress-monitor-nevastech
sudo systemctl stop wordpress-monitor-ascent365
```

### **Start a Service:**
```bash
sudo systemctl start wordpress-monitor-nevastech
sudo systemctl start wordpress-monitor-ascent365
```

---

## 🔧 **UPDATING CONFIG LATER**

### **To Change Schedule Time:**

```bash
# Edit config
nano ~/wordpress-monitor/config/ascent365.yaml

# Change line 17:
check_time: "10:00"  # Change to whatever you want

# Save (Ctrl+X, Y, Enter)

# Restart service
sudo systemctl restart wordpress-monitor-ascent365
```

### **To Add More Recipients:**

```bash
# Edit config
nano ~/wordpress-monitor/config/config.yaml

# Add more emails:
recipients:
  - "email1@example.com"
  - "email2@example.com"  # Add more here

# Save and restart
sudo systemctl restart wordpress-monitor-nevastech
```

---

## 🐛 **TROUBLESHOOTING**

### **Emails Not Sending?**

Check logs:
```bash
tail -n 50 ~/wordpress-monitor/logs/ascent365-service.log | grep -i error
```

Verify .env or config credentials.

### **Service Won't Start?**

Check for errors:
```bash
sudo journalctl -u wordpress-monitor-ascent365 -n 50
```

### **High Memory Usage?**

Check memory:
```bash
free -h
```

Restart services:
```bash
sudo systemctl restart wordpress-monitor-nevastech
sudo systemctl restart wordpress-monitor-ascent365
```

---

## 💰 **COST**

**Hostinger VPS 2 (Recommended):**
- **RAM:** 2 GB
- **Storage:** 20 GB
- **Price:** ~$6-10 USD/month
- **Perfect for:** 2 websites, daily checks

---

## 📞 **NEED HELP?**

**View all services:**
```bash
sudo systemctl list-units --type=service | grep wordpress
```

**Check system resources:**
```bash
htop
```

Press `q` to exit.

---

## 🎯 **QUICK SUMMARY**

1. ✅ Connect to VPS via SSH
2. ✅ Install Python & dependencies (10 min)
3. ✅ Upload your files via WinSCP (10 min)
4. ✅ Install Python packages (10 min)
5. ✅ Configure .env and configs (5 min)
6. ✅ Test email sending (5 min)
7. ✅ Create systemd services (5 min)
8. ✅ Start services (2 min)

**Total Time:** 45-60 minutes  
**Result:** 24/7 automated monitoring! 🚀

---

**Both websites are now monitored automatically from your VPS!** 🎉

**You can close SSH and everything keeps running!**
