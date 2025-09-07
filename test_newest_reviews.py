"""
En Yeni Yorumlar Özelliği Test Scripti
"En alakalı" dan "En yeni" ye geçiş testi
"""

from firefox_optimized_scraper import FirefoxGoogleMapsReviewScraper

def test_newest_reviews_feature():
    """En yeni yorumlar seçme özelliğini test et"""
    print("🆕 EN YENİ YORUMLAR ÖZELLİĞİ TESTİ")
    print("=" * 40)
    
    scraper = FirefoxGoogleMapsReviewScraper(headless=False)
    
    # Test için İstanbul Havalimanı URL'si
    test_url = "https://www.google.com/maps/place/%C4%B0stanbul+Havaliman%C4%B1/@41.262981,28.7325741,15z/data=!3m1!4b1!4m6!3m5!1s0x409ffff60abc95a9:0x380ce02cc824e506!8m2!3d41.2768187!4d28.7301397!16s%2Fm%2F0q3_6fq?entry=ttu&g_ep=EgoyMDI1MDkwMy4wIKXMDSoASAFQAw%3D%3D"
    
    try:
        print("🔧 Test adımları:")
        print("1. İşletme sayfasına git")
        print("2. Yorumlar sekmesine geç")
        print("3. 'En alakalı' dropdown'ını bul")
        print("4. 'En yeni' seçeneğini seç")
        print("5. En yeni yorumları çıkar")
        print("-" * 40)
        
        reviews = scraper.scrape_reviews(
            business_name="İstanbul Havalimanı",
            max_reviews=5,
            google_maps_url=test_url
        )
        
        if reviews:
            print(f"\n🎉 BAŞARILI! {len(reviews)} en yeni yorum çıkarıldı")
            
            # Tarih analizini yap
            print(f"\n📅 TARİH ANALİZİ:")
            for i, review in enumerate(reviews, 1):
                print(f"{i}. {review.reviewer_name}: {review.date}")
            
            # En yeni yorumların tarih kontrolü
            recent_dates = [r.date for r in reviews if 'gün önce' in r.date or 'hafta önce' in r.date]
            if recent_dates:
                print(f"\n✅ En yeni yorumlar bulundu: {len(recent_dates)} adet")
            else:
                print(f"\n⚠️ Çok yeni yorumlar bulunamadı, ama sıralama değişmiş olabilir")
            
        else:
            print("❌ Test başarısız: Yorum çıkarılamadı")
            
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        import traceback
        traceback.print_exc()

def test_sorting_comparison():
    """Sıralama karşılaştırma testi"""
    print("🔄 SIRALAMA KARŞILAŞTIRMA TESTİ")
    print("=" * 35)
    
    print("Bu test 'En alakalı' vs 'En yeni' sıralamasını karşılaştırır")
    print("Manuel olarak dropdown'ı gözlemleyin...")
    
    scraper = FirefoxGoogleMapsReviewScraper(headless=False)
    
    test_url = "https://www.google.com/maps/place/%C4%B0stanbul+Havaliman%C4%B1/@41.262981,28.7325741,15z/data=!3m1!4b1!4m6!3m5!1s0x409ffff60abc95a9:0x380ce02cc824e506!8m2!3d41.2768187!4d28.7301397!16s%2Fm%2F0q3_6fq?entry=ttu&g_ep=EgoyMDI1MDkwMy4wIKXMDSoASAFQAw%3D%3D"
    
    try:
        # WebDriver'ı başlat
        scraper.setup_driver()
        
        # İşletme sayfasına git
        if scraper.navigate_to_business_url(test_url):
            
            # Yorumlar sekmesine git
            if scraper.navigate_to_reviews():
                
                print("\n1️⃣ Önce 'En alakalı' sıralaması ile yorumları görelim...")
                input("Yorumları manuel gözlemleyin ve Enter'a basın...")
                
                # En yeni yorumları seç
                print("\n2️⃣ Şimdi 'En yeni' sıralamasına geçiyoruz...")
                if scraper.select_newest_reviews():
                    print("✅ 'En yeni' seçildi!")
                    input("Yorumların sıralamadaki değişikliği gözlemleyin ve Enter'a basın...")
                    
                    # Şimdi yorumları çıkar
                    reviews = scraper.extract_reviews(3)
                    
                    if reviews:
                        print(f"\n📋 EN YENİ {len(reviews)} YORUM:")
                        for i, review in enumerate(reviews, 1):
                            print(f"{i}. 👤 {review.reviewer_name}")
                            print(f"   📅 {review.date}")
                            print(f"   💬 {review.review_text[:80]}...")
                            print()
                    
                else:
                    print("❌ 'En yeni' seçilemedi")
            else:
                print("❌ Yorumlar sekmesi açılamadı")
        else:
            print("❌ İşletme sayfasına gidilemedi")
            
    except Exception as e:
        print(f"❌ Karşılaştırma testi hatası: {e}")
        
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    print("🧪 EN YENİ YORUMLAR TEST ARACI")
    print("=" * 35)
    print("1. Otomatik test (en yeni yorumlar)")
    print("2. Manuel karşılaştırma testi")
    
    choice = input("\nSeçiminizi yapın (1 veya 2): ").strip()
    
    if choice == "2":
        test_sorting_comparison()
    else:
        test_newest_reviews_feature()
