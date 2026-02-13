# Scheduler Timing - How It Works

## 📅 Your Current Configuration

```yaml
schedule:
  check_interval: "daily"
  check_time: "14:57"      # 2:57 PM
  timezone: "Asia/Kolkata"
```

---

## ⏰ **How the Daily Schedule Works**

### **Your Question:**
> "If I schedule a run at 15:00 and it completes successfully, when will it run again automatically?"

### **Answer:**
**It will run at 15:00 the NEXT DAY (tomorrow)** ✅

---

## 📊 **Schedule Behavior Explained**

### **Daily Schedule Pattern:**

```
Day 1:
├─ 15:00 → Check runs (takes ~5-10 minutes with browser)
├─ 15:10 → Check completes successfully
├─ 15:10 to 23:59 → Scheduler waits...
└─ (Next scheduled run: Tomorrow at 15:00)

Day 2:
├─ 15:00 → Check runs again automatically
├─ 15:10 → Check completes
└─ (Next run: Day 3 at 15:00)

Day 3:
├─ 15:00 → Check runs again
└─ ... continues daily
```

---

## 🔁 **When Does It Run Automatically?**

| Current Time | What Happens | Next Run |
|-------------|--------------|----------|
| **14:30** | Scheduler starts | Today at **15:00** |
| **15:00** | Check runs NOW | Tomorrow at **15:00** |
| **15:05** | Check still running... | Tomorrow at **15:00** |
| **15:10** | Check completes ✅ | Tomorrow at **15:00** |
| **16:00** | Nothing (waiting) | Tomorrow at **15:00** |
| **20:00** | Nothing (waiting) | Tomorrow at **15:00** |
| **Next day 15:00** | Check runs AGAIN | Day after at **15:00** |

---

## 🎯 **Key Points:**

1. **"daily" = Once per day** at the specified time
2. **Runs at the SAME time every day** (15:00 in your case)
3. **Keeps running forever** until you stop it with Ctrl+C
4. **If check takes 10 minutes**, next run is still at 15:00 tomorrow, not 10 minutes later

---

## 📖 **Real-World Example**

### **Today (Feb 12, 2026):**

```
Current time: 14:57 (2:57 PM)
Scheduler config: check_time: "14:57"

Timeline:
14:57:00 → ⚡ Check starts
14:57:05 → 🌐 Browser launches (headless)
14:58:30 → 📊 Running all checks
15:02:45 → 📄 Generating PDF
15:03:10 → 📧 Sending email
15:03:15 → ✅ Check complete

15:03:16 → 😴 Scheduler waits...
16:00:00 → 😴 Still waiting...
20:00:00 → 😴 Still waiting...
23:59:59 → 😴 Still waiting...
```

### **Tomorrow (Feb 13, 2026):**

```
14:56:59 → 😴 Still waiting...
14:57:00 → ⚡ Check starts AGAIN!
14:57:05 → 🌐 Browser launches
... (repeats the process)
```

---

## 🔄 **Different Schedule Options**

You can change the schedule in `config.yaml`:

### **Option 1: Daily (Current)**
```yaml
check_interval: "daily"
check_time: "15:00"     # Runs every day at 3:00 PM
```
**Runs:** Once per day at 15:00

### **Option 2: Hourly**
```yaml
check_interval: "hourly"
check_time: "00:30"     # Minutes past the hour
```
**Runs:** Every hour at 30 minutes past (1:30, 2:30, 3:30, etc.)

### **Option 3: Every X Minutes**
```yaml
check_interval: "*/30"  # Every 30 minutes
check_time: "00:00"     # Ignored for interval schedules
```
**Runs:** Every 30 minutes (15:00, 15:30, 16:00, 16:30, etc.)

### **Option 4: Multiple Times Per Day (Advanced)**
```yaml
check_interval: "0 9,15,21 * * *"  # Cron expression
check_time: "09:00"                # Not used for cron
```
**Runs:** Three times daily: 9:00 AM, 3:00 PM, 9:00 PM

---

## 🕐 **Current Time vs Schedule**

**Right now:** 14:57 (2:57 PM)  
**Your schedule:** check_time: "14:57"  

**If you start the scheduler NOW:**
- It will run **immediately** (at 14:57)
- Then wait until **tomorrow at 14:57**

**If you start at 15:30 (after scheduled time):**
- It will **wait until tomorrow at 14:57**
- Won't run today since 14:57 already passed

---

## 📅 **Viewing Next Scheduled Run**

When you start the scheduler, you'll see:

```
Scheduler configured: daily at 14:57 (Asia/Kolkata)
```

APScheduler calculates the next run time automatically. To see it, you can check the logs:

```powershell
# View scheduler logs
Get-Content -Path logs\scheduler.log -Tail 20
```

Look for lines like:
```
Added job "wordpress_monitor" to job store "default"
Next run at: 2026-02-13 14:57:00 IST
```

---

## 🛑 **What Stops the Automatic Runs?**

The scheduler will keep running daily **FOREVER** until one of these happens:

1. ❌ You press **Ctrl+C**
2. ❌ Computer shuts down / restarts
3. ❌ Terminal window closes
4. ❌ Power outage
5. ❌ System crash
6. ❌ Task killed via Task Manager

**Otherwise:** Runs every day at the scheduled time indefinitely! ♾️

---

## 💡 **To Keep It Running 24/7**

### **Option 1: Keep Terminal Open**
- Leave the terminal window open
- Don't close your laptop

### **Option 2: Windows Task Scheduler (Recommended for Production)**
Create a Windows scheduled task to start the script on boot:

```powershell
# Create a scheduled task (run as admin)
$action = New-ScheduledTaskAction -Execute "python" -Argument "C:\Users\Nevas\.gemini\antigravity\scratch\wordpress-monitor\scheduler.py" -WorkingDirectory "C:\Users\Nevas\.gemini\antigravity\scratch\wordpress-monitor"
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "WordPressMonitor" -Action $action -Trigger $trigger -Settings $settings -User "SYSTEM"
```

### **Option 3: Windows Service**
- Convert to a Windows service (more advanced)
- Runs in background even when logged out

---

## 📝 **Summary**

### **Your Current Setup:**

| Setting | Value | Meaning |
|---------|-------|---------|
| **Interval** | `daily` | Once per day |
| **Time** | `14:57` | 2:57 PM |
| **Timezone** | `Asia/Kolkata` | Indian Standard Time |
| **Frequency** | Every 24 hours | Same time daily |

### **Schedule Flow:**

```
Start → Run at 14:57 → Complete → Wait 24h → Run at 14:57 → ...
```

### **Example Timeline:**

- **Today 14:57** → Runs
- **Tomorrow 14:57** → Runs
- **Day after 14:57** → Runs
- **Every day 14:57** → Runs

**As long as the terminal stays open, it runs daily automatically!** 🔄

---

## 🎯 **Quick Answers**

**Q: When is the next run after it completes successfully?**  
A: Exactly **24 hours** from the scheduled time (tomorrow at 14:57)

**Q: Does it run multiple times if I don't stop it?**  
A: Yes! Runs **every day** at 14:57 until you stop it

**Q: What if the check takes 30 minutes?**  
A: Next run is still **tomorrow at 14:57** (not 30 minutes later)

**Q: Can I change the time to 15:00?**  
A: Yes! Edit `config.yaml` → `check_time: "15:00"` → Restart scheduler

**Q: Do I need to restart the scheduler daily?**  
A: No! Once started, it runs **automatically every day** ✨

---

**Bottom line: Set it and forget it! The scheduler handles everything automatically.** 🚀
