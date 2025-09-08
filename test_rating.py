#!/usr/bin/env python3
"""
Rating Extraction Test Script
Sadece rating çıkarma işlemini test eder
"""

from database_scraper import DatabaseGoogleMapsScraper

def test_rating_extraction():
    """Rating extraction'ı test et"""
    print("🧪 Rating Extraction Test Başlıyor...")
    
    # Scraper oluştur
    scraper = DatabaseGoogleMapsScraper(headless=False)  # Görünür mod
    
    try:
        # Test için kısa bir scraping yap
        result = scraper.extract_reviews_with_database(
            business_name="İstanbul Sabiha Gökçen Uluslararası Havalimanı",
            business_url="https://www.google.com/maps/place/%C4%B0stanbul+Sabiha+G%C3%B6k%C3%A7en+Uluslararas%C4%B1+Havaliman%C4%B1/@40.9066532,29.3107929,16z/data=!4m8!3m7!1s0x14cadbcbf424a153:0xacefca4d8098da74!8m2!3d40.8944747!4d29.3130928!9m1!1b1!16zL20vMDJnbmhx?entry=ttu&g_ep=EgoyMDI1MDkwMy4wIKXMDSoASAFQAw%3D%3D",
            target_text_reviews=5,  # Az sayıda test
            target_ratings=10
        )
        
        if result["success"]:
            print(f"\n✅ Test Başarılı!")
            print(f"📊 Metin yorumları: {result['text_reviews']}")
            print(f"📈 Toplam puanlama: {result['ratings_count']}")
            print(f"⭐ Ortalama puan: {result['average_rating']}")
        else:
            print(f"❌ Test Başarısız: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Test hatası: {e}")
    finally:
        scraper.close_driver()

if __name__ == "__main__":
    test_rating_extraction()
