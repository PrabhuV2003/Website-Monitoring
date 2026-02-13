# Quick Email Testing Guide

## ✅ Test Email Sending Instantly

I've created **3 test scripts** to quickly test email sending!

---

## 🚀 **Quick Tests:**

### **Test Nevastech Email:**
```powershell
.\test_email_nevastech.ps1
```

**What it does:**
1. ✅ Runs quick check on https://www.nevastech.com
2. ✅ Generates report & PDF
3. ✅ Sends email to: renderthaniks@gmail.com, prabhu@nevastech.com
4. ✅ Shows SUCCESS or FAILED

---

### **Test Ascent365 Email:**
```powershell
.\test_email_ascent365.ps1
```

**What it does:**
1. ✅ Runs quick check on https://www.ascent365.com
2. ✅ Generates report & PDF
3. ✅ Sends email to: prabhuofficial2003@gmail.com
4. ✅ Shows SUCCESS or FAILED

---

### **Test BOTH Emails:**
```powershell
.\test_all_emails.ps1
```

**What it does:**
1. ✅ Runs Nevastech test
2. ✅ Runs Ascent365 test
3. ✅ Shows results for both

---

## 📋 **What You'll See:**

### **If Email Succeeds:** ✅
```
========================================
  EMAIL TEST - NEVASTECH
========================================

Running quick check...
Report: reports/report_chk_20260213_111625_abc123.html
PDF: reports/report_chk_20260213_111625_abc123.pdf

Sending test email...

========================================
SUCCESS! Email sent!
========================================
Check the inbox for:
  - renderthaniks@gmail.com
  - prabhu@nevastech.com
```

### **If Email Fails:** ❌
```
========================================
FAILED! Email not sent!
========================================
Error: Authentication failed

Possible issues:
  1. Wrong Gmail credentials in config/config.yaml
  2. Wrong App Password
  3. 2-Step Verification not enabled
```

---

## 🔧 **Before Testing:**

### **Make sure you've updated credentials!**

**For Nevastech** (`config/config.yaml`):
```yaml
smtp_username: "your-real-email@gmail.com"  # UPDATE
smtp_password: "your-real-app-password"     # UPDATE
```

**For Ascent365** (`config/ascent365.yaml`):
```yaml
smtp_username: "your-real-email@gmail.com"  # UPDATE
smtp_password: "your-real-app-password"     # UPDATE
```

**If you haven't updated them yet**, the test will **FAIL** (dummy credentials won't work).

---

## 🎯 **Recommended Testing Flow:**

### **Step 1: Update Credentials**
```powershell
# Edit config/config.yaml - Update Nevastech credentials
# Edit config/ascent365.yaml - Update Ascent365 credentials
```

### **Step 2: Test Nevastech**
```powershell
.\test_email_nevastech.ps1
```

### **Step 3: Check Email**
- Open renderthaniks@gmail.com inbox
- Open prabhu@nevastech.com inbox
- Look for email: "🌐 Website Health Report — Nevas Technologies"

### **Step 4: Test Ascent365**
```powershell
.\test_email_ascent365.ps1
```

### **Step 5: Check Email**
- Open prabhuofficial2003@gmail.com inbox
- Look for email: "🌐 Website Health Report — Ascent Innovation"

---

## ⚠️ **Common Issues:**

### **Issue 1: Authentication Failed**
**Error:** `Authentication failed` or `Username and Password not accepted`

**Solution:**
- Use Gmail **App Password**, NOT regular password
- Get it from: https://myaccount.google.com/apppasswords
- Enable 2-Step Verification first

### **Issue 2: SMTP Connection Failed**
**Error:** `Could not connect to SMTP server`

**Solution:**
- Check internet connection
- Make sure smtp_server is `smtp.gmail.com`
- Make sure smtp_port is `587`

### **Issue 3: Wrong FROM Address**
**Error:** Email sends but FROM address is wrong

**Solution:**
- Make sure `from_email` matches `smtp_username`
- Both should be the same Gmail address

---

## 🎉 **Success Checklist:**

After running tests successfully:

- [ ] Nevastech test passed
- [ ] Email arrived at renderthaniks@gmail.com
- [ ] Email arrived at prabhu@nevastech.com
- [ ] FROM address shows: nevastech.monitor@gmail.com (or your email)
- [ ] PDF attachment included

- [ ] Ascent365 test passed
- [ ] Email arrived at prabhuofficial2003@gmail.com
- [ ] FROM address shows: ascent365.monitor@gmail.com (or your email)
- [ ] PDF attachment included

**If all checkboxes are ✅, email sending works perfectly!**

---

## 📁 **Test Scripts Created:**

| Script | What It Tests |
|--------|---------------|
| `test_email_nevastech.ps1` | Nevastech email only |
| `test_email_ascent365.ps1` | Ascent365 email only |
| `test_all_emails.ps1` | Both websites |

---

## 🚀 **Quick Start:**

```powershell
# Test Nevastech email now:
.\test_email_nevastech.ps1

# Test Ascent365 email now:
.\test_email_ascent365.ps1

# Test both:
.\test_all_emails.ps1
```

**Each test takes about 30-60 seconds to complete!**
