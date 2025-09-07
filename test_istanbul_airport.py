"""
İstanbul Havalimanı Test - Tek Seferlik
"""

from firefox_optimized_scraper import FirefoxGoogleMapsReviewScraper

def test_istanbul_airport():
    """İstanbul Havalimanı ile test"""
    
    print("🛫 İSTANBUL HAVALİMANI TEST")
    print("=" * 50)
    
    scraper = FirefoxGoogleMapsReviewScraper(headless=False)
    
    reviews = scraper.scrape_reviews(
        business_name="İstanbul Havalimanı",
        location="İstanbul",
        max_reviews=10
    )
    
    if reviews:
        print(f"\n✅ BAŞARILI: {len(reviews)} yorum çıkarıldı")
        
        # Farklı yorumcu sayısını kontrol et
        unique_reviewers = set([r.reviewer_name for r in reviews])
        print(f"👥 Farklı yorumcu sayısı: {len(unique_reviewers)}")
        
        # Her yorumcuyu listele
        print("\n👤 YORUMCULAR:")
        for name in unique_reviewers:
            count = len([r for r in reviews if r.reviewer_name == name])
            print(f"   - {name}: {count} yorum")
        
        # En iyi yorumları göster
        print("\n📝 ÖNE ÇIKAN YORUMLAR:")
        for i, review in enumerate(reviews[:5], 1):
            if len(review.review_text) > 20:  # Sadece anlamlı yorumları göster
                print(f"\n{i}. 👤 {review.reviewer_name}")
                print(f"   ⭐ {review.rating} | 📅 {review.date}")
                print(f"   💬 {review.review_text[:150]}...")
    else:
        print("❌ BAŞARISIZ: Hiç yorum çıkarılamadı")

if __name__ == "__main__":
    test_istanbul_airport()
