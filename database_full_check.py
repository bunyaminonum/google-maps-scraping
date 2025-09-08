#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from database_test import ReviewsDatabase
import os

def check_all_databases():
    """Tüm veritabanlarını kontrol et"""
    print("🔍 Tüm Veritabanları Kontrol Ediliyor...")
    
    # Workspace'deki tüm .db dosyalarını bul
    db_files = []
    for file in os.listdir('.'):
        if file.endswith('.db'):
            db_files.append(file)
    
    print(f"\n📋 Bulunan veritabanları: {db_files}")
    
    for db_file in db_files:
        print(f"\n📊 {db_file} Analizi:")
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # Tablo varlığını kontrol et
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='reviews';")
            if not cursor.fetchone():
                print("   ❌ Reviews tablosu bulunamadı")
                conn.close()
                continue
            
            # Toplam kayıt
            cursor.execute("SELECT COUNT(*) FROM reviews;")
            total = cursor.fetchone()[0]
            print(f"   📈 Toplam yorum: {total}")
            
            if total > 0:
                # Rating dağılımı
                cursor.execute("SELECT rating, COUNT(*) FROM reviews GROUP BY rating ORDER BY rating;")
                ratings = cursor.fetchall()
                print(f"   📊 Rating dağılımı:")
                for rating, count in ratings:
                    print(f"      ⭐ {rating}: {count} yorum")
                
                # Murat'ı özellikle ara
                cursor.execute("SELECT reviewer_name, rating FROM reviews WHERE reviewer_name LIKE '%Murat%';")
                murat_reviews = cursor.fetchall()
                if murat_reviews:
                    print(f"   👤 Murat yorumları:")
                    for name, rating in murat_reviews:
                        print(f"      {name}: {rating}⭐")
            
            conn.close()
            
        except Exception as e:
            print(f"   ❌ Hata: {e}")
    
    # Dashboard'ın hangi veritabanını kullandığını kontrol et
    print(f"\n🎯 Dashboard Veritabanı Kontrolü:")
    print(f"   📋 ReviewsDatabase varsayılan path'i kontrol ediliyor...")
    
    db = ReviewsDatabase()
    print(f"   🗂️ Kullanılan veritabanı: {db.db_path}")
    
    # Bu veritabanındaki Murat'ı kontrol et
    df = db.get_all_reviews()
    murat_data = df[df['reviewer_name'].str.contains('Murat', na=False)]
    if not murat_data.empty:
        print(f"   👤 Dashboard'ta Murat yorumları:")
        for _, row in murat_data.iterrows():
            print(f"      {row['reviewer_name']}: {row['rating']}⭐")
    else:
        print(f"   ❌ Dashboard'ta Murat yorumu bulunamadı")

if __name__ == "__main__":
    check_all_databases()
