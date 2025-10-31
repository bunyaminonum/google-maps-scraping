@echo off
REM Google Maps API Pipeline Starter
REM This script runs the data pipeline scheduler

echo ========================================
echo   Google Maps API Data Pipeline
echo ========================================
echo.
echo Starting scheduler...
echo Press Ctrl+C to stop
echo.

C:\Users\onumb\AppData\Local\Microsoft\WindowsApps\python3.12.exe api_pipeline\scheduler.py
