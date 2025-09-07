"""
Firefox Basit Test
"""

from google_maps_scraper_firefox import GoogleMapsReviewScraper

def firefox_test():
    """Firefox ile basit test"""
    
    print("🦊 Firefox Test Başlıyor")
    print("=" * 40)
    
    try:
        # Scraper'ı başlat
        print("🚀 Firefox scraper başlatılıyor...")
        scraper = GoogleMapsReviewScraper(headless=False)
        
        # Basit bir işletme testi
        business_name = "McDonald's"
        location = "Istanbul"
        
        print(f"\n🔍 Test işletmesi: {business_name} - {location}")
        
        # Yorumları al
        reviews = scraper.get_latest_reviews(
            business_name=business_name,
            location=location,
            max_reviews=3  # Sadece 3 yorum test için
        )
        
        if reviews:
            print(f"\n✅ {len(reviews)} yorum başarıyla alındı!")
            
            for i, review in enumerate(reviews, 1):
                print(f"\n{i}. {review.reviewer_name}")
                print(f"   ⭐ {review.rating}")
                print(f"   📅 {review.date}")
                print(f"   💬 {review.review_text[:100]}...")
                if review.is_new:
                    print("   🆕 YENİ!")
            
            # CSV'ye kaydet
            scraper.save_to_csv(reviews, "firefox_test_reviews.csv")
        else:
            print("❌ Hiç yorum alınamadı")
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            scraper.close()
        except:
            pass

if __name__ == "__main__":
    firefox_test()
