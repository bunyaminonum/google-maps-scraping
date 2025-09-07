#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veritabanı tarih formatları analizi
"""

from database_test import ReviewsDatabase
import pandas as pd

def analyze_dates():
    """Veritabanındaki tarih formatlarını analiz et"""
    
    db = ReviewsDatabase('main_reviews.db')
    df = db.get_all_reviews()
    
    print(f'📊 Toplam yorum: {len(df)}')
    print('\n📅 Benzersiz tarih formatları:')
    
    unique_dates = df['date_original'].unique()
    
    for i, date in enumerate(unique_dates[:20]):
        print(f'   {i+1:2d}. "{date}"')
    
    # Sorunlu formatları bul
    print('\n⚠️ Kategorize edilmemiş zaman formatları:')
    problematic_dates = df[df['time_category'] == 'Zaman bilgisi belirsiz']['date_original'].unique()
    
    for date in problematic_dates[:10]:
        print(f'   ❌ "{date}"')
    
    # En son yorumları kontrol et
    print('\n🕐 Son 10 yorumun tarihleri:')
    latest = df.head(10)
    for i, row in latest.iterrows():
        print(f'   {row["date_original"]} -> {row.get("time_category", "N/A")}')

if __name__ == "__main__":
    analyze_dates()
