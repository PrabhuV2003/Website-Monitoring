# Scheduler Browser Configuration

## Current Configuration: ✅ **Headless Browser Mode**

The scheduler is now configured to **always use a headless browser** (Playwright) for all scheduled checks.

---

## What Changed

### Before (HTTP Requests Only):
```python
result = monitor.run_all_checks(
    use_browser=False,  # Use HTTP requests (faster but limited)
    headless=True       # Not applicable
)
```

**Limitations:**
- ❌ No JavaScript execution
- ❌ Cannot test forms
- ❌ No screenshot capture
- ❌ Limited content verification
- ❌ No dynamic content detection

### After (Headless Browser):
```python
result = monitor.run_all_checks(
    use_browser=True,   # Use headless browser
    headless=True       # Run invisibly in background
)
```

**Benefits:**
- ✅ Full JavaScript execution
- ✅ Form testing capabilities
- ✅ Screenshot capture
- ✅ Comprehensive content verification
- ✅ Dynamic content detection
- ✅ Real browser environment
- ✅ More accurate testing

---

## How It Works

### Headless Mode Explained:

**Headless Browser** = A real browser (Chromium) that runs **without a visible window**

- 🌐 **Full Browser Features**: Renders pages, executes JavaScript, loads all resources
- 👻 **Invisible**: Runs in the background, no windows pop up
- 🚀 **Automated**: Perfect for scheduled tasks
- 📊 **Comprehensive**: Captures screenshots, measures performance, tests forms

### What This Means for Your Checks:

When the scheduler runs at **13:07 daily**, it will:

1. **Launch Chromium** (invisibly in background)
2. **Navigate to your website** (https://www.ascent365.com)
3. **Execute all checks**:
   - ✅ Page loading and performance
   - ✅ JavaScript execution
   - ✅ Content integrity verification
   - ✅ Link checking (all pages)
   - ✅ Image loading times
   - ✅ SEO checks
   - ✅ SSL certificate validation
   - ✅ Form accessibility (if configured)
   - ✅ Screenshot capture
4. **Generate PDF report**
5. **Email report** to recipients
6. **Close browser** automatically

**You won't see any browser windows** - it all happens in the background! 🎩✨

---

## Performance Considerations

### Speed:
- **HTTP Requests**: ~30-60 seconds for basic checks
- **Headless Browser**: ~2-5 minutes for comprehensive checks

### Resource Usage:
- **Memory**: ~200-500 MB during check
- **CPU**: Moderate during execution
- **Disk**: Screenshots and PDFs saved to reports folder

### When Browser Runs:
- Only during scheduled checks (daily at 13:07)
- Browser closes automatically after check completes
- No persistent background processes

---

## Browser Installation

The headless browser (Chromium) is installed via Playwright:

```powershell
# If not already installed, run:
playwright install chromium
```

**Location**: `C:\Users\Nevas\AppData\Local\ms-playwright\`

---

## Switching Back to HTTP Mode (If Needed)

If you want faster checks but less comprehensive testing, edit `scheduler.py`:

```python
# Line 78 - Change this:
use_browser=True,   # Use headless browser

# To this:
use_browser=False,  # Use HTTP requests
```

Then restart the scheduler.

---

## Monitoring Browser Activity

### Check Logs:
```powershell
# View real-time logs
Get-Content -Path logs\scheduler.log -Wait -Tail 50
```

Look for:
```
Running with HEADLESS BROWSER (invisible browser for comprehensive checks)
```

### Check Screenshots:
After each run, screenshots are saved to:
```
reports\screenshots\
```

### Check Reports:
HTML and PDF reports are saved to:
```
reports\
```

---

## Troubleshooting

### "Browser not found" Error:
```powershell
playwright install chromium
```

### Browser Process Stuck:
```powershell
# Find chromium processes
Get-Process | Where-Object {$_.Name -like "*chromium*"}

# Kill if needed
Stop-Process -Name chromium -Force
```

### Slow Performance:
- Browser mode is slower than HTTP requests (this is normal)
- Each page requires full rendering with JavaScript
- Expected: 2-5 minutes per full check

---

## Configuration Summary

| Setting | Value | Impact |
|---------|-------|--------|
| **Mode** | Headless Browser | Most comprehensive checks |
| **Visibility** | Invisible | No browser windows shown |
| **Schedule** | Daily at 13:07 | Automated background execution |
| **Browser** | Chromium (via Playwright) | Real browser environment |
| **Checks** | Full suite | JavaScript, forms, screenshots, etc. |
| **Reports** | PDF + HTML | Automatically generated and emailed |

---

## Benefits for Ascent365 Monitoring

Using headless browser ensures:

1. **Accurate Testing**: Real user experience simulation
2. **JavaScript Validation**: All dynamic content checked
3. **Visual Verification**: Screenshots capture actual appearance
4. **Form Testing**: Can verify form accessibility (if configured)
5. **Performance Metrics**: Real-world loading times
6. **Comprehensive Reports**: More detailed insights

---

## Summary

✅ **Scheduler now runs with headless browser**  
✅ **No visible windows** - completely automated  
✅ **Comprehensive checks** - JavaScript, forms, screenshots  
✅ **Same schedule** - Daily at 13:07 (Asia/Kolkata)  
✅ **Automatic PDF reports** - Emailed to recipients  

**The scheduler will provide more thorough and accurate website monitoring using a real browser environment!** 🚀
