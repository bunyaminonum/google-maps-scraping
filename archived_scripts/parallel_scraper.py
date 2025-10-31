#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 Database Google Maps Scraper - Parallel Version
Ban-safe parallel scraping with database integration
"""

from database_scraper import DatabaseGoogleMapsScraper, Review
from database_test import ReviewsDatabase
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class ParallelTask:
    """Parallel scraping task"""
    business_name: str
    business_url: str
    target_reviews: int = 50
    target_text_reviews: int = 10
    session_prefix: str = "parallel"

class ParallelDatabaseScraper:
    """Parallel scraper with database integration"""
    
    def __init__(self, db_path="reviews.db", max_workers=2, safe_mode=True):
        """
        Args:
            db_path: Database file path
            max_workers: Maximum concurrent workers (2-3 recommended for Google)
            safe_mode: Enable extra safety measures if True
        """
        self.db_path = db_path
        self.max_workers = max_workers
        self.safe_mode = safe_mode
        self.results_lock = threading.Lock()
        self.all_results = []
        
    def create_worker_scraper(self, worker_id: int, headless: bool = True):
        """Create scraper for worker"""
        try:
            # Separate browser profile for each worker
            scraper = DatabaseGoogleMapsScraper(
                headless=headless,
                db_path=self.db_path
            )
            
            # Safe mode settings
            if self.safe_mode:
                # Randomize user agent
                user_agents = [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0"
                ]
                
                # Add random user agent to browser
                if hasattr(scraper, 'driver') and scraper.driver:
                    ua = random.choice(user_agents)
                    scraper.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": ua})
            
            return scraper
            
        except Exception as e:
            print(f"❌ Worker {worker_id} scraper creation error: {e}")
            return None
    
    def smart_delay(self, worker_id: int, operation: str = "default"):
        """Smart delay - avoid bans"""
        base_delays = {
            "start": (2.0, 5.0),
            "page_load": (3.0, 6.0),
            "between_businesses": (5.0, 10.0),
            "scroll": (1.5, 3.0),
            "default": (2.0, 4.0)
        }
        
        min_delay, max_delay = base_delays.get(operation, base_delays["default"])
        
        if self.safe_mode:
            # Increase delays in safe mode
            min_delay *= 1.5
            max_delay *= 2.0
        
        delay = random.uniform(min_delay, max_delay)
        
        print(f"⏱️ Worker {worker_id}: Waiting {delay:.1f}s for {operation}...")
        time.sleep(delay)
        
        return delay
    
    def scrape_worker_task(self, worker_id: int, tasks: List[ParallelTask]):
        """Process all tasks for a worker"""
        worker_results = []
        scraper = None
        
        try:
            print(f"🔧 Worker {worker_id} starting - {len(tasks)} tasks")
            
            # Worker startup delay (prevent overlapping)
            self.smart_delay(worker_id, "start")
            
            # Create scraper
            scraper = self.create_worker_scraper(worker_id, headless=True)
            if not scraper:
                raise Exception("Failed to create scraper")
            
            # Process tasks sequentially
            for i, task in enumerate(tasks):
                try:
                    print(f"📋 Worker {worker_id}: Processing {task.business_name} ({i+1}/{len(tasks)})")
                    
                    # Delay between businesses
                    if i > 0:
                        self.smart_delay(worker_id, "between_businesses")
                    
                    # Create session ID
                    session_id = f"{task.session_prefix}_{worker_id}_{int(time.time())}"
                    
                    # Perform scraping
                    result = scraper.extract_reviews_with_database(
                        business_name=task.business_name,
                        business_url=task.business_url,
                        target_text_reviews=task.target_text_reviews,
                        target_ratings=task.target_reviews
                    )
                    
                    if result["success"]:
                        session_id = result.get("session_id", f"worker_{worker_id}_{int(time.time())}")
                        print(f"✅ Worker {worker_id}: {task.business_name} completed")
                        print(f"   📊 {result['total_reviews']} reviews, {result['text_reviews']} text")
                        
                        worker_results.append({
                            "worker_id": worker_id,
                            "business_name": task.business_name,
                            "session_id": session_id,
                            "success": True,
                            "total_reviews": result["total_reviews"],
                            "text_reviews": result["text_reviews"],
                            "error": None
                        })
                    else:
                        session_id = f"failed_worker_{worker_id}_{int(time.time())}"
                        print(f"⚠️ Worker {worker_id}: {task.business_name} failed")
                        worker_results.append({
                            "worker_id": worker_id,
                            "business_name": task.business_name,
                            "session_id": session_id,
                            "success": False,
                            "error": result.get("error", "Unknown error")
                        })
                        
                except Exception as e:
                    print(f"❌ Worker {worker_id}: {task.business_name} task error - {e}")
                    worker_results.append({
                        "worker_id": worker_id,
                        "business_name": task.business_name,
                        "success": False,
                        "error": str(e)
                    })
            
            print(f"🏁 Worker {worker_id} completed - {len(worker_results)} results")
            return worker_results
            
        except Exception as e:
            print(f"❌ Worker {worker_id} general error: {e}")
            return [{
                "worker_id": worker_id,
                "success": False,
                "error": f"Worker error: {e}"
            }]
            
        finally:
            # Clean up scraper
            if scraper:
                try:
                    scraper.cleanup()
                except:
                    pass
    
    def parallel_scrape_businesses(self, tasks: List[ParallelTask]):
        """Main parallel scraping function"""
        print(f"🚀 PARALLEL SCRAPING STARTING")
        print(f"="*60)
        print(f"📋 Business count: {len(tasks)}")
        print(f"🔧 Worker count: {self.max_workers}")
        print(f"🛡️ Safe mode: {'Enabled' if self.safe_mode else 'Disabled'}")
        print(f"💾 Database: {self.db_path}")
        print(f"="*60)
        
        # Distribute tasks to workers
        tasks_per_worker = []
        for i in range(self.max_workers):
            worker_tasks = [task for j, task in enumerate(tasks) if j % self.max_workers == i]
            if worker_tasks:
                tasks_per_worker.append(worker_tasks)
        
        print(f"📊 Task distribution:")
        for i, worker_tasks in enumerate(tasks_per_worker):
            print(f"   Worker {i+1}: {len(worker_tasks)} tasks")
        
        # Parallel execution
        start_time = time.time()
        all_results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Start workers
            futures = []
            for i, worker_tasks in enumerate(tasks_per_worker):
                worker_id = i + 1
                future = executor.submit(self.scrape_worker_task, worker_id, worker_tasks)
                futures.append((worker_id, future))
            
            # Collect results
            for worker_id, future in futures:
                try:
                    worker_results = future.result()
                    all_results.extend(worker_results)
                    print(f"✅ Worker {worker_id} results received")
                except Exception as e:
                    print(f"❌ Worker {worker_id} future error: {e}")
                    all_results.append({
                        "worker_id": worker_id,
                        "success": False,
                        "error": f"Future error: {e}"
                    })
        
        end_time = time.time()
        
        # Summary report
        self.print_final_report(all_results, start_time, end_time)
        
        return all_results
    
    def print_final_report(self, results: List[Dict], start_time: float, end_time: float):
        """Print final report"""
        print(f"\n" + "="*60)
        print(f"📊 PARALLEL SCRAPING RESULTS")
        print(f"="*60)
        
        successful = len([r for r in results if r.get("success", False)])
        total_reviews = sum([r.get("total_reviews", 0) for r in results if r.get("success", False)])
        total_text = sum([r.get("text_reviews", 0) for r in results if r.get("success", False)])
        
        duration = end_time - start_time
        
        print(f"⏱️ Total time: {duration:.1f} seconds")
        print(f"✅ Successful businesses: {successful}/{len(results)}")
        print(f"📊 Total reviews: {total_reviews}")
        print(f"💬 Text reviews: {total_text}")
        
        if duration > 0:
            print(f"🚀 Speed: {total_reviews/duration:.1f} reviews/second")
            print(f"📈 Efficiency: {total_reviews/(duration/60):.1f} reviews/minute")
        
        print(f"\n📋 Detailed Results:")
        for result in results:
            if result.get("success", False):
                business = result.get("business_name", "Unknown")
                reviews = result.get("total_reviews", 0)
                worker = result.get("worker_id", "?")
                print(f"   ✅ {business}: {reviews} reviews (Worker {worker})")
            else:
                business = result.get("business_name", "Unknown")
                error = result.get("error", "Unknown error")
                worker = result.get("worker_id", "?")
                print(f"   ❌ {business}: {error} (Worker {worker})")

def demo_parallel_database_scraping():
    """Parallel database scraping demo"""
    print("🎯 PARALLEL DATABASE SCRAPING DEMO")
    print("="*50)
    
    # Test businesses
    tasks = [
        ParallelTask(
            business_name="Istanbul Airport",
            business_url="https://www.google.com/maps/place/İstanbul+Havalimanı/@41.2619652,28.741773,12z/data=!3m1!4b1!4m6!3m5!1s0x14b015c8ef2a5935:0x8d1a87ba3a5b8b4e!8m2!3d41.2619652!4d28.741773!16zL20vMDZfZm5z?entry=ttu",
            target_reviews=30,
            target_text_reviews=8
        ),
        ParallelTask(
            business_name="Sabiha Gokcen Airport",
            business_url="https://www.google.com/maps/place/İstanbul+Sabiha+Gökçen+Uluslararası+Havalimanı/@40.8986426,29.3092776,12z/data=!3m1!4b1!4m6!3m5!1s0x14cadddc0d8b2b73:0x8d1a87ba3a5b8b4e!8m2!3d40.8986426!4d29.3092776!16zL20vMDZfZm5z?entry=ttu",
            target_reviews=30,
            target_text_reviews=8
        ),
        ParallelTask(
            business_name="Starbucks Zorlu Center",
            business_url="https://www.google.com/maps/search/starbucks+zorlu+center",
            target_reviews=25,
            target_text_reviews=6
        )
    ]
    
    # Create parallel scraper
    scraper = ParallelDatabaseScraper(
        db_path="reviews.db",
        max_workers=2,  # Safe parallelism
        safe_mode=True  # Extra security
    )
    
    # Start scraping
    results = scraper.parallel_scrape_businesses(tasks)
    
    # Database check
    print(f"\n💾 DATABASE CHECK:")
    db = ReviewsDatabase("reviews.db")
    df = db.get_all_reviews()
    
    print(f"📊 Total records: {len(df)}")
    print(f"🏢 Business count: {df['business_name'].nunique()}")
    
    # Show recent sessions
    recent_sessions = df['scrape_session_id'].value_counts().head(5)
    print(f"📋 Recent sessions:")
    for session, count in recent_sessions.items():
        if session and "parallel" in str(session):
            print(f"   🗂️ {session}: {count} reviews")

if __name__ == "__main__":
    demo_parallel_database_scraping()
