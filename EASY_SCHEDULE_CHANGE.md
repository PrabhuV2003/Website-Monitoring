# EASY Way to Change Schedule Time

## ✅ Super Simple - Just Edit 1 File!

You only need to edit the **config file**. That's it!

---

## For Ascent365

### 1. Open this file:
```
config/ascent365.yaml
```

### 2. Find this line (around line 17):
```yaml
check_time: "06:00"
```

### 3. Change it to your desired time:
```yaml
check_time: "09:30"    # 9:30 AM
```
OR
```yaml
check_time: "14:00"    # 2:00 PM
```
OR
```yaml
check_time: "18:45"    # 6:45 PM
```

### 4. Save the file

### 5. Restart the scheduler:
- Press **Ctrl+C** in the Ascent365 window
- Run: `python scheduler_ascent365.py`

**DONE!** ✅

---

## For Nevastech

### 1. Open this file:
```
config/config.yaml
```

### 2. Find this line (around line 19):
```yaml
check_time: "16:30"
```

### 3. Change it to your desired time:
```yaml
check_time: "10:00"    # 10:00 AM
```

### 4. Save the file

### 5. Restart the scheduler:
- Press **Ctrl+C** in the Nevastech window
- Run: `python scheduler_nevastech.py`

**DONE!** ✅

---

## Time Format Guide

Use **24-hour format** with quotes around it:

| What You Want | Write This |
|---------------|------------|
| Midnight (12:00 AM) | `"00:00"` |
| 6:00 AM | `"06:00"` |
| 8:30 AM | `"08:30"` |
| 12:00 PM (Noon) | `"12:00"` |
| 2:15 PM | `"14:15"` |
| 4:30 PM | `"16:30"` |
| 6:00 PM | `"18:00"` |
| 9:45 PM | `"21:45"` |
| 11:59 PM | `"23:59"` |

---

## Complete Example

Let's change **Ascent365** from **6:00 AM** to **10:15 AM**:

### Step 1: Open `config/ascent365.yaml`

### Step 2: Find and change:
```yaml
# BEFORE:
  check_time: "06:00"

# AFTER:  
  check_time: "10:15"
```

### Step 3: Save file (Ctrl+S)

### Step 4: In Ascent365 window:
```powershell
# Press Ctrl+C
# Then:
python scheduler_ascent365.py
```

### Step 5: Done! ✅

The scheduler will now run at 10:15 AM every day!

---

## That's It!

**3 simple steps:**
1. ✅ Edit config file (`check_time: "HH:MM"`)
2. ✅ Save
3. ✅ Restart scheduler

**No Python code editing required!** 🎉
