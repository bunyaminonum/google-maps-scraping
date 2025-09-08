#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from database_test import ReviewsDatabase

def check_schema_and_ratings():
    """Database şeması ve rating'leri kontrol et"""
    print("📊 Veritabanı Kontrolü...")
    
    db = ReviewsDatabase()
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    # Tablo şeması
    print("\n📋 Reviews Tablosu Şeması:")
    cursor.execute("PRAGMA table_info(reviews);")
    for row in cursor.fetchall():
        print(f"   {row[1]} ({row[2]}) - {row}")
    
    # Rating dağılımı
    print("\n📈 Rating Dağılımı:")
    cursor.execute("SELECT rating, COUNT(*) as count FROM reviews GROUP BY rating ORDER BY rating;")
    for row in cursor.fetchall():
        rating, count = row
        print(f"   ⭐ {rating} yıldız: {count} yorum")
    
    # En son eklenen yorumlar (sadece business name ile)
    print("\n📝 En Son 10 Yorum:")
    cursor.execute("""
        SELECT reviewer_name, rating, business_name, 
               CASE 
                   WHEN review_text IS NULL OR review_text = '' THEN 'Sadece puanlama'
                   ELSE substr(review_text, 1, 50) || '...'
               END as text_preview
        FROM reviews 
        ORDER BY rowid DESC 
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        name, rating, business, text_preview = row
        print(f"   👤 {name or 'Anonim'}: {rating}⭐ [{business or 'N/A'}] - {text_preview}")
    
    # Session kolonunu kontrol et
    print("\n🔍 Scrape Session ID Kontrolü:")
    cursor.execute("SELECT scrape_session_id, COUNT(*) FROM reviews WHERE scrape_session_id IS NOT NULL GROUP BY scrape_session_id ORDER BY COUNT(*) DESC LIMIT 5;")
    sessions = cursor.fetchall()
    if sessions:
        for session_id, count in sessions:
            print(f"   🗂️ {session_id}: {count} yorum")
    else:
        print("   ❌ Hiç session ID bulunamadı")
    
    conn.close()

if __name__ == "__main__":
    check_schema_and_ratings()
