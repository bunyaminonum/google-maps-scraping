#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sabiha Gökçen Place ID Finder
Use Google Place ID Finder to get the correct ID
"""

print("="*70)
print("🔍 HOW TO FIND THE CORRECT PLACE ID FOR SABIHA GÖKÇEN")
print("="*70)

print("""
📋 STEPS:

1. Go to: https://developers.google.com/maps/documentation/places/web-service/place-id

2. Search for: "Istanbul Sabiha Gokcen International Airport"
   or Turkish: "İstanbul Sabiha Gökçen Havalimanı"

3. Click on the airport on the map

4. Copy the Place ID (starts with ChIJ...)

5. Update the Place ID in one of these files:
   
   A) In settings.py:
      c:\\Users\\onumb\\OneDrive\\Masaüstü\\confluent\\google-maps-scraping-1\\api_pipeline\\config\\settings.py
      
      Change this line:
      ("ChIJjUzc_GH4yhQRuBbTdFuNAAg", "İstanbul Sabiha Gökçen Havalimanı"),
      
      To:
      ("YOUR_NEW_PLACE_ID_HERE", "İstanbul Sabiha Gökçen Havalimanı"),
   
   B) Or add directly in the dashboard:
      - Click "🚀 Collect Latest Reviews"
      - Enter the Place ID manually

📍 ALTERNATIVE METHOD:

1. Go to Google Maps: https://www.google.com/maps
2. Search: "Sabiha Gokcen Airport"
3. Look at the URL - it will have something like:
   https://www.google.com/maps/place/.../@...data=...!3s0x14cac7e0fcb21deb:0x51e5db8a6054172d
   
   The Place ID might be encoded in the URL

4. Or right-click on the location → "Share" → Copy link
   Then decode the Place ID from the link

""")

print("="*70)
print("💡 QUICK TEST:")
print("="*70)
print("""
After getting the Place ID, test it with:

    python -c "from api_pipeline.collectors.google_maps_api import GoogleMapsAPICollector; \\
               from dotenv import load_dotenv; import os; load_dotenv(); \\
               api_key = os.getenv('GOOGLE_MAPS_API_KEY'); \\
               collector = GoogleMapsAPICollector(api_key); \\
               result = collector.collect_reviews('YOUR_PLACE_ID', 'Sabiha Gökçen'); \\
               print('✅ WORKS!' if result.get('success') else f'❌ FAILED: {result.get(\"error\")}')"
""")

print("="*70)
