#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Duplicate Detection Debug Script
Check if duplicate detection is working correctly
"""

import sqlite3
from database_test import ReviewsDatabase

def check_duplicates():
    """Check for duplicate reviews in database"""
    
    db = ReviewsDatabase()
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("🔍 DUPLICATE DETECTION CHECK")
    print("=" * 70)
    
    # 1. Check total reviews
    cursor.execute("SELECT COUNT(*) FROM reviews")
    total = cursor.fetchone()[0]
    print(f"\n📊 Total reviews: {total}")
    
    # 2. Check unique hashes
    cursor.execute("SELECT COUNT(DISTINCT review_hash) FROM reviews")
    unique = cursor.fetchone()[0]
    print(f"🔑 Unique hashes: {unique}")
    
    # 3. Find duplicates
    duplicates = total - unique
    print(f"⚠️  Duplicates: {duplicates}")
    
    if duplicates > 0:
        print(f"\n❌ WARNING: {duplicates} duplicate reviews found!")
        
        # Show duplicate groups
        cursor.execute("""
            SELECT review_hash, COUNT(*) as count, 
                   GROUP_CONCAT(id) as ids,
                   business_name, reviewer_name, date_original
            FROM reviews 
            GROUP BY review_hash 
            HAVING count > 1
            ORDER BY count DESC
            LIMIT 5
        """)
        
        print("\n🔍 Top duplicate groups:")
        print("-" * 70)
        for row in cursor.fetchall():
            hash_val, count, ids, biz, reviewer, date = row
            print(f"\nHash: {hash_val[:16]}...")
            print(f"  Count: {count}")
            print(f"  IDs: {ids}")
            print(f"  Business: {biz}")
            print(f"  Reviewer: {reviewer}")
            print(f"  Date: {date}")
    else:
        print("\n✅ No duplicates found! Detection working correctly.")
    
    # 4. Check hash distribution
    cursor.execute("""
        SELECT business_name, COUNT(*) as total, COUNT(DISTINCT review_hash) as unique_count
        FROM reviews
        GROUP BY business_name
    """)
    
    print("\n\n📍 Reviews by Business:")
    print("-" * 70)
    for row in cursor.fetchall():
        biz, tot, uni = row
        dups = tot - uni
        status = "✅" if dups == 0 else f"⚠️  {dups} dups"
        print(f"{status} {biz}: {tot} total, {uni} unique")
    
    # 5. Check most recent session
    cursor.execute("""
        SELECT scrape_session_id, COUNT(*) as count, 
               MIN(created_at) as first_added
        FROM reviews
        GROUP BY scrape_session_id
        ORDER BY first_added DESC
        LIMIT 5
    """)
    
    print("\n\n🕐 Recent Sessions:")
    print("-" * 70)
    for row in cursor.fetchall():
        session, count, added = row
        print(f"{added}: {session} ({count} reviews)")
    
    conn.close()
    print("\n" + "=" * 70)

if __name__ == "__main__":
    check_duplicates()
