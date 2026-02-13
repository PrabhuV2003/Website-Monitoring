# Gmail Setup Guide for WordPress Monitor Email

## Step-by-Step Gmail Configuration

### 🔐 Step 1: Get Your Gmail App Password

**Important:** Gmail requires an "App Password" for automated email sending. You CANNOT use your regular Gmail password.

#### How to Create Gmail App Password:

1. **Go to Google Account Settings:**
   - Visit: https://myaccount.google.com/security
   - Make sure you're logged into the Gmail account you want to use

2. **Enable 2-Step Verification** (if not already enabled):
   - Scroll to "How you sign in to Google"
   - Click "2-Step Verification"
   - Follow the prompts to enable it
   - You'll need your phone for verification

3. **Generate App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Or: Google Account → Security → 2-Step Verification → App passwords (at bottom)
   - Under "Select app", choose **"Mail"**
   - Under "Select device", choose **"Windows Computer"** or **"Other"** (type "WordPress Monitor")
   - Click **"Generate"**

4. **Copy the 16-Character Password:**
   - Google will show a 16-character password like: `abcd efgh ijkl mnop`
   - **COPY THIS PASSWORD** - you'll need it in the next step
   - You won't be able to see it again!

---

### ⚙️ Step 2: Configure WordPress Monitor

#### Option A: Using PowerShell Setup Script (Recommended - Easiest)

Run this in PowerShell from the wordpress-monitor directory:

    ```powershell
    .\setup_email.ps1
    ```

When prompted:
- **Email**: Enter your Gmail address (e.g., `yourname@gmail.com`)
- **Password**: Paste the 16-character App Password you just copied
- **Save option**: Choose **2** (Permanent for current user)

#### Option B: Manual Configuration

**1. Set Environment Variables Permanently:**

Open PowerShell and run:

```powershell
# Replace with YOUR Gmail address
[System.Environment]::SetEnvironmentVariable('SMTP_USERNAME', 'yourname@gmail.com', 'User')

# Replace with YOUR App Password (16 characters from Google)
[System.Environment]::SetEnvironmentVariable('SMTP_PASSWORD', 'abcd efgh ijkl mnop', 'User')

# Also set for current session
$env:SMTP_USERNAME = 'yourname@gmail.com'
$env:SMTP_PASSWORD = 'abcd efgh ijkl mnop'
```

**2. Update config.yaml:**

The Gmail SMTP settings are already correct in your config.yaml:

```yaml
alerts:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"  # ✅ Correct for Gmail
    smtp_port: 587                  # ✅ Correct for Gmail
    smtp_username: ""  # Leave empty - uses environment variable
    smtp_password: ""  # Leave empty - uses environment variable
    from_email: "yourname@gmail.com"  # ← Update this to YOUR Gmail
    recipients:
      - "client@example.com"  # ← Update with actual client emails
```

---

### 📧 Step 3: Update Recipients

Edit `config/config.yaml` and add your client email addresses:

```yaml
alerts:
  email:
    from_email: "yourname@gmail.com"  # Your Gmail address
    recipients:
      - "client1@example.com"         # Replace with real client emails
      - "client2@example.com"         # Add more as needed
      - "manager@yourcompany.com"     # Add as many as you want
```

---

### ✅ Step 4: Test Email Delivery

Run the test script to verify everything works:

```powershell
python test_email.py
```

**Expected Output:**
```
============================================================
📧 EMAIL CONFIGURATION TEST
============================================================

📋 Email Settings:
   Enabled: True
   SMTP Server: smtp.gmail.com
   SMTP Port: 587
   From Email: yourname@gmail.com
   Recipients: client1@example.com, client2@example.com

🔐 Environment Variables:
   SMTP_USERNAME: ✅ Set
   SMTP_PASSWORD: ✅ Set

✅ Email configuration is complete!

============================================================
📨 READY TO SEND TEST EMAIL
============================================================

This will send a test PDF report to:
  • client1@example.com
  • client2@example.com

Proceed? (yes/no): yes

🚀 Sending test email...
   📄 Generating HTML report...
   ✅ HTML report created: reports/report_test_email_...html
   📄 Converting to PDF...
   ✅ PDF created: reports/report_test_email_...pdf
   📧 Sending email...

✅ SUCCESS! Test email sent to:
   ✉️  client1@example.com
   ✉️  client2@example.com

📬 Check your inbox for the test report!
```

---

### 🚀 Step 5: Start Automated Monitoring

Once the test is successful, start the scheduler:

```powershell
python scheduler.py
```

Now your monitor will:
- Run checks at the scheduled time (currently: daily at 11:07 AM)
- Automatically generate PDF reports
- Email them to all configured recipients
- Log everything to `logs/scheduler.log`

---

## 🔍 Verification Checklist

Before going live, verify:

- [ ] Gmail App Password created (not regular password!)
- [ ] `SMTP_USERNAME` environment variable set to your Gmail
- [ ] `SMTP_PASSWORD` environment variable set to App Password
- [ ] `from_email` in config.yaml updated to your Gmail
- [ ] `recipients` in config.yaml updated with real client emails
- [ ] Test email sent successfully (`python test_email.py`)
- [ ] Test email received in client inbox
- [ ] PDF attachment opens correctly

---

## ⚠️ Common Gmail Issues & Solutions

### Issue: "SMTP authentication failed"
**Cause:** Using regular Gmail password instead of App Password  
**Fix:** Create and use an App Password (see Step 1 above)

### Issue: "Username and Password not accepted"
**Cause:** 2-Step Verification not enabled or App Password not generated  
**Fix:** 
1. Enable 2-Step Verification: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords

### Issue: "Environment variables not persisting"
**Cause:** Variables set only for current session  
**Fix:** Use option 2 when running `setup_email.ps1`, or use `SetEnvironmentVariable` with `'User'` parameter

### Issue: "Emails going to spam"
**Cause:** Gmail's spam filters or recipient email filters  
**Fix:** 
1. Send from a verified Gmail address
2. Ask recipients to check spam folder and mark as "Not Spam"
3. Add your monitoring email to recipient's contacts

---

## 🎯 Quick Reference

**Gmail SMTP Settings:**
- Server: `smtp.gmail.com`
- Port: `587`
- Security: TLS/STARTTLS
- Authentication: Required (App Password)

**Environment Variables:**
```powershell
$env:SMTP_USERNAME = "yourname@gmail.com"
$env:SMTP_PASSWORD = "abcd efgh ijkl mnop"  # 16-char App Password
```

**Test Command:**
```powershell
python test_email.py
```

**Start Scheduler:**
```powershell
python scheduler.py
```

**View Logs:**
```powershell
Get-Content logs\scheduler.log -Wait -Tail 20
```

---

## 📱 App Password Management

**View existing App Passwords:**
https://myaccount.google.com/apppasswords

**Revoke App Password:**
If compromised, go to the link above and delete the password. Then generate a new one.

**Multiple devices:**
You can create different App Passwords for different purposes (e.g., one for WordPress Monitor, one for other apps)

---

## ✅ You're All Set!

Once configured, your WordPress Monitor will automatically:
1. ✉️ Send professional PDF reports to clients
2. 📊 Include health scores and issue summaries
3. 📎 Attach detailed PDF reports
4. ⏰ Run on your configured schedule
5. 📝 Log all activities

No manual intervention needed! 🚀
