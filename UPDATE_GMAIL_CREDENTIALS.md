# Where to Update Gmail Credentials

## ✅ Setup Complete with Dummy Credentials

I've configured both websites with **placeholder credentials**. You need to update them with your actual Gmail accounts and App Passwords.

---

## 📝 **What to Update:**

### **File 1: Nevastech** (`config/config.yaml`)

**Open:** `config/config.yaml`  
**Find lines 28-30:**

```yaml
# NEVASTECH EMAIL ACCOUNT - UPDATE THESE VALUES
smtp_username: "nevastech.monitor@gmail.com"  # UPDATE: Your Gmail for Nevastech
smtp_password: "your-app-password-here"       # UPDATE: App Password from Gmail
from_email: "nevastech.monitor@gmail.com"     # UPDATE: Same as smtp_username
```

**Replace with YOUR values:**

```yaml
# NEVASTECH EMAIL ACCOUNT - UPDATE THESE VALUES
smtp_username: "your-nevastech-email@gmail.com"  # Your actual Gmail
smtp_password: "abcd efgh ijkl mnop"              # Your actual App Password
from_email: "your-nevastech-email@gmail.com"      # Same as smtp_username
```

---

### **File 2: Ascent365** (`config/ascent365.yaml`)

**Open:** `config/ascent365.yaml`  
**Find lines 26-29:**

```yaml
# ASCENT365 EMAIL ACCOUNT - UPDATE THESE VALUES
smtp_username: "ascent365.monitor@gmail.com"  # UPDATE: Your Gmail for Ascent365
smtp_password: "your-app-password-here"       # UPDATE: App Password from Gmail
from_email: "ascent365.monitor@gmail.com"     # UPDATE: Same as smtp_username
```

**Replace with YOUR values:**

```yaml
# ASCENT365 EMAIL ACCOUNT - UPDATE THESE VALUES
smtp_username: "your-ascent365-email@gmail.com"  # Your actual Gmail
smtp_password: "wxyz abcd efgh ijkl"             # Your actual App Password
from_email: "your-ascent365-email@gmail.com"     # Same as smtp_username
```

---

## 🔑 **How to Get App Passwords:**

### **Step 1: For Nevastech Gmail Account**

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in to the Gmail account you want to use for Nevastech
3. Select app: "Mail"
4. Select device: "Other (custom name)" → Type "WordPress Monitor Nevastech"
5. Click "Generate"
6. **Copy the 16-character password** (looks like: `abcd efgh ijkl mnop`)
7. Paste it into `config/config.yaml` at `smtp_password`

### **Step 2: For Ascent365 Gmail Account**

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in to a DIFFERENT Gmail account for Ascent365
3. Select app: "Mail"
4. Select device: "Other (custom name)" → Type "WordPress Monitor Ascent365"
5. Click "Generate"
6. **Copy the 16-character password**
7. Paste it into `config/ascent365.yaml` at `smtp_password`

---

## 📧 **Example: Real Credentials**

### **Nevastech** (`config/config.yaml`):
```yaml
smtp_username: "nevasai2025@gmail.com"
smtp_password: "abcd efgh ijkl mnop"
from_email: "nevasai2025@gmail.com"
```

### **Ascent365** (`config/ascent365.yaml`):
```yaml
smtp_username: "ascent.reports@gmail.com"
smtp_password: "wxyz abcd efgh ijkl"
from_email: "ascent.reports@gmail.com"
```

---

## ⚠️ **Important Notes:**

1. **App Password ≠ Regular Password**
   - Don't use your regular Gmail password
   - Use the 16-character App Password from Google

2. **2-Step Verification Required**
   - You MUST enable 2-Step Verification before you can create App Passwords
   - Go to: https://myaccount.google.com/security

3. **Keep Passwords Secure**
   - Never share your App Passwords
   - The config files contain sensitive data

4. **Same Email for Both?**
   - If you want to use the SAME Gmail for both, that's OK
   - Just use the same credentials in both config files
   - But you won't see different FROM addresses

---

## 🎯 **Quick Summary:**

| File | Lines to Update | What to Change |
|------|----------------|----------------|
| `config/config.yaml` | 28-30 | Nevastech Gmail & App Password |
| `config/ascent365.yaml` | 26-29 | Ascent365 Gmail & App Password |

---

## ✅ **After Updating:**

1. Save both config files
2. Restart both schedulers:
   ```powershell
   # Stop both (Ctrl+C in each window)
   # Then restart:
   .\start_all_monitors.ps1
   ```

3. Test by running:
   ```powershell
   .\test_ascent365_now.ps1
   ```

4. Check if email arrives with correct FROM address

---

## 🔍 **Current Dummy Values:**

**Nevastech:**
- Email: `nevastech.monitor@gmail.com` ← CHANGE THIS
- Password: `your-app-password-here` ← CHANGE THIS

**Ascent365:**
- Email: `ascent365.monitor@gmail.com` ← CHANGE THIS
- Password: `your-app-password-here` ← CHANGE THIS

---

**When you're ready, update these 2 files with your real Gmail credentials!**
