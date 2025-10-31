#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Scheduler for API Pipeline
Runs collection every N minutes without Airflow dependency
"""

import time
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_pipeline.pipeline_manager import APIPipelineManager
from api_pipeline.config.settings import Config, BusinessConfig


class SimpleScheduler:
    """Simple scheduler for API pipeline"""
    
    def __init__(self, interval_minutes: int = 5):
        """
        Initialize scheduler
        
        Args:
            interval_minutes: How often to run collection (default: 5 minutes)
        """
        self.interval_minutes = interval_minutes
        self.interval_seconds = interval_minutes * 60
        self.pipeline = APIPipelineManager()
        self.run_count = 0
        
    def run_once(self):
        """Run pipeline once"""
        self.run_count += 1
        
        print(f"\n{'='*70}")
        print(f"🔄 SCHEDULED RUN #{self.run_count}")
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        try:
            result = self.pipeline.run_pipeline()
            
            if result['success']:
                print(f"\n✅ Run #{self.run_count} completed successfully")
                return True
            else:
                print(f"\n❌ Run #{self.run_count} failed")
                return False
                
        except Exception as e:
            print(f"\n❌ Run #{self.run_count} error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def start(self):
        """Start scheduler loop"""
        print("\n" + "="*70)
        print("🚀 SIMPLE SCHEDULER STARTING")
        print("="*70)
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️  Interval: Every {self.interval_minutes} minutes")
        print(f"📍 Businesses: {len(BusinessConfig.BUSINESSES)}")
        print(f"🔄 Press Ctrl+C to stop")
        print("="*70 + "\n")
        
        try:
            while True:
                # Run collection
                self.run_once()
                
                # Wait for next run
                next_run = datetime.now().timestamp() + self.interval_seconds
                next_run_time = datetime.fromtimestamp(next_run).strftime('%H:%M:%S')
                
                print(f"\n⏳ Next run at: {next_run_time}")
                print(f"💤 Sleeping for {self.interval_minutes} minutes...")
                print("-" * 70)
                
                time.sleep(self.interval_seconds)
                
        except KeyboardInterrupt:
            print(f"\n\n{'='*70}")
            print("🛑 SCHEDULER STOPPED")
            print("="*70)
            print(f"📊 Total runs: {self.run_count}")
            print(f"⏰ Stopped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("="*70 + "\n")


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple API Pipeline Scheduler')
    parser.add_argument(
        '--interval',
        type=int,
        default=Config.COLLECTION_INTERVAL_MINUTES,
        help=f'Collection interval in minutes (default: {Config.COLLECTION_INTERVAL_MINUTES})'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (no scheduling)'
    )
    
    args = parser.parse_args()
    
    if args.once:
        # Run once mode
        print("\n🎯 Running pipeline once (no scheduling)...\n")
        scheduler = SimpleScheduler(args.interval)
        scheduler.run_once()
        print("\n✅ Done!")
    else:
        # Scheduled mode
        scheduler = SimpleScheduler(args.interval)
        scheduler.start()


if __name__ == "__main__":
    main()
