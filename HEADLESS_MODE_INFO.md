# Headless Mode Configuration

## ✅ Scheduler Now Runs in Headless Mode

Your WordPress Monitor scheduler is now configured to **always run in headless mode**. This means:

### What is Headless Mode?

**Headless mode** = Monitoring runs in the background with **no visible browser windows**

This is perfect for:
- ✓ **Automated scheduling** - No interruptions while you work
- ✓ **Server deployments** - Can run on servers without displays
- ✓ **Background operation** - Silent monitoring 24/7
- ✓ **Resource efficiency** - Uses less memory without rendering UI

---

## 🔧 Current Configuration

### Scheduler Settings

The scheduler (`scheduler.py`) is now configured to:

```python
result = monitor.run_all_checks(
    use_browser=False,  # Uses fast HTTP requests (no browser needed)
    headless=True       # If browser is needed, runs invisible
)
```

**What this means:**
1. **HTTP Mode (Default)**: Uses fast HTTP requests - no browser at all
2. **Headless Browser (If Needed)**: If browser is required for certain checks, it runs invisibly

---

## 🎯 Benefits

### For Scheduled Automation
- **No Pop-ups**: Browser windows won't interrupt your work
- **Silent Operation**: Runs completely in background
- **Unattended**: Can run while you're away
- **Server-Ready**: Works on headless servers (no GUI needed)

### For Performance
- **Faster**: HTTP mode is quicker than browser
- **Less Memory**: No browser UI rendering
- **More Stable**: Fewer dependencies on display drivers

---

## 📊 Monitoring Modes

Your system now uses the most efficient mode for each task:

| Check Type | Mode | Visible Browser? |
|------------|------|------------------|
| **Scheduled Checks** | HTTP + Headless | ❌ No |
| **Link Checking** | HTTP | ❌ No |
| **Image Checking** | HTTP | ❌ No |
| **Uptime Monitoring** | HTTP | ❌ No |
| **PDF Generation** | Headless Browser | ❌ No |
| **Manual CLI Checks** | HTTP (default) | ❌ No |

---

## 🚀 Running the Scheduler

Start the scheduler - it will run silently in the background:

```powershell
python scheduler.py
```

**You'll see in logs:**
```
2026-02-12 11:07:00 - INFO - Starting scheduled check
2026-02-12 11:07:00 - INFO - Running in HEADLESS mode (no visible browser windows)
2026-02-12 11:07:15 - INFO - Check completed: 3 issues found
2026-02-12 11:07:18 - INFO - PDF generated
2026-02-12 11:07:22 - INFO - Report PDF emailed successfully
```

**No browser windows will appear!** ✓

---

## 🔄 Override Headless Mode (Manual Testing Only)

If you ever need to **see the browser** for debugging (manual use only):

### CLI Manual Check with Visible Browser
```powershell
# This will show the browser (for debugging)
python cli.py --check full --browser --no-headless
```

### Note
The scheduler **always uses headless mode** and cannot be overridden. This is by design for stable automated operation.

---

## 📝 Log Monitoring

Since everything runs invisibly, monitor progress via logs:

```powershell
# Real-time log viewing
Get-Content logs\scheduler.log -Wait -Tail 20

# View all logs
Get-Content logs\scheduler.log
```

---

## ✅ Summary

Your scheduler is now configured for optimal background operation:

- ✓ **Headless Mode Enabled** - No visible windows
- ✓ **HTTP Mode Default** - Fast and efficient  
- ✓ **Silent Operation** - Runs in background
- ✓ **Daily Schedule** - 11:07 AM Asia/Kolkata
- ✓ **Auto Email** - PDF reports to clients
- ✓ **Full Logging** - All activity tracked

Perfect for unattended, automated website monitoring! 🚀
