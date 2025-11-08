@echo off
REM 🔄 Standalone Scheduler Launcher for Windows
REM This batch file runs the scheduler independently in the background

echo ========================================
echo Google Maps Review Scheduler
echo Standalone Background Mode
echo ========================================
echo.

REM Check if Python is available
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not found in PATH
    echo Please install Python or add it to PATH
    pause
    exit /b 1
)

echo Starting scheduler in background mode...
echo.

REM Run the standalone scheduler script
python run_scheduler_standalone.py

pause
