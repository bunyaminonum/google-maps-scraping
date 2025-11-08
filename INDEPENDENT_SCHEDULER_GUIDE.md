# 🚀 Independent Scheduler Guide

## Overview

The Independent Scheduler allows you to run the Google Maps review collector continuously in the background, independent of the Streamlit dashboard.

## Why Use Independent Mode?

✅ **Always Running**: Scheduler continues even when dashboard is closed  
✅ **More Reliable**: No dependency on web browser or Streamlit session  
✅ **Better Performance**: Dedicated process for background collection  
✅ **Flexibility**: View data in dashboard anytime without affecting collection  

## Quick Start (Windows)

### Method 1: Double-Click (Easiest)

1. **Locate the file**: `run_scheduler.bat` in your project folder
2. **Double-click** to run
3. A command window will open showing live status
4. **Minimize** the window (don't close it)
5. Scheduler is now running independently!

**To Stop**: Go back to the command window and press `Ctrl+C`

### Method 2: PowerShell

```powershell
# Navigate to project folder
cd "C:\Users\onumb\OneDrive\Masaüstü\confluent\google-maps-scraping-1"

# Run standalone scheduler
python run_scheduler_standalone.py
```

### Method 3: Hidden Background Process (Advanced)

```powershell
# Start in background (hidden)
Start-Process -WindowStyle Hidden python -ArgumentList "run_scheduler_standalone.py"

# To stop later, find and kill the process
Get-Process python | Where-Object {$_.CommandLine -like "*run_scheduler_standalone*"} | Stop-Process
```

## How It Works

```
┌─────────────────────────────────────────────┐
│  Independent Scheduler Process              │
│  (run_scheduler_standalone.py)              │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ 1. Read config from scheduler_config│   │
│  │ 2. Collect reviews via Google API  │   │
│  │ 3. Save to reviews.db              │   │
│  │ 4. Update scheduler_status.json    │   │
│  │ 5. Wait for next interval          │   │
│  │ 6. Repeat                          │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
                    ↓
        ┌──────────────────────┐
        │   reviews.db         │  ← Data stored here
        │   (SQLite database)  │
        └──────────────────────┘
                    ↓
        ┌──────────────────────┐
        │ Dashboard            │  ← View data anytime
        │ (database_dashboard) │
        └──────────────────────┘
```

## Configuration

Before running, configure your scheduler:

1. **Open Dashboard**: `streamlit run database_dashboard.py`
2. **Go to**: Background Auto Scheduler → ⚙️ Scheduler Settings
3. **Set**:
   - Collection interval (15/30/60/120/180 minutes)
   - Select businesses to monitor
4. **Save Settings**

Settings are saved to `scheduler_config.json` and will be used by independent scheduler.

## Monitoring

### Check Status File

```powershell
# View current status
cat scheduler_status.json | ConvertFrom-Json | Format-List
```

### View Logs in Real-Time

The standalone script shows live status updates:

```
[14:30:15] 📊 Status: Active | Total: 12 collections | Last: 14:25:00 | Next: 14:55:00
[14:30:45] 📊 Status: Active | Total: 12 collections | Last: 14:25:00 | Next: 14:55:00
```

### Check Database

```powershell
# Open dashboard to view collected data
streamlit run database_dashboard.py
```

## Important Notes

⚠️ **Only One Instance**: Run either dashboard scheduler OR independent scheduler, not both  
⚠️ **API Key Required**: Ensure `GOOGLE_MAPS_API_KEY` is set in `.env` file  
⚠️ **Database Access**: Dashboard and scheduler both access `reviews.db` (SQLite handles concurrent access)  

## Troubleshooting

### Scheduler Won't Start

**Problem**: "Failed to start scheduler"

**Solutions**:
1. Check if another scheduler instance is already running
2. Verify `scheduler_status.json` shows `"active": false`
3. Ensure `.env` file contains valid `GOOGLE_MAPS_API_KEY`
4. Check that businesses are configured in `scheduler_config.json`

### Can't Stop Scheduler

**Problem**: Scheduler keeps running after pressing Ctrl+C

**Solution**:
```powershell
# Force stop all Python processes (use with caution)
Get-Process python | Stop-Process -Force

# Or, find specific process
Get-Process python | Select-Object Id, Path | Where-Object {$_.Path -like "*run_scheduler*"}
# Then kill by ID:
Stop-Process -Id <process_id>
```

### No Data Appearing

**Problem**: Scheduler is running but no new reviews

**Solutions**:
1. Check logs in `scheduler_status.json` for errors
2. Verify businesses have valid Place IDs
3. Ensure API key has sufficient quota
4. Check if reviews are marked as duplicates (already in DB)

## Best Practices

✅ **Test First**: Run scheduler from dashboard before using independent mode  
✅ **Monitor Logs**: Check status file regularly for errors  
✅ **Set Reasonable Intervals**: 30 minutes is balanced; too frequent may hit API limits  
✅ **Keep Script Running**: Don't close the command window (minimize it instead)  
✅ **Use Process Manager**: Consider Windows Task Scheduler for automatic startup  

## Advanced: Windows Task Scheduler

To run scheduler automatically on system startup:

1. Open **Task Scheduler**
2. Create new task:
   - **Trigger**: At system startup
   - **Action**: Start program
     - Program: `python.exe`
     - Arguments: `run_scheduler_standalone.py`
     - Start in: `C:\Users\onumb\OneDrive\Masaüstü\confluent\google-maps-scraping-1`
3. **Settings**: 
   - Run whether user is logged on or not
   - Hidden

## Support

If you encounter issues:

1. Check `scheduler_status.json` for error logs
2. Review dashboard logs in sidebar
3. Verify `.env` configuration
4. Test with dashboard scheduler first

---

**Happy Collecting! 🎉**

*For more information, see the main project README or open the dashboard.*
