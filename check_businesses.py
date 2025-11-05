#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check all businesses in database"""

import sqlite3

conn = sqlite3.connect('reviews.db')
cursor = conn.cursor()

print("\n" + "="*60)
print("📊 ALL BUSINESSES IN DATABASE")
print("="*60)

# Get all businesses with Place IDs
cursor.execute("""
    SELECT business_name, business_url 
    FROM reviews 
    WHERE business_url LIKE 'ChIJ%' 
    GROUP BY business_name 
    ORDER BY business_name
""")

businesses = cursor.fetchall()

for i, (name, place_id) in enumerate(businesses, 1):
    print(f"\n{i}. {name}")
    print(f"   Place ID: {place_id}")

conn.close()

print("\n" + "="*60)
print(f"Total: {len(businesses)} businesses")
print("="*60)
