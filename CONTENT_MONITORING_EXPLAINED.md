# How Content Change Monitoring Works

## 📖 Complete Guide to Understanding Content Hash Tracking

---

## 🎯 **WHAT IS CONTENT CHANGE MONITORING?**

Content change monitoring **tracks if the text/content on your web pages changes** between checks.

**Think of it like:**
- 📸 Taking a "fingerprint" of your page content
- 💾 Saving that fingerprint
- 🔍 Comparing next time to see if content changed
- 🚨 Alerting you if something is different

---

## 🔧 **HOW IT WORKS - STEP BY STEP:**

### **Step 1: First Check (Creating Baseline)**

**When monitor runs for the FIRST time:**

```
Visit: https://www.nevastech.com/about/

Extract content:
"Nevas Technologies is a leading provider of..."

Calculate hash:
Content → SHA256 Algorithm → "a7b3c8d2e4f1g9h5i2j6k8m0n4p7q9"

Save to database:
Page: /about/
Hash: a7b3c8d2e4f1g9h5i2j6k8m0n4p7q9
Date: 2026-02-16 09:00:00
```

✅ **Baseline created!**

---

### **Step 2: Second Check (Comparison)**

**Next day, monitor runs again:**

```
Visit: https://www.nevastech.com/about/

Extract content:
"Nevas Technologies is a leading provider of..."
(SAME content as yesterday)

Calculate new hash:
Content → SHA256 Algorithm → "a7b3c8d2e4f1g9h5i2j6k8m0n4p7q9"

Compare with saved hash:
Old: a7b3c8d2e4f1g9h5i2j6k8m0n4p7q9
New: a7b3c8d2e4f1g9h5i2j6k8m0n4p7q9

Result: MATCH ✅
```

**Report:** ✅ No content changes detected

---

### **Step 3: Content Was Modified**

**Someone updated the About page:**

```
Visit: https://www.nevastech.com/about/

Extract content:
"Nevas Technologies is a global leader in..."
(Changed "leading" to "global leader")

Calculate new hash:
Content → SHA256 Algorithm → "x2y4z6a8b0c2d4e6f8g0h2i4j6k8m0"

Compare with saved hash:
Old: a7b3c8d2e4f1g9h5i2j6k8m0n4p7q9
New: x2y4z6a8b0c2d4e6f8g0h2i4j6k8m0

Result: DIFFERENT! ⚠️
```

**Report:** 
```
⚠️ Content Changed
Page: /about/
Old Hash: a7b3c8d2...
New Hash: x2y4z6a8...
Change detected on: 2026-02-16 16:30:00
```

---

## 🧮 **WHAT IS A HASH?**

### **Simple Explanation:**

A **hash** is like a **unique fingerprint** for text.

**Example:**

```
Text: "Hello World"
Hash: 64ec88ca00b268e5ba1a35678a1b5316d212f4f366b2477232534a8aeca37f3c

Text: "Hello World!"  (added exclamation)
Hash: c0535e4be2b79ffd93291305436bf889314e4a3faec05ecffcbb7df31ad9e51a
```

**Even ONE character change = COMPLETELY different hash!**

---

### **Hash Properties:**

1. **Unique** - Each content produces unique hash
2. **Consistent** - Same content = Same hash always
3. **One-way** - Can't reverse hash back to original text
4. **Fixed length** - Always same length (64 characters for SHA256)

---

## 📊 **REAL EXAMPLE:**

### **Scenario: Nevastech Homepage**

#### **Monday - First Check:**
```
Content extracted from /
"Welcome to Nevas Technologies
We provide enterprise solutions..."

Hash: a7b3c8d2e4f1g9h5i2j6k8m0n4p7q9

Status: ✅ Baseline created
```

#### **Tuesday - No Changes:**
```
Content extracted from /
"Welcome to Nevas Technologies
We provide enterprise solutions..."

Hash: a7b3c8d2e4f1g9h5i2j6k8m0n4p7q9

Comparison:
Old: a7b3c8d2e4f1g9h5i2j6k8m0n4p7q9
New: a7b3c8d2e4f1g9h5i2j6k8m0n4p7q9

Status: ✅ No changes
```

#### **Wednesday - Content Updated:**
```
Content extracted from /
"Welcome to Nevas Technologies
We provide cutting-edge enterprise solutions..."
(Added "cutting-edge")

Hash: x2y4z6a8b0c2d4e6f8g0h2i4j6k8m0

Comparison:
Old: a7b3c8d2e4f1g9h5i2j6k8m0n4p7q9
New: x2y4z6a8b0c2d4e6f8g0h2i4j6k8m0

Status: ⚠️ CONTENT CHANGED!

Alert sent to: renderthaniks@gmail.com
Subject: Content Change Detected on Nevas Technologies
```

---

## 🎯 **WHAT GETS MONITORED?**

### **Content That's Tracked:**

✅ **Main text content** on the page  
✅ **Headings** (H1, H2, H3)  
✅ **Paragraphs**  
✅ **List items**  
✅ **Navigation text**  

### **What's Ignored:**

❌ HTML tags (only text matters)  
❌ Whitespace/formatting  
❌ Comments in code  
❌ Images (separate check)  
❌ CSS/JavaScript files  

---

## 📁 **WHERE IS DATA STORED?**

### **Hash Storage:**

```
wordpress-monitor/
├── data/
│   └── content_hashes/
│       ├── nevastech.json          # Hashes for Nevastech
│       └── ascent365.json           # Hashes for Ascent365
```

### **Example Hash File:**

**`nevastech.json`**
```json
{
  "/": {
    "hash": "a7b3c8d2e4f1g9h5i2j6k8m0n4p7q9",
    "last_checked": "2026-02-16T09:00:00",
    "last_changed": "2026-02-15T14:30:00"
  },
  "/about/": {
    "hash": "b8c4d9e5f2g0h6i3j7k9m1n5p8q2r4",
    "last_checked": "2026-02-16T09:00:00",
    "last_changed": "2026-02-16T09:00:00"
  },
  "/contact/": {
    "hash": "c9d5e0f3g1h7i4j8k0m2n6p9q3r5s7",
    "last_checked": "2026-02-16T09:00:00",
    "last_changed": "2026-02-10T11:20:00"
  }
}
```

---

## ⚙️ **CONFIGURATION OPTIONS:**

### **In `config/config.yaml`:**

```yaml
content_integrity:
  # Track if content changes
  enable_change_detection: true
  
  # Save screenshot comparisons (visual diff)
  baseline_screenshots: true
  
  # Calculate hash values for content
  hash_critical_content: true
```

---

## 🔔 **WHEN DO YOU GET ALERTS?**

### **Alert Triggers:**

1. **Content Hash Changed** → Email sent
2. **Screenshot Differs** → Email sent (if enabled)
3. **No Changes** → No alert (only in scheduled report)

### **Example Alert Email:**

```
Subject: ⚠️ Content Change Detected - Nevas Technologies

Dear Team,

Content changes have been detected on your website:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 CHANGED PAGES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Page: /about/
Old Hash: a7b3c8d2e4f1g9h5i2j6k8m0n4p7q9
New Hash: x2y4z6a8b0c2d4e6f8g0h2i4j6k8m0
Changed: 2026-02-16 09:15:23

Page: /services/
Old Hash: c9d5e0f3g1h7i4j8k0m2n6p9q3r5s7
New Hash: p1q3r5s7t9u1v3w5x7y9z1a3b5c7d9
Changed: 2026-02-16 09:15:28

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This could indicate:
✓ Intentional content updates
✗ Unauthorized modifications
✗ Potential security breach

Please review these changes.
```

---

## 💡 **USE CASES:**

### **✅ When Content Monitoring is USEFUL:**

1. **Security Monitoring**
   - Detect unauthorized page modifications
   - Catch hacking attempts
   - Monitor for malware injection

2. **Compliance**
   - Legal disclaimers must not change
   - Terms of Service tracking
   - Privacy Policy monitoring

3. **Static Pages**
   - About Us page (rarely changes)
   - Contact information (should be stable)
   - Company policies

4. **Team Coordination**
   - Know when content was updated
   - Track who made changes (if integrated with CMS)
   - Audit trail for modifications

---

### **❌ When Content Monitoring is LESS USEFUL:**

1. **Dynamic Content**
   - News websites (content changes daily)
   - Blogs (new posts frequently)
   - E-commerce (products update often)
   - Pricing pages (prices change)

2. **Marketing Sites**
   - Landing pages (A/B testing)
   - Promotional content (seasonal changes)
   - Homepage banners (rotate frequently)

---

## 🎛️ **HOW TO CUSTOMIZE:**

### **Option 1: Enable for Specific Pages Only**

**Edit your page list in config:**

```yaml
pages_to_monitor:
  - path: "/"
    monitor_content_changes: true      # Monitor homepage
  - path: "/about/"
    monitor_content_changes: true      # Monitor about
  - path: "/blog/"
    monitor_content_changes: false     # Don't monitor blog (changes often)
  - path: "/contact/"
    monitor_content_changes: true      # Monitor contact
```

---

### **Option 2: Set Alert Threshold**

**Only alert if multiple pages change:**

```yaml
content_integrity:
  enable_change_detection: true
  alert_threshold: 3  # Only alert if 3+ pages changed
```

**Use case:** If someone updates 1-2 pages, no alert. If hacker changes many pages, alert!

---

### **Option 3: Ignore Specific Elements**

**Skip dynamic sections:**

```yaml
content_integrity:
  ignore_selectors:
    - ".news-feed"           # Skip news feed (updates daily)
    - ".price-widget"        # Skip pricing (changes often)
    - "#latest-posts"        # Skip latest posts section
```

---

## 📊 **REPORT EXAMPLE:**

### **Daily Report with Content Changes:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 WEBSITE HEALTH REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Website: Nevas Technologies
Date: February 16, 2026, 4:30 PM

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Status: ✅ OPERATIONAL
Uptime: 100%
Response Time: 520ms
Pages Checked: 5
Issues Found: 1 (Content Change)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ CONTENT CHANGES DETECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Page: /about/
Previous Hash: a7b3c8d2e4f1g9h5
Current Hash:  x2y4z6a8b0c2d4e6
Change Time:   09:15:23 AM

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ ALL CHECKS PASSED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Uptime: Site is accessible
✓ Links: All 42 links working
✓ Images: All 15 images loaded
✓ SEO: Meta tags present
✓ SSL: Certificate valid (expires in 89 days)
```

---

## 🔍 **TECHNICAL DETAILS:**

### **Hash Algorithm:**

**SHA-256** (Secure Hash Algorithm 256-bit)

**Properties:**
- **Output:** Always 64 hexadecimal characters
- **Collision resistance:** Virtually impossible to find two different texts with same hash
- **Speed:** Fast to compute (~0.1ms per page)
- **Security:** Cryptographically secure

### **Process Flow:**

```
1. Fetch page HTML
   ↓
2. Extract text content (remove HTML tags)
   ↓
3. Normalize (remove extra spaces, lowercase)
   ↓
4. Calculate SHA-256 hash
   ↓
5. Compare with stored hash
   ↓
6. If different → Alert
   If same → Continue
   ↓
7. Update stored hash with new value
   ↓
8. Save timestamp
```

---

## 🎯 **BEST PRACTICES:**

### **✅ DO:**

1. **Monitor critical pages**
   - Legal notices
   - Contact information
   - About Us
   - Privacy Policy

2. **Set up proper baselines**
   - Run first check when content is correct
   - Review and approve initial hashes

3. **Review change alerts**
   - Don't ignore them!
   - Verify changes are intentional

4. **Keep baselines updated**
   - After intentional updates, new hash becomes baseline

---

### **❌ DON'T:**

1. **Don't monitor highly dynamic content**
   - Blog posts
   - News feeds
   - Product catalogs
   - Pricing tables

2. **Don't panic on alerts**
   - Could be intentional updates
   - Check with your team first

3. **Don't rely solely on hash monitoring**
   - Use with other security measures
   - Not a replacement for proper security

---

## 🛠️ **TROUBLESHOOTING:**

### **Problem: Too Many Alerts**

**Solution:**
- Add dynamic sections to `ignore_selectors`
- Increase `alert_threshold`
- Disable for frequently changing pages

### **Problem: Missing Real Changes**

**Solution:**
- Verify `hash_critical_content: true`
- Check hash storage file exists
- Ensure page is in `pages_to_monitor`

### **Problem: False Positives**

**Causes:**
- Ads rotation (ignore ad sections)
- Timestamps (ignore date/time elements)
- Session data (ignore dynamic content)

---

## ✅ **SUMMARY:**

### **Content Change Monitoring:**

**What:** Tracks if page text content changes  
**How:** Calculates unique hash (fingerprint) of content  
**When:** Every scheduled check  
**Alerts:** Email when content differs from baseline  

### **Current Status:**

| Website | Content Monitoring |
|---------|-------------------|
| **Nevastech** | ✅ Enabled |
| **Ascent365** | ❌ Disabled (no config) |

### **Best For:**

✅ Security monitoring  
✅ Compliance tracking  
✅ Static page integrity  
✅ Unauthorized change detection  

---

**Content change monitoring is now ENABLED and explained!** 🎓

**You now understand how hash-based content tracking works!** 📚
