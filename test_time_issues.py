#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Time Issues Test Script
Comprehensive test for review time handling
"""

import sqlite3
from datetime import datetime
import sys

def test_database_schema():
    """Test 1: Check database schema"""
    print("=" * 70)
    print("TEST 1: DATABASE SCHEMA")
    print("=" * 70)
    
    conn = sqlite3.connect('reviews.db')
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(reviews)")
    columns = cursor.fetchall()
    
    print("\n📋 Reviews Table Structure:")
    for col in columns:
        print(f"   - {col[1]:20s} {col[2]:15s} {'(PRIMARY KEY)' if col[5] else ''}")
    
    conn.close()
    
    # Check for time-related columns
    time_columns = [col[1] for col in columns if 'time' in col[1].lower() or 'date' in col[1].lower()]
    print(f"\n⏰ Time-related columns found: {', '.join(time_columns)}")
    
    return columns

def test_review_data():
    """Test 2: Check actual review data"""
    print("\n" + "=" * 70)
    print("TEST 2: ACTUAL REVIEW DATA")
    print("=" * 70)
    
    conn = sqlite3.connect('reviews.db')
    cursor = conn.cursor()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM reviews")
    total = cursor.fetchone()[0]
    print(f"\n📊 Total reviews in database: {total}")
    
    if total == 0:
        print("⚠️  No reviews found in database!")
        conn.close()
        return
    
    # Get latest 5 reviews
    cursor.execute("""
        SELECT 
            id,
            business_name, 
            reviewer_name, 
            date_original, 
            timestamp_parsed,
            time_category,
            rating,
            created_at
        FROM reviews 
        ORDER BY id DESC 
        LIMIT 5
    """)
    
    reviews = cursor.fetchall()
    
    print("\n📝 Latest 5 Reviews:")
    print("-" * 70)
    
    for review in reviews:
        print(f"\nReview ID: {review[0]}")
        print(f"  Business: {review[1][:40]}")
        print(f"  Reviewer: {review[2]}")
        print(f"  Date Original: {review[3]}")
        print(f"  Timestamp Parsed: {review[4]}")
        print(f"  Time Category: {review[5]}")
        print(f"  Rating: {review[6]}")
        print(f"  Created At (DB): {review[7]}")
    
    conn.close()

def test_api_time_format():
    """Test 3: Check API response time format"""
    print("\n" + "=" * 70)
    print("TEST 3: API TIME FORMAT")
    print("=" * 70)
    
    import os
    from dotenv import load_dotenv
    from api_pipeline.collectors.google_maps_api import GoogleMapsAPICollector
    
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not api_key:
        print("❌ No API key found")
        return
    
    # Test with Istanbul Airport
    place_id = "ChIJqZW8Cvb_n0ARBuUkyCzgDDg"
    
    print(f"\n🔍 Testing API collection...")
    print(f"   Place ID: {place_id}")
    
    collector = GoogleMapsAPICollector(api_key)
    result = collector.collect_reviews(place_id, "Test Location")
    
    if result['success'] and result['reviews']:
        print(f"\n✅ Collected {len(result['reviews'])} reviews")
        
        print("\n📅 Time Format Analysis:")
        print("-" * 70)
        
        for i, review in enumerate(result['reviews'][:3], 1):
            print(f"\nReview {i}:")
            print(f"  Author: {review.author_name}")
            print(f"  Time (UNIX): {review.time}")
            print(f"  Time (datetime): {review.timestamp}")
            print(f"  Relative Time: {review.relative_time}")
            print(f"  Language: {review.language}")
            
            # Check if timestamp is valid
            if review.time:
                dt = datetime.fromtimestamp(review.time)
                print(f"  ✅ Converted: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"  ❌ Invalid timestamp!")
    else:
        print(f"❌ API collection failed: {result.get('error', 'Unknown error')}")

def test_time_conversion():
    """Test 4: Test time conversion logic"""
    print("\n" + "=" * 70)
    print("TEST 4: TIME CONVERSION LOGIC")
    print("=" * 70)
    
    import time as time_module
    
    # Test UNIX timestamps
    test_timestamps = [
        1730000000,  # Recent timestamp
        int(time_module.time()),  # Current time
        1609459200,  # 2021-01-01
    ]
    
    print("\n⏱️  UNIX Timestamp Conversion Test:")
    print("-" * 70)
    
    for ts in test_timestamps:
        try:
            dt = datetime.fromtimestamp(ts)
            print(f"Timestamp: {ts}")
            print(f"  → {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  → {dt.isoformat()}")
        except Exception as e:
            print(f"❌ Error converting {ts}: {e}")
        print()

def test_dashboard_compatibility():
    """Test 5: Check Streamlit dashboard data loading"""
    print("\n" + "=" * 70)
    print("TEST 5: DASHBOARD DATA LOADING")
    print("=" * 70)
    
    from database_test import ReviewsDatabase
    
    db = ReviewsDatabase("reviews.db")
    
    # Get all reviews
    df = db.get_all_reviews()
    
    if df.empty:
        print("⚠️  No data returned from database")
        return
    
    print(f"\n📊 DataFrame Info:")
    print(f"   Rows: {len(df)}")
    print(f"   Columns: {len(df.columns)}")
    
    print(f"\n📋 Column Names:")
    for col in df.columns:
        print(f"   - {col}")
    
    # Check time-related columns
    time_cols = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
    print(f"\n⏰ Time Columns: {', '.join(time_cols)}")
    
    # Sample data
    if len(df) > 0:
        print(f"\n📝 Sample Review (first row):")
        review = df.iloc[0]
        for col in time_cols:
            if col in df.columns:
                print(f"   {col}: {review[col]}")

def run_all_tests():
    """Run all tests"""
    print("\n")
    print("🧪" * 35)
    print(" " * 10 + "TIME ISSUES COMPREHENSIVE TEST")
    print("🧪" * 35)
    print("\n")
    
    try:
        test_database_schema()
        test_review_data()
        test_api_time_format()
        test_time_conversion()
        test_dashboard_compatibility()
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
