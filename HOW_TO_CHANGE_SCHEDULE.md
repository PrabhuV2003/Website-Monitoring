# How to Change Scheduling Time

## Quick Guide

To change the schedule time for any website, you need to edit **2 places**:

1. The **scheduler Python file** (required)
2. The **config YAML file** (optional, for reference)

---

## For Ascent365 (Currently 6:00 AM)

### Step 1: Edit the Scheduler File

**File:** `scheduler_ascent365.py`

**Find this section (around line 148-155):**

```python
# Add job: Daily at 6:00 AM
scheduler.add_job(
    run_check_and_email,
    trigger=CronTrigger(
        hour=6,      # <-- CHANGE THIS (0-23, 24-hour format)
        minute=0,    # <-- CHANGE THIS (0-59)
        timezone='Asia/Kolkata'
    ),
    id='ascent365_daily_check',
    name='Ascent365 Daily Check at 6:00 AM',
    replace_existing=True
)
```

**Change the `hour` and `minute` values:**

- `hour=6` means 6:00 AM
- `minute=0` means on the hour (00 minutes)

### Step 2: Edit the Config File (Optional)

**File:** `config/ascent365.yaml`

**Find this section:**

```yaml
# Monitoring Schedule
schedule:
  check_interval: "daily"
  check_time: "06:00"      # <-- CHANGE THIS (HH:MM format)
  timezone: "Asia/Kolkata"
```

Change `check_time` to your desired time in 24-hour format.

### Step 3: Restart the Scheduler

1. Go to the Ascent365 scheduler window
2. Press **Ctrl+C** to stop it
3. Restart: `python scheduler_ascent365.py`

---

## For Nevastech (Currently 4:30 PM)

### Step 1: Edit the Scheduler File

**File:** `scheduler_nevastech.py`

**Find this section:**

```python
# Add job: Daily at specific time
scheduler.add_job(
    run_check_and_email,
    trigger=CronTrigger(
        hour=16,     # <-- CHANGE THIS (16 = 4:00 PM)
        minute=30,   # <-- CHANGE THIS
        timezone='Asia/Kolkata'
    ),
    id='nevastech_daily_check',
    name='Nevastech Daily Check',
    replace_existing=True
)
```

**Change the `hour` and `minute` values.**

### Step 2: Edit the Config File (Optional)

**File:** `config/config.yaml`

```yaml
# Monitoring Schedule
schedule:
  check_interval: "daily"
  check_time: "16:30"      # <-- CHANGE THIS
  timezone: "Asia/Kolkata"
```

### Step 3: Restart the Scheduler

1. Go to the Nevastech scheduler window
2. Press **Ctrl+C** to stop it
3. Restart: `python scheduler_nevastech.py`

---

## Time Examples

### Common Schedule Times:

| Time | Hour Value | Minute Value | Description |
|------|------------|--------------|-------------|
| 12:00 AM (Midnight) | `hour=0` | `minute=0` | Start of day |
| 6:00 AM | `hour=6` | `minute=0` | Early morning |
| 9:00 AM | `hour=9` | `minute=0` | Morning |
| 12:00 PM (Noon) | `hour=12` | `minute=0` | Midday |
| 2:30 PM | `hour=14` | `minute=30` | Afternoon |
| 4:30 PM | `hour=16` | `minute=30` | Late afternoon |
| 6:00 PM | `hour=18` | `minute=0` | Evening |
| 11:59 PM | `hour=23` | `minute=59` | End of day |

### Example Changes:

#### Change Ascent365 to 8:30 AM:
```python
trigger=CronTrigger(
    hour=8,
    minute=30,
    timezone='Asia/Kolkata'
)
```

#### Change Nevastech to 3:00 PM:
```python
trigger=CronTrigger(
    hour=15,
    minute=0,
    timezone='Asia/Kolkata'
)
```

---

## Quick Change Example

Let's say you want to change **Ascent365** from **6:00 AM** to **10:15 AM**:

### 1. Open `scheduler_ascent365.py`

### 2. Find line ~151-154, change:
```python
# FROM:
hour=6,
minute=0,

# TO:
hour=10,
minute=15,
```

### 3. Save file

### 4. Restart scheduler:
```powershell
# Press Ctrl+C in the Ascent365 window
# Then run:
python scheduler_ascent365.py
```

### 5. Done!

The new schedule will be in effect immediately.

---

## Advanced: Multiple Times Per Day

If you want to run checks **multiple times per day**:

```python
# Example: Run at 9 AM and 6 PM daily
scheduler.add_job(
    run_check_and_email,
    trigger=CronTrigger(
        hour='9,18',  # <-- Multiple hours (9 AM and 6 PM)
        minute=0,
        timezone='Asia/Kolkata'
    ),
    id='ascent365_daily_check',
    name='Ascent365 Daily Check - Twice Daily',
    replace_existing=True
)
```

Or add multiple separate jobs:

```python
# Morning check at 9 AM
scheduler.add_job(
    run_check_and_email,
    trigger=CronTrigger(hour=9, minute=0, timezone='Asia/Kolkata'),
    id='ascent365_morning_check',
    name='Ascent365 Morning Check',
)

# Evening check at 6 PM
scheduler.add_job(
    run_check_and_email,
    trigger=CronTrigger(hour=18, minute=0, timezone='Asia/Kolkata'),
    id='ascent365_evening_check',
    name='Ascent365 Evening Check',
)
```

---

## Summary

**To change schedule time:**

1. ✅ Edit the scheduler `.py` file
2. ✅ Change `hour` and `minute` values
3. ✅ Save the file
4. ✅ Stop the scheduler (Ctrl+C)
5. ✅ Restart the scheduler

**That's it!** The new schedule is active immediately! 🎯

---

## Current Schedules:

- **Ascent365:** Daily at 6:00 AM
  - File: `scheduler_ascent365.py` line ~151
  - Config: `config/ascent365.yaml`

- **Nevastech:** Daily at 4:30 PM
  - File: `scheduler_nevastech.py` line ~151
  - Config: `config/config.yaml`
