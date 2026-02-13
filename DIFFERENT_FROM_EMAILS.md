# How to Use Different Email Addresses for Each Website

## ✅ Easy Setup - Different FROM Emails

You can send emails from different addresses for each website!

---

## Option 1: Same SMTP Account, Different FROM Name (Recommended)

### This works if:
- ✅ You have ONE Gmail account
- ✅ You want different "display names" for each website
- ✅ Emails come from the same address but look different

### Setup:

**Nevastech** (`config/config.yaml`):
```yaml
alerts:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    smtp_username: ""  # Uses SMTP_USERNAME from .env
    smtp_password: ""  # Uses SMTP_PASSWORD from .env
    from_email: "nevasai2025@gmail.com"  # FROM address
    recipients:
      - "renderthaniks@gmail.com"
      - "prabhu@nevastech.com"
```

**Ascent365** (`config/ascent365.yaml`):
```yaml
alerts:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    smtp_username: ""  # Uses same SMTP_USERNAME from .env
    smtp_password: ""  # Uses same SMTP_PASSWORD from .env
    from_email: "nevasai2025@gmail.com"  # Same FROM address
    recipients:
      - "prabhuofficial2003@gmail.com"
```

**Result:**
- ✅ Nevastech emails: FROM "nevasai2025@gmail.com"
- ✅ Ascent365 emails: FROM "nevasai2025@gmail.com"
- ✅ Different recipients for each
- ✅ Same Gmail account sends both

---

## Option 2: Different Gmail Accounts for Each Website

### This works if:
- ✅ You have TWO different Gmail accounts
- ✅ You want completely different FROM addresses
- ✅ Each website uses its own email account

### Setup:

### Step 1: Create Two Gmail App Passwords

**Gmail Account 1** (for Nevastech):
- Email: `nevastech.monitor@gmail.com`
- App Password: `abcd efgh ijkl mnop`

**Gmail Account 2** (for Ascent365):
- Email: `ascent365.monitor@gmail.com`
- App Password: `wxyz abcd efgh ijkl`

### Step 2: Update Config Files

**Nevastech** (`config/config.yaml`):
```yaml
alerts:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    smtp_username: "nevastech.monitor@gmail.com"  # <-- Account 1
    smtp_password: "abcd efgh ijkl mnop"           # <-- App password 1
    from_email: "nevastech.monitor@gmail.com"
    recipients:
      - "renderthaniks@gmail.com"
      - "prabhu@nevastech.com"
```

**Ascent365** (`config/ascent365.yaml`):
```yaml
alerts:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    smtp_username: "ascent365.monitor@gmail.com"  # <-- Account 2
    smtp_password: "wxyz abcd efgh ijkl"           # <-- App password 2
    from_email: "ascent365.monitor@gmail.com"
    recipients:
      - "prabhuofficial2003@gmail.com"
```

**Result:**
- ✅ Nevastech emails: FROM "nevastech.monitor@gmail.com"
- ✅ Ascent365 emails: FROM "ascent365.monitor@gmail.com"
- ✅ Completely separate Gmail accounts

---

## Option 3: Environment Variables + Config Override

### This is the CURRENT setup:

**Your `.env` file:**
```env
SMTP_USERNAME=nevasai2025@gmail.com
SMTP_PASSWORD=your-app-password-here
```

**Nevastech** (`config/config.yaml`):
```yaml
alerts:
  email:
    smtp_username: ""  # Uses SMTP_USERNAME from .env
    smtp_password: ""  # Uses SMTP_PASSWORD from .env
    from_email: "nevastech.monitor@gmail.com"  # Custom FROM
```

**Ascent365** (`config/ascent365.yaml`):
```yaml
alerts:
  email:
    smtp_username: ""  # Uses SMTP_USERNAME from .env
    smtp_password: ""  # Uses SMTP_PASSWORD from .env
    from_email: "ascent365.reports@gmail.com"  # Custom FROM
```

**Note:** This only works if your Gmail account allows sending from different addresses (Gmail alias feature).

---

## 🎯 Recommended Setup (Easiest)

### Use Option 1: Same Account, Different Display

**Current Setup:**
- SMTP Account: `nevasai2025@gmail.com`
- Both websites use this account
- Change `from_email` in each config

**Nevastech:**
```yaml
from_email: "Nevastech Monitor <nevasai2025@gmail.com>"
```

**Ascent365:**
```yaml
from_email: "Ascent365 Monitor <nevasai2025@gmail.com>"
```

**Emails will show:**
- Nevastech: "FROM: Nevastech Monitor"
- Ascent365: "FROM: Ascent365 Monitor"

---

## 📧 Email Examples

### Nevastech Email:
```
FROM: Nevastech Monitor <nevasai2025@gmail.com>
TO: renderthaniks@gmail.com, prabhu@nevastech.com
SUBJECT: 🌐 Website Health Report — Nevas Technologies (2026-02-13)
```

### Ascent365 Email:
```
FROM: Ascent365 Monitor <nevasai2025@gmail.com>
TO: prabhuofficial2003@gmail.com
SUBJECT: 🌐 Website Health Report — Ascent Innovation (2026-02-13)
```

---

## 🔧 Quick Change

### For Nevastech:

Edit `config/config.yaml` line 30:
```yaml
from_email: "Nevastech Reports <nevasai2025@gmail.com>"
```

### For Ascent365:

Edit `config/ascent365.yaml` line 28:
```yaml
from_email: "Ascent365 Reports <nevasai2025@gmail.com>"
```

### Restart schedulers:
```powershell
# Stop both (Ctrl+C in each window)
# Then start:
.\start_all_monitors.ps1
```

**Done!** Each website now has a different FROM name! ✅

---

## Summary

| Option | Complexity | Use Case |
|--------|------------|----------|
| **Same Account, Different Name** | ⭐ Easy | Same Gmail, different display names |
| **Different Accounts** | ⭐⭐⭐ Hard | Separate Gmail accounts per website |
| **Env + Override** | ⭐⭐ Medium | One account, Gmail aliases |

**Recommended:** Use Option 1 (same account, different display names)!
