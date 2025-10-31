#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps API Collector
Fast and reliable review collection using official Google Maps API
"""

import requests
import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass
import time


@dataclass
class Review:
    """Review data structure"""
    author_name: str
    author_url: str
    rating: int
    text: str
    time: int  # UNIX timestamp
    relative_time: str
    language: str
    profile_photo_url: Optional[str] = None
    
    @property
    def timestamp(self) -> datetime.datetime:
        """Convert UNIX timestamp to datetime"""
        return datetime.datetime.fromtimestamp(self.time)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'author_name': self.author_name,
            'author_url': self.author_url,
            'rating': self.rating,
            'text': self.text,
            'time': self.time,
            'timestamp': self.timestamp,
            'relative_time': self.relative_time,
            'language': self.language,
            'profile_photo_url': self.profile_photo_url
        }


class GoogleMapsAPICollector:
    """
    Google Maps API based review collector
    
    Features:
    - Fast (1-2 seconds per request)
    - Reliable (official API)
    - Rate limit handling
    - Error recovery
    """
    
    BASE_URL = "https://maps.googleapis.com/maps/api/place/details/json"
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    
    def __init__(self, api_key: str, language: str = "tr"):
        """
        Initialize API collector
        
        Args:
            api_key: Google Maps API key
            language: Language code (default: tr for Turkish)
        """
        self.api_key = api_key
        self.language = language
        self.request_count = 0
        self.last_request_time = None
    
    def collect_reviews(
        self, 
        place_id: str, 
        business_name: Optional[str] = None
    ) -> Dict:
        """
        Collect latest reviews for a place
        
        Args:
            place_id: Google Maps Place ID
            business_name: Optional business name for logging
            
        Returns:
            Dictionary with:
                - success: bool
                - reviews: List[Review]
                - business_name: str
                - place_id: str
                - total_count: int
                - error: str (if failed)
        """
        print(f"\n🔍 Collecting reviews for Place ID: {place_id}")
        if business_name:
            print(f"   📍 Business: {business_name}")
        
        # Build API URL
        url = (
            f"{self.BASE_URL}"
            f"?placeid={place_id}"
            f"&fields=name,reviews"
            f"&reviews_sort=newest"
            f"&key={self.api_key}"
            f"&language={self.language}"
        )
        
        # Make request with retry logic
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                print(f"   🌐 API Request (attempt {attempt}/{self.MAX_RETRIES})")
                
                response = requests.get(url, timeout=10)
                self.request_count += 1
                self.last_request_time = datetime.datetime.now()
                
                data = response.json()
                
                if response.status_code == 200:
                    if 'result' in data:
                        # Extract business name from API if not provided
                        if not business_name and 'name' in data['result']:
                            business_name = data['result']['name']
                        
                        # Parse reviews
                        if 'reviews' in data['result']:
                            reviews = self._parse_reviews(data['result']['reviews'])
                            
                            print(f"   ✅ Success: {len(reviews)} reviews collected")
                            print(f"   📊 API requests made: {self.request_count}")
                            
                            return {
                                'success': True,
                                'reviews': reviews,
                                'business_name': business_name or 'Unknown',
                                'place_id': place_id,
                                'total_count': len(reviews),
                                'collected_at': datetime.datetime.now()
                            }
                        else:
                            print(f"   ⚠️ No reviews found for this place")
                            return {
                                'success': True,
                                'reviews': [],
                                'business_name': business_name or 'Unknown',
                                'place_id': place_id,
                                'total_count': 0,
                                'collected_at': datetime.datetime.now()
                            }
                    else:
                        error_msg = data.get('status', 'Unknown error')
                        print(f"   ❌ API Error: {error_msg}")
                        
                        if attempt < self.MAX_RETRIES:
                            print(f"   🔄 Retrying in {self.RETRY_DELAY} seconds...")
                            time.sleep(self.RETRY_DELAY)
                            continue
                        
                        return {
                            'success': False,
                            'error': error_msg,
                            'place_id': place_id
                        }
                else:
                    print(f"   ❌ HTTP Error: {response.status_code}")
                    
                    if attempt < self.MAX_RETRIES:
                        print(f"   🔄 Retrying in {self.RETRY_DELAY} seconds...")
                        time.sleep(self.RETRY_DELAY)
                        continue
                    
                    return {
                        'success': False,
                        'error': f'HTTP {response.status_code}',
                        'place_id': place_id
                    }
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Request Exception: {e}")
                
                if attempt < self.MAX_RETRIES:
                    print(f"   🔄 Retrying in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
                    continue
                
                return {
                    'success': False,
                    'error': str(e),
                    'place_id': place_id
                }
        
        # If we get here, all retries failed
        return {
            'success': False,
            'error': 'Max retries exceeded',
            'place_id': place_id
        }
    
    def _parse_reviews(self, raw_reviews: List[Dict]) -> List[Review]:
        """
        Parse raw API reviews into Review objects
        
        Args:
            raw_reviews: Raw review data from API
            
        Returns:
            List of Review objects
        """
        reviews = []
        
        for raw in raw_reviews:
            try:
                review = Review(
                    author_name=raw.get('author_name', 'Anonymous'),
                    author_url=raw.get('author_url', ''),
                    rating=raw.get('rating', 0),
                    text=raw.get('text', ''),
                    time=raw.get('time', 0),
                    relative_time=raw.get('relative_time_description', ''),
                    language=raw.get('language', self.language),
                    profile_photo_url=raw.get('profile_photo_url')
                )
                reviews.append(review)
            except Exception as e:
                print(f"   ⚠️ Failed to parse review: {e}")
                continue
        
        return reviews
    
    def get_stats(self) -> Dict:
        """Get collector statistics"""
        return {
            'total_requests': self.request_count,
            'last_request': self.last_request_time,
            'language': self.language
        }


# Test function
def test_collector():
    """Test the API collector"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not api_key:
        print("❌ GOOGLE_MAPS_API_KEY not found in .env file")
        return
    
    # Test with Istanbul Airport
    place_id = "ChIJqZW8Cvb_n0ARBuUkyCzgDDg"
    business_name = "İstanbul Havalimanı"
    
    collector = GoogleMapsAPICollector(api_key)
    result = collector.collect_reviews(place_id, business_name)
    
    if result['success']:
        print(f"\n✅ Collection successful!")
        print(f"📍 Business: {result['business_name']}")
        print(f"📊 Total reviews: {result['total_count']}")
        print(f"\n📝 Latest reviews:")
        
        for i, review in enumerate(result['reviews'][:3], 1):
            print(f"\n--- Review {i} ---")
            print(f"👤 Author: {review.author_name}")
            print(f"⭐ Rating: {review.rating}")
            print(f"📅 Time: {review.timestamp}")
            print(f"💬 Text: {review.text[:100]}...")
    else:
        print(f"\n❌ Collection failed: {result['error']}")


if __name__ == "__main__":
    test_collector()
