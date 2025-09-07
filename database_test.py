#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Maps Reviews Database Test
Veritabanı entegrasyonu test scripti
"""

import sqlite3
import pandas as pd
from datetime import datetime, timezone
import json
import os

class ReviewsDatabase:
    def __init__(self, db_path="reviews.db"):
        """Veritabanı bağlantısını başlat"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Veritabanı tablolarını oluştur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Reviews tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            business_name TEXT NOT NULL,
            business_url TEXT,
            reviewer_name TEXT,
            rating INTEGER,
            date_original TEXT,
            review_text TEXT,
            timestamp_parsed DATETIME,
            time_category TEXT,
            scrape_session_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Scrape sessions tablosu
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS scrape_sessions (
            id TEXT PRIMARY KEY,
            business_name TEXT NOT NULL,
            business_url TEXT,
            target_text_reviews INTEGER,
            target_total_ratings INTEGER,
            actual_text_reviews INTEGER,
            actual_total_ratings INTEGER,
            average_rating REAL,
            scrape_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'completed'
        )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Veritabanı tabloları oluşturuldu/kontrol edildi")
    
    def save_scrape_session(self, session_data):
        """Scrape session bilgilerini kaydet"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO scrape_sessions 
        (id, business_name, business_url, target_text_reviews, target_total_ratings,
         actual_text_reviews, actual_total_ratings, average_rating, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_data['session_id'],
            session_data['business_name'],
            session_data.get('business_url', ''),
            session_data.get('target_text_reviews', 0),
            session_data.get('target_total_ratings', 0),
            session_data.get('actual_text_reviews', 0),
            session_data.get('actual_total_ratings', 0),
            session_data.get('average_rating', 0),
            session_data.get('status', 'completed')
        ))
        
        conn.commit()
        conn.close()
        print(f"✅ Scrape session kaydedildi: {session_data['session_id']}")
    
    def save_reviews(self, reviews_data, session_id):
        """Yorumları veritabanına kaydet"""
        if not reviews_data:
            print("⚠️ Kaydedilecek yorum bulunamadı")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        saved_count = 0
        
        for review in reviews_data:
            cursor.execute('''
            INSERT INTO reviews 
            (business_name, business_url, reviewer_name, rating, date_original,
             review_text, timestamp_parsed, time_category, scrape_session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                review.get('business_name', ''),
                review.get('business_url', ''),
                review.get('reviewer_name', ''),
                review.get('rating'),
                review.get('date', ''),
                review.get('review_text', ''),
                review.get('timestamp_parsed'),
                review.get('time_category', ''),
                session_id
            ))
            saved_count += 1
        
        conn.commit()
        conn.close()
        print(f"✅ {saved_count} yorum veritabanına kaydedildi")
    
    def get_all_reviews(self):
        """Tüm yorumları getir"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
        SELECT r.*, s.business_name as session_business_name, s.scrape_date
        FROM reviews r
        LEFT JOIN scrape_sessions s ON r.scrape_session_id = s.id
        ORDER BY r.created_at DESC
        '''
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def get_reviews_by_business(self, business_name):
        """Belirli işletmenin yorumlarını getir"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
        SELECT * FROM reviews 
        WHERE business_name LIKE ?
        ORDER BY created_at DESC
        '''
        
        df = pd.read_sql_query(query, conn, params=[f'%{business_name}%'])
        conn.close()
        
        return df
    
    def get_statistics(self):
        """Genel istatistikleri getir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Toplam yorum sayısı
        cursor.execute("SELECT COUNT(*) FROM reviews")
        total_reviews = cursor.fetchone()[0]
        
        # Toplam işletme sayısı
        cursor.execute("SELECT COUNT(DISTINCT business_name) FROM reviews")
        total_businesses = cursor.fetchone()[0]
        
        # Ortalama puan
        cursor.execute("SELECT AVG(rating) FROM reviews WHERE rating IS NOT NULL")
        avg_rating = cursor.fetchone()[0]
        
        # Metin yorumu olanlar
        cursor.execute("SELECT COUNT(*) FROM reviews WHERE review_text IS NOT NULL AND review_text != ''")
        text_reviews = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_reviews': total_reviews,
            'total_businesses': total_businesses,
            'average_rating': round(avg_rating, 2) if avg_rating else 0,
            'text_reviews': text_reviews,
            'rating_only': total_reviews - text_reviews
        }

def test_database():
    """Veritabanı fonksiyonlarını test et"""
    print("🧪 VERİTABANI TEST BAŞLIYOR...")
    print("=" * 50)
    
    # Veritabanı oluştur
    db = ReviewsDatabase("test_reviews.db")
    
    # Test verisi oluştur
    test_session = {
        'session_id': f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'business_name': 'Test İşletmesi',
        'business_url': 'https://test.com',
        'target_text_reviews': 5,
        'target_total_ratings': 10,
        'actual_text_reviews': 3,
        'actual_total_ratings': 8,
        'average_rating': 4.2,
        'status': 'completed'
    }
    
    # Session kaydet
    print("1️⃣ Test session kaydediliyor...")
    db.save_scrape_session(test_session)
    
    # Test yorumları oluştur
    test_reviews = [
        {
            'business_name': 'Test İşletmesi',
            'business_url': 'https://test.com',
            'reviewer_name': 'Test Kullanıcı 1',
            'rating': 5,
            'date': '2 saat önce',
            'review_text': 'Harika bir yer, kesinlikle tavsiye ederim!',
            'timestamp_parsed': datetime.now().isoformat(),
            'time_category': 'Bugün'
        },
        {
            'business_name': 'Test İşletmesi',
            'business_url': 'https://test.com',
            'reviewer_name': 'Test Kullanıcı 2',
            'rating': 4,
            'date': '1 gün önce',
            'review_text': 'Güzel hizmet ama biraz pahalı',
            'timestamp_parsed': datetime.now().isoformat(),
            'time_category': 'Dün'
        },
        {
            'business_name': 'Test İşletmesi',
            'business_url': 'https://test.com',
            'reviewer_name': 'Test Kullanıcı 3',
            'rating': 3,
            'date': '1 hafta önce',
            'review_text': '',  # Sadece puanlama
            'timestamp_parsed': datetime.now().isoformat(),
            'time_category': 'Bu Hafta'
        }
    ]
    
    # Yorumları kaydet
    print("2️⃣ Test yorumları kaydediliyor...")
    db.save_reviews(test_reviews, test_session['session_id'])
    
    # Verileri geri oku
    print("3️⃣ Veriler okunuyor...")
    all_reviews = db.get_all_reviews()
    print(f"📊 Toplam yorum: {len(all_reviews)}")
    
    # İstatistikleri göster
    print("4️⃣ İstatistikler:")
    stats = db.get_statistics()
    for key, value in stats.items():
        print(f"   📈 {key}: {value}")
    
    # İlk birkaç yorumu göster
    print("5️⃣ İlk 3 yorum:")
    if len(all_reviews) > 0:
        for i, review in all_reviews.head(3).iterrows():
            print(f"   👤 {review['reviewer_name']} - ⭐ {review['rating']}")
            if review['review_text']:
                print(f"      💬 {review['review_text'][:50]}...")
    
    print("=" * 50)
    print("✅ VERİTABANI TESTİ TAMAMLANDI!")
    
    return db

if __name__ == "__main__":
    # Test çalıştır
    test_database()
