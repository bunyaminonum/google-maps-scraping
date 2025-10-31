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
    INTERVAL_MINUTES = 30
    
    def __init__(self):
        self.stop_event = Event()
        self.thread = None
        self.status = self.load_status()
        
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
            
            # Collect for all businesses
            businesses = BusinessConfig.BUSINESSES if BusinessConfig.BUSINESSES else []
            
            if not businesses:
                # Use default from session if available
                businesses = [
                    ("ChIJqZW8Cvb_n0ARBuUkyCzgDDg", "İstanbul Havalimanı")
                ]
            
            for place_id, business_name in businesses:
                result = collector.collect_reviews(place_id, business_name)
                
                if result and result.get('success'):
                    reviews = result.get('reviews', [])
                    
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
                                'business_url': review.author_url if hasattr(review, 'author_url') else '',
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
                            total_new += 1
                        else:
                            total_duplicates += 1
            
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
        """Categorize timestamp into time periods"""
        try:
            now = datetime.now()
            
            # Make timezone naive for comparison
            if timestamp.tzinfo is not None:
                timestamp = timestamp.replace(tzinfo=None)
            
            diff = now - timestamp
            
            if diff.total_seconds() < 3600:
                return "Last Hour"
            elif diff.days == 0:
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
            # Run collection
            collection_msg = f"⏰ Starting scheduled collection (Run #{self.status['total_collections'] + 1})"
            print(f"\n{collection_msg}")
            self.add_log(collection_msg, 'info')
            
            result = self.collect_reviews()
            
            # Update status
            self.status['last_run'] = datetime.now().isoformat()
            self.status['next_run'] = (datetime.now() + timedelta(minutes=self.INTERVAL_MINUTES)).isoformat()
            self.status['total_collections'] += 1
            self.status['last_result'] = result
            self.save_status()
            
            if result['success']:
                success_msg = f"✅ Collection successful! New: {result['new_reviews']}, Duplicates: {result['duplicates']}"
                print(success_msg)
                self.add_log(success_msg, 'success')
            else:
                print(f"❌ Collection failed: {result.get('error', 'Unknown error')}")
            
            print(f"⏳ Next collection at: {self.status['next_run']}")
            
            # Wait for interval or stop signal
            for _ in range(self.INTERVAL_MINUTES * 60):
                if self.stop_event.is_set():
                    break
                time.sleep(1)
        
        print("⏸️  Scheduler stopped")
    
    def start(self):
        """Start the scheduler in background"""
        if self.thread and self.thread.is_alive():
            print("⚠️  Scheduler already running")
            return False
        
        self.stop_event.clear()
        self.status['active'] = True
        self.status['next_run'] = (datetime.now() + timedelta(minutes=self.INTERVAL_MINUTES)).isoformat()
        self.save_status()
        
        self.thread = Thread(target=self.run_loop, daemon=True)
        self.thread.start()
        
        print("✅ Scheduler started in background")
        return True
    
    def stop(self):
        """Stop the scheduler"""
        if not self.thread or not self.thread.is_alive():
            print("⚠️  Scheduler not running")
            return False
        
        self.stop_event.set()
        self.thread.join(timeout=5)
        
        self.status['active'] = False
        self.status['next_run'] = None
        self.save_status()
        
        print("✅ Scheduler stopped")
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
    
    print("="*60)
    print("🎯 Google Maps Review Scheduler - Background Service")
    print("="*60)
    print(f"⏱️  Interval: {scheduler.INTERVAL_MINUTES} minutes")
    print(f"📍 Businesses: {len(BusinessConfig.BUSINESSES) if BusinessConfig.BUSINESSES else 1}")
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
