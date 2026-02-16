# Content Change Monitoring - Enabled for Both Websites

## ✅ DONE - Content Monitoring Active for Nevastech & Ascent365!

---

## 🎯 **WHAT WAS ADDED:**

Content change monitoring is now **enabled for BOTH websites:**
- ✅ **Nevastech** - Already had it enabled
- ✅ **Ascent365** - Just enabled!

---

## ⚙️ **CONFIGURATION:**

### **Nevastech** (`config/config.yaml`):
```yaml
content_integrity:
  enable_change_detection: true    # ✅ Tracks content changes
  baseline_screenshots: true       # ✅ Saves baseline screenshots
  hash_critical_content: true      # ✅ Hash value tracking
```

### **Ascent365** (`config/ascent365.yaml`):
```yaml
content_integrity:
  enable_change_detection: true    # ✅ Tracks content changes
  baseline_screenshots: true       # ✅ Saves baseline screenshots
  hash_critical_content: true      # ✅ Hash value tracking
```

**Both configs now identical!** ✅

---

## 📊 **WHAT WILL HAPPEN:**

### **Nevastech Monitoring:**

**Pages Monitored:**
- `/` (Homepage)
- `/company/about-us/`
- `/company/careers/`
- All configured pages

**Daily Check at 4:30 PM:**
1. Visit each page
2. Extract text content
3. Calculate hash (fingerprint)
4. Compare with saved hash
5. If different → Email alert!

---

### **Ascent365 Monitoring:**

**Pages Monitored:**
- `/` (Homepage)
- `/about/` (About page)

**Daily Check at 6:00 AM:**
1. Visit each page
2. Extract text content
3. Calculate hash (fingerprint)
4. Compare with saved hash
5. If different → Email alert!

---

## 📧 **EMAIL ALERTS:**

### **When Will You Get Alerts?**

**Nevastech:**
```
To: renderthaniks@gmail.com, prabhu@nevastech.com
Subject: ⚠️ Content Change - Nevas Technologies

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 CHANGED PAGES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Page: /company/about-us/
Old Hash: a7b3c8d2e4f1g9h5
New Hash: x2y4z6a8b0c2d4e6
Changed: 2026-02-16 16:30:05

This could indicate:
✓ Intentional content updates
✗ Unauthorized modifications
✗ Potential security breach

Please review!
```

**Ascent365:**
```
To: prabhuofficial2003@gmail.com
Subject: ⚠️ Content Change - Ascent Innovation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 CHANGED PAGES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Page: /about/
Old Hash: c9d5e0f3g1h7i4j8
New Hash: p1q3r5s7t9u1v3w5
Changed: 2026-02-16 06:05:12

This could indicate:
✓ Intentional content updates
✗ Unauthorized modifications
✗ Potential security breach

Please review!
```

---

## 💾 **DATA STORAGE:**

Hash values will be stored separately for each website:

```
wordpress-monitor/
├── data/
│   └── content_hashes/
│       ├── nevastech.json          # Nevastech hashes
│       └── ascent365.json           # Ascent365 hashes
```

### **Example: nevastech.json**
```json
{
  "/": {
    "hash": "a7b3c8d2e4f1g9h5i2j6k8m0n4p7q9",
    "last_checked": "2026-02-16T16:30:00",
    "last_changed": "2026-02-15T14:30:00"
  },
  "/company/about-us/": {
    "hash": "b8c4d9e5f2g0h6i3j7k9m1n5p8q2r4",
    "last_checked": "2026-02-16T16:30:00",
    "last_changed": "2026-02-16T16:30:00"
  }
}
```

### **Example: ascent365.json**
```json
{
  "/": {
    "hash": "c9d5e0f3g1h7i4j8k0m2n6p9q3r5s7",
    "last_checked": "2026-02-16T06:00:00",
    "last_changed": "2026-02-16T06:00:00"
  },
  "/about/": {
    "hash": "d0e6f4g2h8i5j9k1m3n7p0q4r6s8t2",
    "last_checked": "2026-02-16T06:00:00",
    "last_changed": "2026-02-10T11:20:00"
  }
}
```

---

## 🔄 **FIRST RUN - BASELINE CREATION:**

### **What Happens on First Check:**

**Nevastech (Next run at 4:30 PM):**
```
Checking /
→ Creating baseline for /
→ Hash: a7b3c8d2e4f1g9h5
→ ✅ Baseline saved

Checking /company/about-us/
→ Creating baseline for /company/about-us/
→ Hash: b8c4d9e5f2g0h6i3
→ ✅ Baseline saved

Status: ✅ Baselines created
No alerts sent (first run)
```

**Ascent365 (Next run at 6:00 AM tomorrow):**
```
Checking /
→ Creating baseline for /
→ Hash: c9d5e0f3g1h7i4j8
→ ✅ Baseline saved

Checking /about/
→ Creating baseline for /about/
→ Hash: d0e6f4g2h8i5j9k1
→ ✅ Baseline saved

Status: ✅ Baselines created
No alerts sent (first run)
```

**First run = No alerts** (just creates baselines)

---

## 🚨 **SUBSEQUENT RUNS - CHANGE DETECTION:**

### **Example: Someone Updates Ascent365 About Page**

**Before:**
```
Page: /about/
Content: "Ascent365 is a leading company..."
Hash: d0e6f4g2h8i5j9k1
```

**After Edit:**
```
Page: /about/
Content: "Ascent365 is a GLOBAL leader..."
Hash: p1q3r5s7t9u1v3w5
```

**Monitor Detects:**
```
Checking /about/
Old Hash: d0e6f4g2h8i5j9k1
New Hash: p1q3r5s7t9u1v3w5
Result: ⚠️ DIFFERENT!

Action:
1. Save new hash
2. Send alert email
3. Log change timestamp
```

**You get email alert immediately!** 📧

---

## 🎯 **USE CASES:**

### **Why Monitor Both Websites?**

| Website | Pages | Content Type | Change Frequency |
|---------|-------|--------------|------------------|
| **Nevastech** | 8+ pages | Corporate info, services | Low (monthly) |
| **Ascent365** | 2 pages | About, contact | Very low (quarterly) |

**Both are good candidates for content monitoring!** ✅

### **Benefits:**

1. **Security**
   - ✅ Detect unauthorized edits
   - ✅ Catch hacking attempts
   - ✅ Find malware injection

2. **Compliance**
   - ✅ Track legal content changes
   - ✅ Monitor terms of service
   - ✅ Audit trail

3. **Coordination**
   - ✅ Know when content updated
   - ✅ Team accountability
   - ✅ Change history

---

## 📊 **MONITORING SCHEDULE:**

| Website | Check Time | Email To | Hash Tracking |
|---------|------------|----------|---------------|
| **Nevastech** | 4:30 PM daily | renderthaniks@gmail.com<br>prabhu@nevastech.com | ✅ Enabled |
| **Ascent365** | 6:00 AM daily | prabhuofficial2003@gmail.com | ✅ Enabled |

---

## 🧪 **TEST IT:**

### **Test Nevastech:**
```powershell
python test_email_nevastech.py
```

**First run output:**
```
Creating content baseline for /
Hash: a7b3c8d2e4f1g9h5
✅ Baseline saved

Creating content baseline for /company/about-us/
Hash: b8c4d9e5f2g0h6i3
✅ Baseline saved
```

### **Test Ascent365:**
```powershell
python test_email_ascent365.py
```

**First run output:**
```
Creating content baseline for /
Hash: c9d5e0f3g1h7i4j8
✅ Baseline saved

Creating content baseline for /about/
Hash: d0e6f4g2h8i5j9k1
✅ Baseline saved
```

---

## 🔧 **CUSTOMIZATION (Optional):**

### **If You Want to Skip Certain Sections:**

**Example: Skip dynamic news section on Nevastech:**

Edit `config/config.yaml`:
```yaml
content_integrity:
  enable_change_detection: true
  baseline_screenshots: true
  hash_critical_content: true
  ignore_selectors:            # Add this
    - ".news-feed"             # Skip news feed
    - "#latest-updates"        # Skip updates section
```

### **If You Want Page-Specific Settings:**

```yaml
pages_to_monitor:
  - path: "/"
    monitor_content_changes: true      # Monitor homepage
  - path: "/blog/"
    monitor_content_changes: false     # Don't monitor blog
```

---

## 📋 **REPORT EXAMPLE:**

### **Daily Report with Content Change:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 WEBSITE HEALTH REPORT - Ascent Innovation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Date: February 16, 2026, 6:00 AM

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: ✅ OPERATIONAL
Uptime: 100%
Response Time: 380ms
Pages Checked: 2
Issues Found: 1 (Content Change)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ CONTENT CHANGES DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Page: /about/
Previous Hash: d0e6f4g2h8i5j9k1
Current Hash:  p1q3r5s7t9u1v3w5
Change Time:   06:05:12 AM

Possible causes:
• Intentional content update
• Unauthorized modification
• Security breach

ACTION REQUIRED: Review this change

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ ALL OTHER CHECKS PASSED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Uptime: Site is accessible
✓ Links: All 12 links working
✓ Images: All 8 images loaded
✓ SEO: Meta tags present
✓ SSL: Certificate valid
```

---

## 🚀 **WHEN DOES IT TAKE EFFECT?**

### **Windows (Local Testing):**
✅ **Immediately!** Next test run will use new settings.

```powershell
python test_email_ascent365.py
```

### **VPS (Production):**
After git push:

```bash
cd ~/wordpress-monitor
git pull

# Restart Ascent365 scheduler
sudo systemctl restart wordpress-monitor-ascent365

# Check it started
sudo systemctl status wordpress-monitor-ascent365
```

---

## ✅ **SUMMARY:**

### **What Changed:**
- ✅ Added `content_integrity` section to `config/ascent365.yaml`
- ✅ Enabled content change detection
- ✅ Enabled baseline screenshots
- ✅ Enabled hash tracking

### **Current Status:**

| Website | Content Monitoring | Pages Monitored |
|---------|-------------------|-----------------|
| **Nevastech** | ✅ Enabled | 8+ pages |
| **Ascent365** | ✅ **Enabled (NEW!)** | 2 pages |

### **Benefits:**
- ✅ Both websites now protected
- ✅ Detect unauthorized changes
- ✅ Security monitoring for both
- ✅ Complete audit trail

---

## 📖 **RELATED DOCUMENTATION:**

- **How it works:** `CONTENT_MONITORING_EXPLAINED.md`
- **Social media exclusions:** `SOCIAL_MEDIA_EXCLUSIONS.md`
- **VPS deployment:** `VPS_DEPLOY_WITH_GITHUB.md`

---

**Content change monitoring is now ACTIVE for BOTH websites!** 🎉

**Nevastech & Ascent365 are both protected!** ✅
