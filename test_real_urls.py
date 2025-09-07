"""
Basit URL Test - İstanbul Havalimanı
Gerçek Google Maps URL'si ile test
"""

from firefox_optimized_scraper import FirefoxGoogleMapsReviewScraper

def test_istanbul_airport_url():
    """İstanbul Havalimanı gerçek URL ile test"""
    print("🛫 İSTANBUL HAVALİMANI URL TESTİ")
    print("=" * 40)
    
    # Gerçek Google Maps URL'si (kullanıcının verdiği)
    istanbul_airport_url = "https://www.google.com/maps/place/%C4%B0stanbul+Havaliman%C4%B1/@41.262981,28.7325741,15z/data=!3m1!4b1!4m6!3m5!1s0x409ffff60abc95a9:0x380ce02cc824e506!8m2!3d41.2768187!4d28.7301397!16s%2Fm%2F0q3_6fq?entry=ttu&g_ep=EgoyMDI1MDkwMy4wIKXMDSoASAFQAw%3D%3D"
    
    print(f"🔗 URL: {istanbul_airport_url[:80]}...")
    
    scraper = FirefoxGoogleMapsReviewScraper(headless=False)
    
    try:
        reviews = scraper.scrape_reviews(
            business_name="İstanbul Havalimanı",
            max_reviews=8,
            google_maps_url=istanbul_airport_url
        )
        
        if reviews:
            print(f"\n🎉 BAŞARILI! {len(reviews)} yorum çıkarıldı")
            
            # Benzersiz yorumcu sayısını kontrol et
            unique_reviewers = set([r.reviewer_name for r in reviews])
            print(f"👥 Farklı yorumcu sayısı: {len(unique_reviewers)}")
            
            # En iyi yorumları göster
            print(f"\n📝 EN İYİ YORUMLAR:")
            for i, review in enumerate(reviews[:3], 1):
                print(f"\n{i}. 👤 {review.reviewer_name}")
                print(f"   ⭐ Puan: {review.rating}")
                print(f"   📅 Tarih: {review.date}")
                print(f"   💬 Yorum: {review.review_text[:120]}...")
            
            print(f"\n💡 URL AVANTAJLARI:")
            print(f"   ✅ Arama adımı atlandı")
            print(f"   ✅ Doğrudan işletme sayfasına gidildi")
            print(f"   ✅ Daha hızlı (5-10 saniye kazanç)")
            print(f"   ✅ Daha güvenilir")
            
        else:
            print("❌ BAŞARISIZ: Yorum çıkarılamadı")
            
    except Exception as e:
        print(f"❌ HATA: {e}")
        import traceback
        traceback.print_exc()

def test_sabiha_gokcen_url():
    """Sabiha Gökçen Havalimanı URL ile test"""
    print("🛫 SABİHA GÖKÇEN HAVALİMANI URL TESTİ")
    print("=" * 45)
    
    # Sabiha Gökçen gerçek URL'si (kullanıcının verdiği)
    sabiha_url = "https://www.google.com/maps/place/%C4%B0stanbul+Sabiha+G%C3%B6k%C3%A7en+Uluslararas%C4%B1+Havaliman%C4%B1/@40.9066492,29.3133517,17z/data=!3m1!4b1!4m6!3m5!1s0x14cadbcbf424a153:0xacefca4d8098da74!8m2!3d40.8944747!4d29.3130928!16zL20vMDJnbmhx?entry=ttu&g_ep=EgoyMDI1MDkwMy4wIKXMDSoASAFQAw%3D%3D"
    
    print(f"🔗 URL: {sabiha_url[:80]}...")
    
    scraper = FirefoxGoogleMapsReviewScraper(headless=False)
    
    try:
        reviews = scraper.scrape_reviews(
            business_name="Sabiha Gökçen Havalimanı",
            max_reviews=6,
            google_maps_url=sabiha_url
        )
        
        if reviews:
            print(f"\n🎉 BAŞARILI! {len(reviews)} yorum çıkarıldı")
            
            # İlk birkaç yorumu göster
            for i, review in enumerate(reviews[:2], 1):
                print(f"\n{i}. 👤 {review.reviewer_name}")
                print(f"   ⭐ {review.rating} | 📅 {review.date}")
                print(f"   💬 {review.review_text[:100]}...")
            
        else:
            print("❌ BAŞARISIZ: Yorum çıkarılamadı")
            
    except Exception as e:
        print(f"❌ HATA: {e}")

if __name__ == "__main__":
    print("🔥 GOOGLE MAPS GERÇEK URL TESTİ")
    print("=" * 40)
    print("1. İstanbul Havalimanı")
    print("2. Sabiha Gökçen Havalimanı")
    print("3. Her ikisini de test et")
    
    choice = input("\nSeçiminizi yapın (1, 2 veya 3): ").strip()
    
    if choice == "1":
        test_istanbul_airport_url()
    elif choice == "2":
        test_sabiha_gokcen_url()
    elif choice == "3":
        test_istanbul_airport_url()
        input("\n⏳ İlk test tamamlandı. İkinci teste geçmek için Enter'a basın...")
        test_sabiha_gokcen_url()
    else:
        print("Geçersiz seçim, İstanbul Havalimanı testi yapılıyor...")
        test_istanbul_airport_url()
