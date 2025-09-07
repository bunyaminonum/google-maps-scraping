"""
Test script - Basit çalışma testi
"""

def test_imports():
    """İmport testleri"""
    try:
        import selenium
        print(f"✅ Selenium kurulu: {selenium.__version__}")
        
        from selenium import webdriver
        print("✅ WebDriver import edildi")
        
        import pandas as pd
        print(f"✅ Pandas kurulu: {pd.__version__}")
        
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ WebDriver Manager import edildi")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import hatası: {e}")
        return False

def test_scraper_import():
    """Scraper class'ı test et"""
    try:
        from google_maps_scraper import GoogleMapsReviewScraper, Review
        print("✅ Scraper class'ı import edildi")
        
        # Review dataclass test
        test_review = Review(
            reviewer_name="Test User",
            review_text="Test yorum",
            rating="5/5",
            date="1 day ago",
            is_new=True
        )
        print(f"✅ Review modeli çalışıyor: {test_review.reviewer_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Scraper import hatası: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Google Maps Scraper Test")
    print("=" * 40)
    
    # Test 1: Paket importları
    print("\n1. Paket testleri:")
    if not test_imports():
        print("❌ Testler başarısız - paket kurulumunu kontrol edin")
        exit(1)
    
    # Test 2: Scraper import
    print("\n2. Scraper testleri:")
    if not test_scraper_import():
        print("❌ Scraper testleri başarısız")
        exit(1)
    
    print("\n🎉 Tüm testler başarılı!")
    print("\nKullanım için:")
    print("python example.py")
    print("veya")
    print("python google_maps_scraper.py")
