# SMTP Email Configuration Guide

## Problem
The scheduler is showing this error:
```
WARNING | scheduler | Failed to email report: SMTP credentials not configured. Set SMTP_USERNAME and SMTP_PASSWORD environment variables.
```

## Solution

You have **two options** to configure SMTP credentials:

---

## ✅ **Option 1: Use Environment Variables (Recommended)**

### Step 1: Get Gmail App Password

1. Go to [Google App Passwords](https://myaccount.google.com/apppasswords)
2. Sign in to your Google account
3. Select **"Mail"** as the app
4. Select **"Other"** as the device, name it "WordPress Monitor"
5. Click **"Generate"**
6. Copy the 16-character password (example: `abcd efgh ijkl mnop`)
7. Remove all spaces: `abcdefghijklmnop`

### Step 2: Run the Setup Script

**Option A: Interactive Setup (Easiest)**
```powershell
cd c:\Users\Nevas\.gemini\antigravity\scratch\wordpress-monitor
.\setup_env.ps1
```

The script will:
- Ask for your Gmail address
- Ask for your App Password
- Create a `.env` file automatically
- Generate a random dashboard secret key

**Option B: Manual Setup**
```powershell
# Copy the example file
copy .env.example .env

# Edit .env in notepad
notepad .env
```

Then update these lines:
```env
SMTP_USERNAME=nevasai2025@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
```

### Step 3: Verify Configuration

Check that the recipients are configured in `config/config.yaml`:
```yaml
alerts:
  email:
    enabled: true
    recipients:
      - "nevasai2025@gmail.com"
      - "manager@company.com"
```

### Step 4: Test Email

```powershell
python test_email.py
```

If successful, you should see:
```
✓ Report email sent successfully to nevasai2025@gmail.com
```

### Step 5: Restart the Scheduler

The scheduler will automatically load the `.env` file on startup:
```powershell
python scheduler.py
```

---

## Option 2: Set Credentials Directly in config.yaml (Not Recommended)

**Warning:** This stores your password in plain text. Only use for testing.

Edit `config/config.yaml`:
```yaml
alerts:
  email:
    enabled: true
    smtp_username: "nevasai2025@gmail.com"
    smtp_password: "your-app-password-here"  # Gmail App Password
    recipients:
      - "nevasai2025@gmail.com"
```

---

## How It Works

1. **Priority Order**: The code checks for credentials in this order:
   - Environment variables (`SMTP_USERNAME`, `SMTP_PASSWORD`)
   - Config file (`smtp_username`, `smtp_password`)

2. **Automatic Loading**: When `scheduler.py` starts, it automatically:
   - Imports `load_env.py`
   - Reads the `.env` file
   - Sets environment variables for the session

3. **Security**: 
   - The `.env` file is in `.gitignore` (never committed to Git)
   - Environment variables are only stored in memory
   - The `.env.example` shows the format without real credentials

---

## Troubleshooting

### "Authentication failed" Error
- Make sure you're using a **Gmail App Password**, not your regular password
- Remove all spaces from the App Password
- Check that 2-Factor Authentication is enabled on your Google account

### "SMTP credentials not configured" Warning
- Verify the `.env` file exists in the project root
- Check that there are no typos in variable names (`SMTP_USERNAME`, `SMTP_PASSWORD`)
- Make sure there are no extra spaces around the `=` sign

### Email not sending but no error
- Check `alerts.email.enabled` is set to `true` in config.yaml
- Verify that `recipients` list has valid email addresses
- Check the `logs/scheduler.log` file for detailed error messages

---

## Quick Reference

| File | Purpose |
|------|---------|
| `.env` | Stores your actual credentials (DO NOT commit) |
| `.env.example` | Template showing required variables |
| `setup_env.ps1` | Interactive script to create `.env` file |
| `load_env.py` | Auto-loads variables from `.env` |
| `test_email.py` | Test script to verify email works |
| `config/config.yaml` | Email recipients and other settings |

---

## Next Steps

After setting up SMTP credentials:

1. ✅ Test email functionality: `python test_email.py`
2. ✅ Run a manual check: `python cli.py check`
3. ✅ Start the scheduler: `python scheduler.py`
4. ✅ Schedule will run automatically at the configured time

The scheduler will now successfully send PDF reports to all recipients after each check! 📧
