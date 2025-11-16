#!/usr/bin/env python3
"""Update business locations using Google Maps API"""

import sqlite3
import time
from api_pipeline.collectors.google_maps_api import GoogleMapsAPICollector
from api_pipeline.config.settings import Config

def update_business_locations():
    """Fetch and update location data for all businesses"""
    
    collector = GoogleMapsAPICollector(Config.GOOGLE_MAPS_API_KEY)
    conn = sqlite3.connect('reviews.db')
    cursor = conn.cursor()
    
    # Get all businesses
    cursor.execute("SELECT id, name, place_id, latitude FROM businesses")
    businesses = cursor.fetchall()
    
    print(f"📍 Found {len(businesses)} businesses")
    print("-" * 50)
    
    updated_count = 0
    
    for business_id, name, place_id, current_lat in businesses:
        if current_lat is not None:
            print(f"✅ {name} - Already has location")
            continue
        
        print(f"🔍 Fetching location for: {name}")
        
        try:
            details = collector.get_place_details(place_id)
            
            if details['success']:
                cursor.execute("""
                    UPDATE businesses 
                    SET address = ?, latitude = ?, longitude = ?
                    WHERE id = ?
                """, (details['address'], details['latitude'], details['longitude'], business_id))
                
                print(f"   ✅ Updated: {details['address']}")
                print(f"   📍 Coordinates: {details['latitude']}, {details['longitude']}")
                updated_count += 1
            else:
                print(f"   ❌ Failed: {details.get('error')}")
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    conn.commit()
    conn.close()
    
    print("-" * 50)
    print(f"✅ Updated {updated_count} business locations")

if __name__ == "__main__":
    update_business_locations()
