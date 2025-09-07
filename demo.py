"""
Demo script - Sadece test amaçlı
"""

from google_maps_scraper import GoogleMapsReviewScraper

def quick_demo():
    """Hızlı demo"""
    print("🚀 Google Maps Scraper Demo")
    print("=" * 40)
    
    # Not: Bu sadece class'ın çalışıp çalışmadığını test eder
    # Gerçek web scraping için chrome driver gerekir
    
    try:
        # Class'ı test et (driver başlatmadan)
        print("✅ Scraper class'ı oluşturuluyor...")
        
        # Sadece import ve class yapısını test et
        from google_maps_scraper import Review
        
        # Örnek veri
        sample_review = Review(
            reviewer_name="Test Kullanıcı",
            review_text="Bu harika bir yer! Çok beğendim.",
            rating="5/5",
            date="2 gün önce",
            is_new=True
        )
        
        print(f"✅ Örnek yorum oluşturuldu:")
        print(f"   👤 {sample_review.reviewer_name}")
        print(f"   ⭐ {sample_review.rating}")
        print(f"   📅 {sample_review.date}")
        print(f"   💬 {sample_review.review_text}")
        print(f"   🆕 Yeni: {'Evet' if sample_review.is_new else 'Hayır'}")
        
        print("\n🎉 Demo başarılı!")
        print("\nGerçek kullanım için:")
        print("python example.py")
        
    except Exception as e:
        print(f"❌ Demo hatası: {e}")

if __name__ == "__main__":
    quick_demo()
