#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find Correct Place ID for Sabiha Gökçen
"""

from api_pipeline.collectors.google_maps_api import GoogleMapsAPICollector
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('GOOGLE_MAPS_API_KEY')

# Try common Place IDs for Sabiha Gökçen
test_ids = [
    ("ChIJjUzc_GH4yhQRuBbTdFuNAAg", "From settings (WRONG)"),
    ("ChIJ_bIz_GH4yhQRV4t2rAh6xOY", "Alternative 1"),
    ("ChIJf_bIz-D4yhQRuBbTdFuNAAg", "Alternative 2"),
    ("ChIJ4T2Tx-D4yhQRqZaZX0T-J6Q", "Alternative 3"),
]

collector = GoogleMapsAPICollector(api_key)

print("🔍 Testing Place IDs for Sabiha Gökçen Havalimanı")
print("="*60)

for place_id, description in test_ids:
    print(f"\n📍 Testing: {description}")
    print(f"   Place ID: {place_id}")
    
    result = collector.collect_reviews(place_id, "Test")
    
    if result.get('success'):
        print(f"   ✅ WORKS! Found: {result.get('business_name')}")
        print(f"   📊 Reviews: {result.get('total_count')}")
        break
    else:
        print(f"   ❌ Failed: {result.get('error')}")

print("\n" + "="*60)
print("💡 If none work, get Place ID from:")
print("   https://developers.google.com/maps/documentation/places/web-service/place-id")
