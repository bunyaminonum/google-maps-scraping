#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from database_test import ReviewsDatabase

def analyze_ratings():
    """Rating durumunu detaylı analiz et"""
    print("📊 Rating Analizi...")
    
    db = ReviewsDatabase()
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    # Toplam veri sayısı
    cursor.execute("SELECT COUNT(*) FROM reviews;")
    total_count = cursor.fetchone()[0]
    print(f"\n📋 Toplam yorum sayısı: {total_count}")
    
    # Rating dağılımı
    print("\n📈 Rating Dağılımı:")
    cursor.execute("SELECT rating, COUNT(*) as count FROM reviews GROUP BY rating ORDER BY rating;")
    for row in cursor.fetchall():
        rating, count = row
        percentage = (count / total_count) * 100
        print(f"   ⭐ {rating} yıldız: {count} yorum ({percentage:.1f}%)")
    
    # 0 rating'li yorumları analiz et
    cursor.execute("SELECT COUNT(*) FROM reviews WHERE rating = 0;")
    zero_count = cursor.fetchone()[0]
    print(f"\n❌ 0 rating'li yorumlar: {zero_count}")
    
    # Session bazlı analiz
    print("\n📋 Session Bazlı Rating Analizi:")
    cursor.execute("""
        SELECT scrape_session_id, 
               COUNT(*) as total_reviews,
               COUNT(CASE WHEN rating > 0 THEN 1 END) as valid_ratings,
               COUNT(CASE WHEN rating = 0 THEN 1 END) as zero_ratings,
               AVG(CASE WHEN rating > 0 THEN rating END) as avg_valid_rating
        FROM reviews 
        WHERE scrape_session_id IS NOT NULL
        GROUP BY scrape_session_id 
        ORDER BY scrape_session_id DESC
    """)
    
    for row in cursor.fetchall():
        session_id, total, valid, zero, avg_rating = row
        print(f"   🗂️ {session_id}:")
        print(f"      📊 Toplam: {total}, ✅ Geçerli: {valid}, ❌ Sıfır: {zero}")
        if avg_rating:
            print(f"      ⭐ Ortalama: {avg_rating:.1f}")
    
    # En son yorumları göster
    print("\n📝 En Son 5 Yorum (Rating Kontrolü):")
    cursor.execute("""
        SELECT reviewer_name, rating, scrape_session_id, created_at
        FROM reviews 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        name, rating, session, created = row
        status = "✅" if rating > 0 else "❌"
        print(f"   {status} {name}: {rating}⭐ [{session}] - {created}")
    
    conn.close()

if __name__ == "__main__":
    analyze_ratings()
