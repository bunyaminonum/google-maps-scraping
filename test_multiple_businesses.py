"""
Farklı İşletme ile Test - Firefox Google Maps Scraper
"""

from firefox_optimized_scraper import FirefoxGoogleMapsReviewScraper

def test_different_businesses():
    """Farklı işletmelerle test yap"""
    
    businesses = [
        {"name": "Maxx Royal Kemer Resort", "location": "Antalya", "reviews": 10},
        {"name": "İstanbul Havalimanı", "location": "İstanbul", "reviews": 8},
        {"name": "Galata Kulesi", "location": "İstanbul", "reviews": 5}
    ]
    
    for i, business in enumerate(businesses, 1):
        print(f"\n🏢 TEST {i}: {business['name']}")
        print("=" * 60)
        
        scraper = FirefoxGoogleMapsReviewScraper(headless=False)
        
        try:
            reviews = scraper.scrape_reviews(
                business_name=business['name'],
                location=business['location'],
                max_reviews=business['reviews']
            )
            
            if reviews:
                print(f"✅ {business['name']}: {len(reviews)} yorum başarıyla çıkarıldı")
                
                # Farklı yorumcu sayısını kontrol et
                unique_reviewers = set([r.reviewer_name for r in reviews])
                print(f"👥 Farklı yorumcu sayısı: {len(unique_reviewers)}")
                
                # Yorumları kısaca göster
                for j, review in enumerate(reviews[:3], 1):
                    print(f"   {j}. {review.reviewer_name}: {review.review_text[:50]}...")
            else:
                print(f"❌ {business['name']}: Yorum çıkarılamadı")
                
        except Exception as e:
            print(f"❌ {business['name']} test hatası: {e}")
        
        # Sonraki test için bekle
        if i < len(businesses):
            input("\n⏳ Sonraki teste geçmek için Enter'a basın...")

if __name__ == "__main__":
    test_different_businesses()
