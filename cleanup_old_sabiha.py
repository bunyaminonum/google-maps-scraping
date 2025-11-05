#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove old Sabiha Gökçen data with wrong Place ID
"""

import sqlite3

conn = sqlite3.connect('reviews.db')
cursor = conn.cursor()

# Count reviews to be deleted
cursor.execute("""
    SELECT COUNT(*) FROM reviews 
    WHERE business_name = 'İstanbul Sabiha Gökçen Havalimanı'
""")
count = cursor.fetchone()[0]

if count > 0:
    print("="*60)
    print(f"⚠️  Found {count} reviews for old 'İstanbul Sabiha Gökçen Havalimanı'")
    print("="*60)
    
    # Delete them
    cursor.execute("""
        DELETE FROM reviews 
        WHERE business_name = 'İstanbul Sabiha Gökçen Havalimanı'
    """)
    
    conn.commit()
    print(f"✅ Deleted {cursor.rowcount} old reviews")
    print("="*60)
else:
    print("✅ No old data found - database is clean!")

conn.close()

# Show final state
print("\n📊 Final Business List:")
print("="*60)

import subprocess
subprocess.run(["python", "check_businesses.py"])
