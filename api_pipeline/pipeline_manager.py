#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Pipeline Manager
Orchestrates API collection and database storage with duplicate detection
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_pipeline.collectors.google_maps_api import GoogleMapsAPICollector, Review
from api_pipeline.config.settings import Config, BusinessConfig
from database_test import ReviewsDatabase
from datetime import datetime
from typing import List, Dict


class APIPipelineManager:
    """
    Manages the complete API data pipeline:
    1. Collect reviews from Google Maps API
    2. Check for duplicates
    3. Save new reviews to database
    4. Track statistics
    """
    
    def __init__(self):
        """Initialize pipeline components"""
        # Validate configuration
        if not Config.validate():
            raise ValueError("Invalid configuration. Check .env file.")
        
        # Initialize components
        self.collector = GoogleMapsAPICollector(
            api_key=Config.GOOGLE_MAPS_API_KEY,
            language=Config.API_LANGUAGE
        )
        self.db = ReviewsDatabase(Config.DATABASE_PATH)
        
        # Statistics
        self.stats = {
            'collections': 0,
            'total_reviews_fetched': 0,
            'new_reviews_saved': 0,
            'duplicates_skipped': 0,
            'errors': 0
        }
    
    def collect_and_save(self, place_id: str, business_name: str) -> Dict:
        """
        Collect reviews for a business and save to database
        
        Args:
            place_id: Google Maps Place ID
            business_name: Business name
            
        Returns:
            Collection result with statistics
        """
        print(f"\n{'='*60}")
        print(f"🚀 PIPELINE: {business_name}")
        print(f"{'='*60}")
        
        # Step 1: Collect from API
        result = self.collector.collect_reviews(place_id, business_name)
        
        if not result['success']:
            print(f"❌ Collection failed: {result.get('error')}")
            self.stats['errors'] += 1
            return {
                'success': False,
                'error': result.get('error'),
                'business_name': business_name
            }
        
        self.stats['collections'] += 1
        reviews = result['reviews']
        self.stats['total_reviews_fetched'] += len(reviews)
        
        print(f"\n📥 Processing {len(reviews)} reviews...")
        
        # Step 2: Process reviews with duplicate detection
        new_reviews = []
        duplicates = 0
        
        for i, review in enumerate(reviews, 1):
            # Generate hash for duplicate detection
            review_hash = self.db.generate_review_hash(
                business_name=business_name,
                reviewer_name=review.author_name,
                date_original=review.relative_time,
                review_text=review.text
            )
            
            # Check if review already exists
            if self.db.check_review_exists(review_hash):
                print(f"   ⏭️  Review {i}/{len(reviews)}: Duplicate (skipped)")
                duplicates += 1
                continue
            
            # New review - prepare for saving
            new_reviews.append({
                'business_name': business_name,
                'business_url': f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                'reviewer_name': review.author_name,
                'rating': review.rating,
                'date_original': review.relative_time,
                'review_text': review.text,
                'timestamp_parsed': review.timestamp,
                'review_hash': review_hash
            })
            
            print(f"   ✅ Review {i}/{len(reviews)}: New (will save)")
        
        # Step 3: Save to database
        if new_reviews:
            print(f"\n💾 Saving {len(new_reviews)} new reviews to database...")
            
            # Create session ID
            session_id = f"api_collection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Save session
            session_data = {
                'session_id': session_id,
                'business_name': business_name,
                'business_url': f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                'target_text_reviews': len(new_reviews),
                'actual_text_reviews': len(new_reviews),
                'actual_total_ratings': len(new_reviews),
                'average_rating': sum(r['rating'] for r in new_reviews) / len(new_reviews) if new_reviews else 0
            }
            self.db.add_session(session_data)
            
            # Save reviews
            for review in new_reviews:
                review_data = {
                    'business_name': review['business_name'],
                    'business_url': review['business_url'],
                    'reviewer_name': review['reviewer_name'],
                    'rating': review['rating'],
                    'review_date': review['date_original'],
                    'review_text': review['review_text'],
                    'timestamp': review['timestamp_parsed'],
                    'scrape_session_id': session_id,
                    'review_hash': review['review_hash']
                }
                self.db.add_review(review_data)
            
            self.stats['new_reviews_saved'] += len(new_reviews)
            print(f"   ✅ Saved successfully!")
        else:
            print(f"\n   ℹ️  No new reviews to save")
        
        self.stats['duplicates_skipped'] += duplicates
        
        # Summary
        print(f"\n📊 PIPELINE SUMMARY:")
        print(f"   📥 Fetched: {len(reviews)} reviews")
        print(f"   ✅ New: {len(new_reviews)} saved")
        print(f"   ⏭️  Duplicates: {duplicates} skipped")
        print(f"{'='*60}\n")
        
        return {
            'success': True,
            'business_name': business_name,
            'place_id': place_id,
            'total_fetched': len(reviews),
            'new_saved': len(new_reviews),
            'duplicates': duplicates,
            'session_id': session_id if new_reviews else None
        }
    
    def run_pipeline(self) -> Dict:
        """
        Run pipeline for all configured businesses
        
        Returns:
            Overall pipeline statistics
        """
        print("\n" + "="*60)
        print("🚀 STARTING API DATA PIPELINE")
        print("="*60)
        print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📍 Businesses: {len(BusinessConfig.BUSINESSES)}")
        print("="*60)
        
        results = []
        
        for place_id, business_name in BusinessConfig.BUSINESSES:
            result = self.collect_and_save(place_id, business_name)
            results.append(result)
        
        # Overall summary
        print("\n" + "="*60)
        print("📊 PIPELINE EXECUTION COMPLETE")
        print("="*60)
        print(f"✅ Collections: {self.stats['collections']}")
        print(f"📥 Total fetched: {self.stats['total_reviews_fetched']}")
        print(f"💾 New saved: {self.stats['new_reviews_saved']}")
        print(f"⏭️  Duplicates skipped: {self.stats['duplicates_skipped']}")
        print(f"❌ Errors: {self.stats['errors']}")
        print("="*60 + "\n")
        
        return {
            'success': True,
            'timestamp': datetime.now(),
            'results': results,
            'stats': self.stats
        }
    
    def get_statistics(self) -> Dict:
        """Get pipeline statistics"""
        return self.stats.copy()


def main():
    """Main execution"""
    try:
        # Initialize pipeline
        pipeline = APIPipelineManager()
        
        # Run pipeline
        result = pipeline.run_pipeline()
        
        if result['success']:
            print("✅ Pipeline executed successfully!")
        else:
            print("❌ Pipeline failed!")
            
    except Exception as e:
        print(f"❌ Pipeline error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
