"""
🔄 Standalone Scheduler Runner
Run the background scheduler independently from Streamlit dashboard
This script allows the scheduler to run continuously without keeping the dashboard open.
"""

import sys
import os
import time
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from background_scheduler import BackgroundScheduler

def main():
    """Run the scheduler standalone"""
    print("="*60)
    print("🚀 Google Maps Review Scheduler - Standalone Mode")
    print("="*60)
    print()
    
    # Initialize scheduler
    scheduler = BackgroundScheduler()
    
    # Get current configuration
    config = scheduler.get_config()
    interval = config.get('interval_minutes', 30)
    businesses = config.get('enabled_businesses', [])
    
    print(f"📊 Configuration:")
    print(f"   ⏱️  Interval: {interval} minutes")
    print(f"   🏢 Businesses: {len(businesses) if businesses else 'All enabled'}")
    if businesses:
        for idx, biz in enumerate(businesses, 1):
            print(f"      {idx}. {biz}")
    print()
    
    # Start scheduler
    print("▶️  Starting background scheduler...")
    if scheduler.start():
        print("✅ Scheduler started successfully!")
        print()
        print("💡 Scheduler is now running in the background.")
        print("   📝 Check scheduler_status.json for live status")
        print("   📊 Reviews will be saved to reviews.db automatically")
        print("   🔄 Dashboard will show latest data when opened")
        print()
        print("⚠️  Press Ctrl+C to stop the scheduler")
        print("="*60)
        print()
        
        try:
            # Keep script running and show status updates
            while True:
                time.sleep(30)  # Check every 30 seconds
                
                # Read current status
                try:
                    import json
                    if os.path.exists('scheduler_status.json'):
                        with open('scheduler_status.json', 'r') as f:
                            status = json.load(f)
                        
                        if status.get('active'):
                            total = status.get('total_collections', 0)
                            last_run = status.get('last_run', 'N/A')
                            next_run = status.get('next_run', 'N/A')
                            
                            # Format timestamps
                            try:
                                if last_run != 'N/A':
                                    last_dt = datetime.fromisoformat(last_run)
                                    last_run = last_dt.strftime('%H:%M:%S')
                                if next_run != 'N/A':
                                    next_dt = datetime.fromisoformat(next_run)
                                    next_run = next_dt.strftime('%H:%M:%S')
                            except:
                                pass
                            
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Status: Active | Total: {total} collections | Last: {last_run} | Next: {next_run}")
                        else:
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Scheduler appears to be stopped")
                            break
                except Exception as e:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Error reading status: {str(e)}")
                
        except KeyboardInterrupt:
            print()
            print("="*60)
            print("⏹️  Stopping scheduler...")
            if scheduler.stop():
                print("✅ Scheduler stopped successfully!")
            else:
                print("⚠️  Scheduler may have already stopped")
            print("👋 Goodbye!")
            print("="*60)
    else:
        print("❌ Failed to start scheduler!")
        print("💡 Possible reasons:")
        print("   - Scheduler may already be running")
        print("   - Check scheduler_status.json for errors")
        print("   - Ensure Google Maps API key is configured in .env")
        sys.exit(1)

if __name__ == "__main__":
    main()
