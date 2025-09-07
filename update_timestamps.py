#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veritabanı zaman verilerini güncelleme scripti
"""

from database_test import ReviewsDatabase
from database_scraper import DatabaseGoogleMapsScraper
import sqlite3

def update_database_timestamps():
    """Veritabanındaki mevcut kayıtların zaman verilerini yeni parsing ile günceller"""
    
    print("🔄 Veritabanı Zaman Güncelleme Başlıyor...")
    print("=" * 50)
    
    # Veritabanı bağlantısı
    db = ReviewsDatabase('main_reviews.db')
    scraper = DatabaseGoogleMapsScraper()
    
    # Tüm kayıtları getir
    df = db.get_all_reviews()
    print(f"📊 Toplam {len(df)} kayıt bulundu")
    
    # SQLite bağlantısı
    conn = sqlite3.connect('main_reviews.db')
    cursor = conn.cursor()
    
    updated_count = 0
    
    for index, row in df.iterrows():
        try:
            review_id = row['id']
            original_date = row['date_original']
            old_category = row.get('time_category', 'N/A')
            
            # Yeni timestamp ve kategori hesapla
            new_timestamp = scraper.parse_relative_time_to_timestamp(original_date)
            new_category = scraper.categorize_timestamp(new_timestamp)
            
            # Eğer kategori değiştiyse güncelle
            if old_category != new_category:
                cursor.execute('''
                    UPDATE reviews 
                    SET timestamp_parsed = ?, time_category = ?
                    WHERE id = ?
                ''', (new_timestamp.isoformat(), new_category, review_id))
                
                print(f"✅ ID {review_id}: '{original_date}' -> {old_category} ➜ {new_category}")
                updated_count += 1
            
        except Exception as e:
            print(f"❌ ID {review_id} güncellenemedi: {e}")
    
    # Değişiklikleri kaydet
    conn.commit()
    conn.close()
    
    print("=" * 50)
    print(f"🎉 Güncelleme tamamlandı!")
    print(f"📈 {updated_count} kayıt güncellendi")
    
    # Sonuçları kontrol et
    print("\n🔍 Güncelleme sonrası durum:")
    
    df_updated = db.get_all_reviews()
    time_categories = df_updated['time_category'].value_counts()
    
    for category, count in time_categories.items():
        print(f"   📊 {category}: {count} kayıt")

if __name__ == "__main__":
    update_database_timestamps()
