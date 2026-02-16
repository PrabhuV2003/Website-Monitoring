# 🚀 Deploy to Hostinger VPS Using GitHub

## Much Easier Than Manual Upload!

---

## 🎯 **WHY USE GITHUB?**

### **Manual Upload (Old Way):**
- ❌ Slow upload via WinSCP (10+ minutes)
- ❌ Hard to update files
- ❌ Have to upload everything again for small changes

### **GitHub (New Way):**
- ✅ Upload once to GitHub (1 minute)
- ✅ Clone to VPS instantly (30 seconds)
- ✅ Update with one command: `git pull`
- ✅ No need to drag/drop files!

---

## 📋 **WHAT WE'LL DO:**

1. Create GitHub account (if you don't have)
2. Create private repository
3. Upload your project to GitHub
4. Clone from GitHub to VPS
5. Done! Update anytime with `git pull`

---

# PART 1: SETUP GITHUB REPOSITORY

---

## **Step 1.1: Create GitHub Account**

**If you already have GitHub account, skip to Step 1.2**

1. Go to: https://github.com/signup
2. Enter your email
3. Create password
4. Choose username
5. Verify email

✅ **Account created!**

---

## **Step 1.2: Create New Repository**

1. Go to: https://github.com/new
2. **Repository name:** `wordpress-monitor`
3. **Description:** WordPress monitoring tool for Nevastech & Ascent365
4. **Visibility:** ⚠️ **PRIVATE** (important - contains passwords!)
5. **Do NOT check** "Add a README file"
6. Click **"Create repository"**

✅ **Repository created!**

You'll see a page with commands. **Keep this page open!**

---

## **Step 1.3: Prepare .gitignore File**

**On your Windows machine:**

Open PowerShell and navigate to your project:

```powershell
cd C:\Users\Nevas\.gemini\antigravity\scratch\wordpress-monitor
```

Create `.gitignore` file:

```powershell
# Create .gitignore
@"
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Reports and logs
reports/
logs/
*.log

# Environment variables (IMPORTANT - don't upload passwords!)
.env

# OS files
.DS_Store
Thumbs.db
*.swp

# Browser data
playwright/.browser/
.playwright/

# Data files
data/
*.db
*.sqlite

# Temporary files
*.tmp
~*
"@ | Out-File -FilePath .gitignore -Encoding utf8
```

✅ **.gitignore created!** (This prevents uploading sensitive files)

---

## **Step 1.4: Create .env.example (Template)**

```powershell
# Create example env file
@"
# SMTP Email Configuration
# IMPORTANT: Use DIFFERENT accounts for each website
# Comment out these if using config files for credentials
# SMTP_USERNAME=your-gmail@gmail.com
# SMTP_PASSWORD=your-app-password-here

# Dashboard
DASHBOARD_SECRET_KEY=your-random-secret-key-here

# Optional
PAGESPEED_API_KEY=
SLACK_WEBHOOK_URL=
DISCORD_WEBHOOK_URL=
"@ | Out-File -FilePath .env.example -Encoding utf8
```

✅ **Template created!** (Safe to upload, has no real passwords)

---

## **Step 1.5: Initialize Git**

```powershell
# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit - WordPress Monitor for Nevastech & Ascent365"
```

If you see error about email/name:
```powershell
git config --global user.email "your-email@gmail.com"
git config --global user.name "Your Name"
# Then try the commit again
git commit -m "Initial commit - WordPress Monitor for Nevastech & Ascent365"
```

---

## **Step 1.6: Push to GitHub**

**Replace `yourusername` with your GitHub username:**

```powershell
# Add GitHub as remote
git remote add origin https://github.com/yourusername/wordpress-monitor.git

# Push to GitHub
git push -u origin main
```

If it asks for "master" instead of "main":
```powershell
git branch -M main
git push -u origin main
```

**GitHub will ask for login:**
- Username: Your GitHub username
- Password: **Personal Access Token** (NOT your GitHub password!)

### **How to Create Personal Access Token:**

1. Go to: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Note: "WordPress Monitor VPS Access"
4. Expiration: 90 days (or longer)
5. Check: ✅ **repo** (full control)
6. Click **"Generate token"**
7. **Copy the token** (looks like: `ghp_xxxxxxxxxxxxxxxxxxx`)
8. **Use this as password** when git asks for it
9. **Save it somewhere safe!** You can't see it again!

After entering token, files upload to GitHub! ✅

---

# PART 2: CLONE FROM GITHUB TO VPS

---

## **Step 2.1: Connect to VPS**

```powershell
ssh root@YOUR_VPS_IP
```

Enter password.

---

## **Step 2.2: Install Git (if not already)**

```bash
sudo apt update
sudo apt install -y git
```

---

## **Step 2.3: Create User (if not already)**

```bash
# Create user
sudo adduser wpmonitor
# Enter password

# Switch to user
su - wpmonitor
```

---

## **Step 2.4: Clone Repository**

**Replace `yourusername` with your GitHub username:**

```bash
cd ~
git clone https://github.com/yourusername/wordpress-monitor.git
cd wordpress-monitor
```

**GitHub will ask for credentials:**
- Username: Your GitHub username
- Password: **Personal Access Token** (the one you created earlier)

✅ **Project cloned to VPS!**

---

## **Step 2.5: Create .env File on VPS**

**IMPORTANT:** `.env` is NOT in GitHub (for security), so create it manually:

```bash
nano .env
```

**Paste your actual credentials:**

```env
# SMTP Configuration - COMMENTED OUT (using config files)
# SMTP_USERNAME=
# SMTP_PASSWORD=

# Dashboard
DASHBOARD_SECRET_KEY=your-random-secret-key-here

# Optional
PAGESPEED_API_KEY=
SLACK_WEBHOOK_URL=
DISCORD_WEBHOOK_URL=
```

**Save:** `Ctrl+X`, `Y`, `Enter`

**Secure the file:**
```bash
chmod 600 .env
```

---

## **Step 2.6: Install Python Dependencies**

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright
playwright install chromium
playwright install-deps chromium
```

⏱️ *Takes 10-15 minutes*

---

## **Step 2.7: Test It Works**

```bash
# Test Nevastech
python test_email_nevastech.py
```

Enter `yes` → Check email!

```bash
# Test Ascent365
python test_email_ascent365.py
```

Enter `yes` → Check email!

✅ **Both working!**

---

## **Step 2.8: Create Systemd Services**

**(Same as before - follow steps 7-9 from HOSTINGER_VPS_SIMPLE_GUIDE.md)**

Create both service files and start them.

---

# PART 3: UPDATING CODE LATER

---

## **🎯 THIS IS THE MAGIC PART!**

### **When You Make Changes on Windows:**

**On your Windows machine:**

```powershell
cd C:\Users\Nevas\.gemini\antigravity\scratch\wordpress-monitor

# Make your changes to files...

# Commit changes
git add .
git commit -m "Updated scheduler times"

# Push to GitHub
git push
```

### **Update VPS (Super Easy!):**

**On your VPS:**

```bash
# Login to VPS
ssh wpmonitor@YOUR_VPS_IP

# Go to project folder
cd ~/wordpress-monitor

# Pull latest changes
git pull

# Restart services
sudo systemctl restart wordpress-monitor-nevastech
sudo systemctl restart wordpress-monitor-ascent365
```

**THAT'S IT!** Changes applied in **10 seconds!** ✅

---

## 📋 **COMMON UPDATES:**

### **Update Schedule Time:**

**On Windows:**
1. Edit `config/ascent365.yaml`
2. Change `check_time: "10:00"`
3. Save

**Push to GitHub:**
```powershell
git add config/ascent365.yaml
git commit -m "Changed Ascent365 schedule to 10:00 AM"
git push
```

**Update VPS:**
```bash
cd ~/wordpress-monitor
git pull
sudo systemctl restart wordpress-monitor-ascent365
```

**Done!** ✅

---

### **Update Email Recipients:**

**On Windows:**
1. Edit `config/config.yaml`
2. Add new recipient email
3. Save

**Push to GitHub:**
```powershell
git add config/config.yaml
git commit -m "Added new email recipient"
git push
```

**Update VPS:**
```bash
cd ~/wordpress-monitor
git pull
sudo systemctl restart wordpress-monitor-nevastech
```

**Done!** ✅

---

### **Fix a Bug:**

**On Windows:**
1. Edit `scheduler_ascent365.py`
2. Fix the bug
3. Save

**Push to GitHub:**
```powershell
git add scheduler_ascent365.py
git commit -m "Fixed PDF generation bug"
git push
```

**Update VPS:**
```bash
cd ~/wordpress-monitor
git pull
sudo systemctl restart wordpress-monitor-ascent365
```

**Done!** ✅

---

## 🔒 **SECURITY NOTES:**

### **✅ Safe to Upload to GitHub:**
- ✅ All code files (`.py`, `.yaml`)
- ✅ Documentation (`.md`)
- ✅ Requirements (`requirements.txt`)
- ✅ `.env.example` (template, no real passwords)

### **❌ NEVER Upload to GitHub:**
- ❌ `.env` file (contains real passwords!)
- ❌ `reports/` folder (HTML/PDF reports)
- ❌ `logs/` folder (log files)
- ❌ `venv/` folder (Python packages)

**The `.gitignore` file prevents these automatically!** ✅

---

## 🎯 **COMPLETE WORKFLOW:**

### **First Time Setup:**
```
1. Create GitHub repo (5 min)
2. Push code to GitHub (2 min)
3. Clone to VPS (1 min)
4. Install dependencies (15 min)
5. Setup services (5 min)
```
**Total: ~30 minutes**

### **Future Updates:**
```
1. Edit files on Windows (1 min)
2. git push (10 seconds)
3. git pull on VPS (5 seconds)
4. Restart service (5 seconds)
```
**Total: ~20 seconds!** 🚀

---

## 📖 **QUICK REFERENCE:**

### **On Windows:**
```powershell
cd C:\Users\Nevas\.gemini\antigravity\scratch\wordpress-monitor

# After making changes
git add .
git commit -m "Describe your changes here"
git push
```

### **On VPS:**
```bash
cd ~/wordpress-monitor
git pull
sudo systemctl restart wordpress-monitor-nevastech
sudo systemctl restart wordpress-monitor-ascent365
```

---

## 🎉 **BENEFITS SUMMARY:**

| Task | Manual Upload | GitHub |
|------|---------------|--------|
| **Initial upload** | 10-15 min | 2 min |
| **Update one file** | 5-10 min | 20 seconds |
| **Track changes** | ❌ No | ✅ Yes |
| **Revert mistakes** | ❌ Hard | ✅ `git revert` |
| **Work from anywhere** | ❌ Need files | ✅ Clone anywhere |
| **Backup** | ❌ Manual | ✅ Automatic |

---

## 🚀 **YOUR NEXT STEPS:**

1. **Create GitHub account** (if needed)
2. **Create private repo** 
3. **Push your code** (Part 1)
4. **Clone to VPS** (Part 2)
5. **Enjoy easy updates!** (Part 3)

---

**GitHub makes VPS deployment 10x easier!** 🎉

**Questions? Check the original guide for VPS setup details:**
`HOSTINGER_VPS_SIMPLE_GUIDE.md`
