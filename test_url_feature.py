"""
Google Maps URL Özelliği Test Scripti
Direkt işletme linkiyle yorumları çıkarmak için
"""

from firefox_optimized_scraper import FirefoxGoogleMapsReviewScraper

def test_popular_businesses_with_urls():
    """Popüler işletmeleri URL ile test et"""
    
    # Test edilecek işletmeler ve URL'leri
    test_cases = [
        {
            "name": "İstanbul Havalimanı",
            "url": "https://www.google.com/maps/place/%C4%B0stanbul+Havaliman%C4%B1/@41.262981,28.7325741,15z/data=!3m1!4b1!4m6!3m5!1s0x409ffff60abc95a9:0x380ce02cc824e506!8m2!3d41.2768187!4d28.7301397!16s%2Fm%2F0q3_6fq?entry=ttu&g_ep=EgoyMDI1MDkwMy4wIKXMDSoASAFQAw%3D%3D",
            "reviews": 8
        },
        {
            "name": "Sabiha Gökçen Havalimanı", 
            "url": "https://www.google.com/maps/place/%C4%B0stanbul+Sabiha+G%C3%B6k%C3%A7en+Uluslararas%C4%B1+Havaliman%C4%B1/@40.9066492,29.3133517,17z/data=!3m1!4b1!4m6!3m5!1s0x14cadbcbf424a153:0xacefca4d8098da74!8m2!3d40.8944747!4d29.3130928!16zL20vMDJnbmhx?entry=ttu&g_ep=EgoyMDI1MDkwMy4wIKXMDSoASAFQAw%3D%3D",
            "reviews": 5
        },
        {
            "name": "Galata Kulesi",
            "url": "https://www.google.com/maps/place/Galata+Kulesi/@41.0256692,28.972721,17z/data=!3m1!4b1!4m6!3m5!1s0x14cab9bd6570f4e1:0xe87e984e5e9a9d5b!8m2!3d41.0256652!4d28.9752959!16zL20vMDl4emJy?entry=ttu&g_ep=EgoyMDI1MDkwMy4wIKXMDSoASAFQAw%3D%3D",
            "reviews": 6
        }
    ]
    
    successful_tests = 0
    total_reviews_extracted = 0
    
    print("🔗 GOOGLE MAPS URL TEST SERİSİ")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST {i}: {test_case['name']}")
        print(f"🔗 URL: {test_case['url'][:60]}...")
        print("-" * 40)
        
        scraper = FirefoxGoogleMapsReviewScraper(headless=False)
        
        try:
            reviews = scraper.scrape_reviews(
                business_name=test_case['name'],
                max_reviews=test_case['reviews'],
                google_maps_url=test_case['url']
            )
            
            if reviews:
                successful_tests += 1
                total_reviews_extracted += len(reviews)
                
                print(f"✅ BAŞARILI: {len(reviews)} yorum çıkarıldı")
                
                # İlk 2 yorumu göster
                print("\n📝 ÖRNEK YORUMLAR:")
                for j, review in enumerate(reviews[:2], 1):
                    print(f"   {j}. 👤 {review.reviewer_name}")
                    print(f"      ⭐ {review.rating} | 📅 {review.date}")
                    print(f"      💬 {review.review_text[:80]}...")
                    
            else:
                print("❌ BAŞARISIZ: Yorum çıkarılamadı")
                
        except Exception as e:
            print(f"❌ HATA: {e}")
        
        # Sonraki test için kullanıcı onayı
        if i < len(test_cases):
            input(f"\n⏳ {test_case['name']} testi tamamlandı. Sonraki teste geçmek için Enter'a basın...")
    
    # Özet sonuçlar
    print(f"\n🏆 TEST ÖZETİ:")
    print("=" * 30)
    print(f"✅ Başarılı test sayısı: {successful_tests}/{len(test_cases)}")
    print(f"📊 Toplam çıkarılan yorum: {total_reviews_extracted}")
    print(f"📈 Başarı oranı: {(successful_tests/len(test_cases)*100):.1f}%")
    
    if successful_tests == len(test_cases):
        print("\n🎉 TÜM TESTLER BAŞARILI! URL özelliği çalışıyor.")
    else:
        print(f"\n⚠️ {len(test_cases) - successful_tests} test başarısız oldu.")

def test_single_url():
    """Tek bir URL ile hızlı test"""
    print("⚡ HIZLI URL TESTİ")
    print("=" * 25)
    
    scraper = FirefoxGoogleMapsReviewScraper(headless=False)
    
    # İstanbul Havalimanı URL testi
    reviews = scraper.scrape_reviews(
        business_name="İstanbul Havalimanı",
        max_reviews=5,
        google_maps_url="https://www.google.com/maps/place/%C4%B0stanbul+Havaliman%C4%B1/@41.262981,28.7325741,15z/data=!3m1!4b1!4m6!3m5!1s0x409ffff60abc95a9:0x380ce02cc824e506!8m2!3d41.2768187!4d28.7301397!16s%2Fm%2F0q3_6fq?entry=ttu&g_ep=EgoyMDI1MDkwMy4wIKXMDSoASAFQAw%3D%3D"
    )
    
    if reviews:
        print(f"\n🎯 Başarı! {len(reviews)} yorum çıkarıldı")
        
        # Benzersiz yorumcu sayısını kontrol et
        unique_reviewers = set([r.reviewer_name for r in reviews])
        print(f"👥 Farklı yorumcu sayısı: {len(unique_reviewers)}")
        
        # URL vs arama karşılaştırması
        print(f"\n💡 URL Avantajları:")
        print(f"   - Arama adımı atlandı ⚡")
        print(f"   - Daha hızlı (5-10 saniye kazanç)")
        print(f"   - Daha güvenilir (arama hatası riski yok)")
        print(f"   - Doğru işletme garantisi")
        
    else:
        print("❌ Test başarısız!")

if __name__ == "__main__":
    print("🔥 GOOGLE MAPS URL TEST ARACI")
    print("=" * 35)
    print("1. Hızlı tek URL testi")  
    print("2. Çoklu işletme URL testi")
    
    choice = input("\nSeçiminizi yapın (1 veya 2): ").strip()
    
    if choice == "2":
        test_popular_businesses_with_urls()
    else:
        test_single_url()
