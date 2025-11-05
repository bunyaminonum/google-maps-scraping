#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manually fix Sabiha Gokcen Airport Place ID in database
"""

import sqlite3

conn = sqlite3.connect('reviews.db')
cursor = conn.cursor()

# Update all Sabiha Gokcen Airport reviews to have correct Place ID
place_id = "ChIJU6Ek9MvbyhQRdNqYgE3K76w"
business_name = "Sabiha Gokcen Airport"

cursor.execute("""
    UPDATE reviews 
    SET business_url = ? 
    WHERE business_name = ?
""", (place_id, business_name))

conn.commit()

print("="*60)
print("✅ Updated Sabiha Gokcen Airport Place ID")
print("="*60)
print(f"Business: {business_name}")
print(f"Place ID: {place_id}")
print(f"Rows updated: {cursor.rowcount}")
print("="*60)

conn.close()

# Verify
print("\n📊 Verifying update...")
import subprocess
subprocess.run(["python", "check_businesses.py"])
