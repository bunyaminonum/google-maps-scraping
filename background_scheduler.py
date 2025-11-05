#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Background Scheduler Service
Runs independently and collects reviews every 30 minutes
"""

import time
import json
import os
from datetime import datetime, timedelta
from threading import Thread, Event
from pathlib import Path

from api_pipeline.collectors.google_maps_api import GoogleMapsAPICollector
from database_test import ReviewsDatabase
from api_pipeline.config.settings import Config, BusinessConfig
from dotenv import load_dotenv


class BackgroundScheduler:
    """
    Independent scheduler that runs in background
    Controlled via status file
    """
    
    STATUS_FILE = "scheduler_status.json"
    CONFIG_FILE = "scheduler_config.json"
    DEFAULT_INTERVAL = 30  # Default interval in minutes
    
    def __init__(self):
        self.stop_event = Event()
        self.thread = None
        self.status = self.load_status()
        self.config = self.load_config()
        
    def load_status(self):
        """Load scheduler status from file"""
        if os.path.exists(self.STATUS_FILE):
            try:
                with open(self.STATUS_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            'active': False,
            'last_run': None,
            'next_run': None,
            'total_collections': 0,
            'last_result': None,
            'logs': []
        }
    
    def save_status(self):
        """Save scheduler status to file"""
        with open(self.STATUS_FILE, 'w') as f:
            json.dump(self.status, f, indent=2, default=str)
    
    def load_config(self):
        """Load scheduler configuration"""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Default configuration
        return {
            'interval_minutes': self.DEFAULT_INTERVAL,
            'enabled_businesses': []  # Empty means all businesses
        }
    
    def save_config(self, config):
        """Save scheduler configuration"""
        try:
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            self.config = config
            self.add_log(f"⚙️ Config updated: {config['interval_minutes']} min, {len(config.get('enabled_businesses', []))} businesses", 'info')
            return True
        except Exception as e:
            self.add_log(f"❌ Config save error: {str(e)}", 'error')
            return False
    
    def get_config(self):
        """Get current configuration"""
        return self.config.copy()
    
    def add_log(self, message, level='info'):
        """Add log entry"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        
        if 'logs' not in self.status:
            self.status['logs'] = []
        
        self.status['logs'].append(log_entry)
        
        # Keep only last 50 logs
        if len(self.status['logs']) > 50:
            self.status['logs'] = self.status['logs'][-50:]
        
        self.save_status()
        print(f"[{level.upper()}] {message}")
    
    def collect_reviews(self):
        """Collect reviews for all configured businesses"""
        try:
            # Load environment
            load_dotenv()
            api_key = os.getenv('GOOGLE_MAPS_API_KEY')
            
            if not api_key:
                return {'success': False, 'error': 'API key not found'}
            
            # Initialize
            collector = GoogleMapsAPICollector(api_key=api_key)
            db = ReviewsDatabase("reviews.db")
            
            total_new = 0
            total_duplicates = 0
            
            # Get businesses from config (includes database businesses)
            all_businesses = BusinessConfig.get_all_businesses_from_db()
            enabled_business_names = self.config.get('enabled_businesses', [])
            
            # If no businesses specified, use all
            if not enabled_business_names:
                businesses = all_businesses
                self.add_log(f"📋 Collecting from all {len(businesses)} businesses", 'info')
            else:
                # Filter to only enabled businesses
                businesses = [(pid, name) for pid, name in all_businesses if name in enabled_business_names]
                self.add_log(f"📋 Collecting from {len(businesses)} selected businesses", 'info')
            
            if not businesses:
                # Use default if nothing configured
                businesses = [
                    ("ChIJqZW8Cvb_n0ARBuUkyCzgDDg", "İstanbul Havalimanı")
                ]
            
            for place_id, business_name in businesses:
                self.add_log(f"📍 Collecting: {business_name} (Place ID: {place_id[:20]}...)", 'info')
                
                # Validate Place ID
                if not place_id or not place_id.startswith('ChIJ'):
                    error_msg = f"❌ Invalid Place ID for {business_name}: {place_id}"
                    self.add_log(error_msg, 'error')
                    print(error_msg)
                    continue
                
                result = collector.collect_reviews(place_id, business_name)
                
                if result and result.get('success'):
                    reviews = result.get('reviews', [])
                    self.add_log(f"  📥 Received {len(reviews)} reviews from API", 'info')
                    
                    business_new = 0
                    business_duplicates = 0
                    
                    for review in reviews:
                        # Generate hash
                        review_hash = db.generate_review_hash(
                            business_name,
                            review.author_name,
                            review.relative_time,
                            review.text or ""
                        )
                        
                        # Check if exists
                        if not db.check_review_exists(review_hash):
                            # Calculate time category
                            timestamp_obj = review.timestamp if hasattr(review, 'timestamp') else None
                            time_category = self._categorize_timestamp(timestamp_obj) if timestamp_obj else "Unknown"
                            
                            # Add review
                            review_data = {
                                'business_name': business_name,
                                'business_url': place_id,  # Store place_id as business_url
                                'reviewer_name': review.author_name,
                                'rating': review.rating,
                                'review_date': review.relative_time,
                                'review_text': review.text or "",
                                'timestamp_parsed': timestamp_obj.isoformat() if timestamp_obj else None,
                                'time_category': time_category,
                                'session_id': f'background_scheduler_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                                'review_hash': review_hash
                            }
                            
                            db.add_review(review_data)
                            business_new += 1
                            total_new += 1
                        else:
                            business_duplicates += 1
                            total_duplicates += 1
                    
                    # Log business summary
                    summary = f"  ✅ {business_name}: {business_new} new, {business_duplicates} duplicates"
                    self.add_log(summary, 'success')
                else:
                    # Log API failure
                    error = result.get('error', 'Unknown error') if result else 'No response'
                    error_msg = f"  ❌ {business_name}: API failed - {error}"
                    self.add_log(error_msg, 'error')
                    print(error_msg)
            
            return {
                'success': True,
                'new_reviews': total_new,
                'duplicates': total_duplicates,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _categorize_timestamp(self, timestamp):
        """Categorize timestamp into time periods with correct timezone handling"""
        try:
            import pytz
            tr_tz = pytz.timezone('Europe/Istanbul')
            now = datetime.now(tr_tz)
            
            # Make timestamp timezone-aware if naive
            if timestamp.tzinfo is None:
                timestamp = tr_tz.localize(timestamp)
            
            diff = now - timestamp
            
            if diff.total_seconds() < 3600:  # Less than 1 hour
                return "Last Hour"
            elif diff.days == 0:  # Same day but more than 1 hour ago
                return "Today"
            elif diff.days == 1:
                return "Yesterday"
            elif diff.days <= 7:
                return "This Week"
            elif diff.days <= 30:
                return "This Month"
            elif diff.days <= 90:
                return "Last 3 Months"
            elif diff.days <= 180:
                return "Last 6 Months"
            elif diff.days <= 365:
                return "This Year"
            else:
                return "Older"
        except:
            return "Unknown"
    
    def run_loop(self):
        """Main scheduler loop"""
        start_msg = f"🚀 Background scheduler started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        print(start_msg)
        self.add_log(start_msg, 'info')
        
        while not self.stop_event.is_set():
            # Reload config in case it changed
            self.config = self.load_config()
            interval = self.config.get('interval_minutes', self.DEFAULT_INTERVAL)
            
            # Run collection
            collection_msg = f"⏰ Starting scheduled collection (Run #{self.status['total_collections'] + 1})"
            print(f"\n{collection_msg}")
            self.add_log(collection_msg, 'info')
            
            result = self.collect_reviews()
            
            # Update status
            now = datetime.now()
            self.status['last_run'] = now.isoformat()
            self.status['next_run'] = (now + timedelta(minutes=interval)).isoformat()
            self.status['total_collections'] += 1
            self.status['last_result'] = result
            self.save_status()
            
            if result['success']:
                success_msg = f"✅ Collection successful! New: {result['new_reviews']}, Duplicates: {result['duplicates']}"
                print(success_msg)
                self.add_log(success_msg, 'success')
            else:
                print(f"❌ Collection failed: {result.get('error', 'Unknown error')}")
            
            next_time = datetime.fromisoformat(self.status['next_run'])
            print(f"⏳ Next collection in {interval} minutes (at {next_time.strftime('%H:%M:%S')})")
            
            # Wait for interval or stop signal
            for _ in range(interval * 60):
                if self.stop_event.is_set():
                    break
                time.sleep(1)
        
        print("⏸️  Scheduler stopped")
    
    def start(self):
        """Start the scheduler in background"""
        # Check if already running
        if self.thread and self.thread.is_alive():
            print("⚠️  Scheduler already running")
            self.add_log("⚠️ Start requested but already running", 'warning')
            return False
        
        # Reload config before starting
        self.config = self.load_config()
        interval = self.config.get('interval_minutes', self.DEFAULT_INTERVAL)
        
        print(f"🚀 Starting scheduler (interval: {interval} min)...")
        
        # Clear stop event and update status
        self.stop_event.clear()
        self.status['active'] = True
        self.status['next_run'] = (datetime.now() + timedelta(minutes=interval)).isoformat()
        self.save_status()
        
        # Start the thread
        self.thread = Thread(target=self.run_loop, daemon=True)
        self.thread.start()
        
        # Give it a moment to start
        time.sleep(0.5)
        
        if self.thread.is_alive():
            print(f"✅ Scheduler started successfully in background")
            self.add_log(f"✅ Scheduler started (interval: {interval} min)", 'success')
            return True
        else:
            print("❌ Failed to start scheduler thread")
            self.add_log("❌ Failed to start scheduler thread", 'error')
            self.status['active'] = False
            self.save_status()
            return False
    
    def stop(self):
        """Stop the scheduler"""
        # Always update status file first
        self.status['active'] = False
        self.status['next_run'] = None
        self.save_status()
        
        if not self.thread or not self.thread.is_alive():
            print("⚠️  Scheduler not running (status file updated)")
            self.add_log("⏹️ Scheduler stopped (was not running)", 'info')
            return True  # Return True since we updated the status
        
        print("🛑 Stopping scheduler...")
        self.add_log("🛑 Stopping scheduler...", 'info')
        
        # Signal the thread to stop
        self.stop_event.set()
        
        # Wait for thread to finish (with timeout)
        self.thread.join(timeout=3)
        
        if self.thread.is_alive():
            print("⚠️  Scheduler thread did not stop gracefully (force stopped)")
            self.add_log("⚠️ Scheduler force stopped", 'warning')
        else:
            print("✅ Scheduler stopped gracefully")
            self.add_log("✅ Scheduler stopped gracefully", 'success')
        
        return True
    
    def get_status(self):
        """Get current scheduler status"""
        self.status = self.load_status()
        return self.status


def main():
    """
    Run scheduler as standalone service
    Usage: python background_scheduler.py
    """
    import signal
    import sys
    
    scheduler = BackgroundScheduler()
    
    def signal_handler(sig, frame):
        print("\n\n🛑 Shutting down scheduler...")
        scheduler.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    config = scheduler.get_config()
    interval = config.get('interval_minutes', scheduler.DEFAULT_INTERVAL)
    enabled = config.get('enabled_businesses', [])
    
    print("="*60)
    print("🎯 Google Maps Review Scheduler - Background Service")
    print("="*60)
    print(f"⏱️  Interval: {interval} minutes")
    print(f"📍 Businesses: {len(enabled) if enabled else 'All'}")
    print("="*60)
    
    scheduler.start()
    
    # Keep alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()


if __name__ == "__main__":
    main()
