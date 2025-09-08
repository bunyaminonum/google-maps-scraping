#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from database_test import ReviewsDatabase

def check_ratings():
    """Rating dağılımını kontrol et"""
    print("📊 Rating Dağılımı Kontrolü...")
    
    db = ReviewsDatabase()
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    # Rating dağılımı
    print("\n📈 Rating Dağılımı:")
    cursor.execute("SELECT rating, COUNT(*) as count FROM reviews GROUP BY rating ORDER BY rating;")
    for row in cursor.fetchall():
        rating, count = row
        print(f"   ⭐ {rating} yıldız: {count} yorum")
    
    # En son eklenen yorumlar
    print("\n📝 En Son 10 Yorum:")
    cursor.execute("""
        SELECT reviewer_name, rating, review_text, timestamp_parsed 
        FROM reviews 
        ORDER BY timestamp_parsed DESC 
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        name, rating, text, timestamp = row
        text_preview = text[:50] + "..." if text and len(text) > 50 else text or "Sadece puanlama"
        print(f"   👤 {name or 'Anonim'}: {rating}⭐ - {text_preview}")
    
    # Session ortalamları
    print("\n📋 Session Ortalamaları:")
    cursor.execute("""
        SELECT session_id, 
               COUNT(*) as review_count,
               AVG(CAST(rating AS FLOAT)) as avg_rating,
               datetime(created_at) as created
        FROM reviews 
        WHERE session_id IS NOT NULL
        GROUP BY session_id 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        session, count, avg_rating, created = row
        print(f"   🗂️ {session}: {count} yorum, ⭐{avg_rating:.1f} ortalama ({created})")
    
    conn.close()

if __name__ == "__main__":
    check_ratings()
