#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zaman parsing test scripti
"""

from database_test import ReviewsDatabase
from database_scraper import DatabaseGoogleMapsScraper
import pandas as pd

def test_time_parsing():
    """Zaman parsing'i test et"""
    
    # Test verileri
    test_times = [
        "bir saat önce",
        "2 saat önce", 
        "bir gün önce",
        "3 gün önce",
        "bir hafta önce",
        "2 hafta önce",
        "bir ay önce",
        "3 ay önce",
        "bir yıl önce",
        "2 yıl önce",
        "bir hafta önce düzenlendi",
        "bir ay önce düzenlendi"
    ]
    
    # Scraper oluştur
    scraper = DatabaseGoogleMapsScraper()
    
    print("🧪 Zaman Parsing Testi")
    print("=" * 50)
    
    for time_str in test_times:
        try:
            timestamp = scraper.parse_relative_time_to_timestamp(time_str)
            category = scraper.categorize_timestamp(timestamp)
            print(f"✅ '{time_str}' -> {timestamp.strftime('%Y-%m-%d %H:%M')} ({category})")
        except Exception as e:
            print(f"❌ '{time_str}' -> HATA: {e}")
    
    print("\n" + "=" * 50)
    
    # Veritabanından gerçek verileri test et
    print("🗄️ Veritabanı Verilerini Test Et")
    
    db = ReviewsDatabase('main_reviews.db')
    df = db.get_all_reviews()
    
    # "bir yıl önce" içeren kayıtları bul
    year_records = df[df['date_original'].str.contains('yıl', na=False)]
    
    print(f"\n📊 'yıl' içeren kayıt sayısı: {len(year_records)}")
    
    if len(year_records) > 0:
        print("\n🔍 'yıl' içeren kayıtlar:")
        for i, record in year_records.head(5).iterrows():
            original_date = record['date_original']
            time_category = record.get('time_category', 'N/A')
            
            # Yeniden parse et
            try:
                timestamp = scraper.parse_relative_time_to_timestamp(original_date)
                new_category = scraper.categorize_timestamp(timestamp)
                print(f"   '{original_date}' -> DB: {time_category}, Yeni: {new_category}")
            except Exception as e:
                print(f"   '{original_date}' -> HATA: {e}")

if __name__ == "__main__":
    test_time_parsing()
