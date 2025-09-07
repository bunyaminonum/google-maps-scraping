#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bugünkü yorumları kontrol et
"""

from database_test import ReviewsDatabase
import pandas as pd

def check_recent_reviews():
    """En yeni yorumları kontrol et"""
    
    db = ReviewsDatabase('main_reviews.db')
    df = db.get_all_reviews()
    
    print(f'📊 Veritabanı toplam yorum: {len(df)}')
    
    print('\n🕐 En son 15 yorumun tarihleri:')
    for i in range(min(15, len(df))):
        row = df.iloc[i]
        date_orig = row['date_original']
        time_cat = row.get('time_category', 'N/A')
        reviewer = row.get('reviewer_name', 'N/A')
        print(f'   {i+1:2d}. "{date_orig}" -> {time_cat} ({reviewer})')
    
    # Bugün kategorisindeki yorumlar
    print('\n📅 Bugün kategorisindeki yorumlar:')
    today_reviews = df[df['time_category'] == 'Bugün']
    print(f'   Toplam: {len(today_reviews)} adet')
    
    if len(today_reviews) > 0:
        for i, row in today_reviews.iterrows():
            print(f'   - "{row["date_original"]}" ({row["reviewer_name"]})')
    
    # Dün kategorisindeki yorumlar
    print('\n📅 Dün kategorisindeki yorumlar:')
    yesterday_reviews = df[df['time_category'] == 'Dün']
    print(f'   Toplam: {len(yesterday_reviews)} adet')
    
    if len(yesterday_reviews) > 0:
        for i, row in yesterday_reviews.head(5).iterrows():
            print(f'   - "{row["date_original"]}" ({row["reviewer_name"]})')
    
    # Saat formatındaki yorumları ara
    print('\n🕐 "saat" içeren yorumlar:')
    hour_reviews = df[df['date_original'].str.contains('saat', na=False)]
    print(f'   Toplam: {len(hour_reviews)} adet')
    
    if len(hour_reviews) > 0:
        for i, row in hour_reviews.iterrows():
            print(f'   - "{row["date_original"]}" -> {row["time_category"]} ({row["reviewer_name"]})')

if __name__ == "__main__":
    check_recent_reviews()
