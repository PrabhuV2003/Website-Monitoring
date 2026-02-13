# Quick Start Guide: PDF Reports & Email Delivery

## ✅ What's Working

Your WordPress Monitor dashboard is now enhanced with:
- 📥 **PDF Generation** - Convert any report to PDF format
- 📧 **Email Delivery** - Send reports directly to clients
- 🎨 **Professional Templates** - Beautiful emails with health scores

## 🚀 How to Use (3 Simple Steps)

### Dashboard is Running
The dashboard is currently active at: **http://127.0.0.1:5000**

### Step 1: Generate or View Reports
1. Open http://127.0.0.1:5000 in your browser
2. Either run a new check OR view existing reports in the Reports table
3. You'll see your reports listed with new action buttons

### Step 2: Generate PDF
Click the **"📥 PDF"** button next to any report:
- PDF is automatically generated
- Opens in a new tab for download
- Saved in the `reports/` folder

### Step 3: Email to Client
Click the **"📧 Email"** button next to any report:
1. A modal dialog opens
2. Enter client email address(es)
3. Click "Add" to add each email
4. Click "Send Email"
5. PDF is auto-generated and sent!

## 📧 Email Configuration (One-Time Setup)

### Option 1: Environment Variables (Recommended)
Set these in your system:
```
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Option 2: Config File
Edit `config/config.yaml`:
```yaml
alerts:
  email:
    enabled: true
    smtp_server: smtp.gmail.com
    smtp_port: 587
    smtp_username: your-email@gmail.com
    smtp_password: your-app-password
    from_email: your-email@gmail.com
    recipients:
      - default-client@example.com
```

### Gmail App Password Setup
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification" if not already enabled
3. Search for "App passwords"
4. Select "Mail" and your device
5. Copy the 16-character password
6. Use this as your `SMTP_PASSWORD`

## 🧪 Test PDF Generation

We've already verified PDF generation works:
```
✅ Test PDF created: test_reports/report_test123_20260210_145859.pdf (6.2 KB)
```

To test again:
```bash
python test_pdf.py
```

## 📊 Email Template Includes

When you email a report, clients receive:
- **Health Score**: Visual indicator (0-100) with emoji
- **Issue Summary**: Count of Critical, High, Medium, Low issues
- **Performance Metrics**: Response time, uptime, pages checked
- **PDF Attachment**: Full detailed report

## 🎯 Example Workflow

**Scenario**: You ran a monitoring check and found issues

1. Dashboard shows "Report Generated" with action buttons
2. Click "📥 PDF" to download a copy for yourself
3. Click "📧 Email" to send to client
4. Enter: `client@example.com`
5. Click "Add" then "Send Email"
6. Client receives professional email with PDF attached
7. Done! ✅

## 🐛 Troubleshooting

### "PDF generation failed"
- **Fix**: xhtml2pdf is already installed and tested
- This error shouldn't occur. If it does, run: `pip install xhtml2pdf`

### "SMTP authentication failed"
- **Gmail users**: Make sure you're using an **App Password**, not your regular password
- **Other providers**: Check smtp_server and smtp_port in config

### "No recipient emails provided"
- **Fix**: Add at least one email address in the modal before clicking "Send"

### Email not sending
1. Check environment variables: `SMTP_USERNAME` and `SMTP_PASSWORD`
2. Verify internet connection
3. Check SMTP server settings (Gmail: smtp.gmail.com:587)
4. Review dashboard logs for error details

## 📁 File Locations

- **Reports**: `reports/` folder
- **PDFs**: Same `reports/` folder (auto-generated)
- **Test Reports**: `test_reports/` folder
- **Config**: `config/config.yaml`

## 🔄 Restart Dashboard

If you made config changes:
1. Stop the dashboard (Ctrl+C in terminal)
2. Restart: `python dashboard/app.py`
3. Reload http://127.0.0.1:5000

## ✨ Features You Can Use Now

- [x] Generate PDF from any HTML report
- [x] Email reports with one click
- [x] Professional email template with health scores
- [x] Multiple recipient support
- [x] Real-time feedback and error handling
- [x] Mobile-responsive email design

## 📝 Summary

**Everything is ready to use!** Just:
1. Set up your SMTP credentials (one-time)
2. Open the dashboard
3. Generate/view reports
4. Click PDF or Email buttons
5. Send professional reports to clients!

Need help? Check the detailed documentation in `PDF_EMAIL_IMPLEMENTATION.md`
