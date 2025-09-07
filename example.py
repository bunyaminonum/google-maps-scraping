"""
Basit örnek kullanım
"""

from google_maps_scraper import GoogleMapsReviewScraper

def main():
    """Ana fonksiyon"""
    
    # Scraper'ı başlat (görünür mod)
    scraper = GoogleMapsReviewScraper(headless=False)
    
    try:
        print("🚀 Google Maps Yorum Çıkarıcı")
        print("=" * 50)
        
        # Kullanıcıdan bilgi al
        business_name = input("İşletme adı: ").strip()
        if not business_name:
            business_name = "Maxx Royal Kemer Resort"  # Varsayılan
            
        location = input("Lokasyon (opsiyonel): ").strip()
        if not location:
            location = "Antalya"  # Varsayılan
            
        max_reviews = input("Kaç yorum (varsayılan 5): ").strip()
        try:
            max_reviews = int(max_reviews) if max_reviews else 5
        except ValueError:
            max_reviews = 5
        
        print(f"\n🔍 Aranıyor: {business_name} - {location}")
        print(f"📝 Hedef yorum sayısı: {max_reviews}")
        
        # Yorumları çıkar
        reviews = scraper.get_latest_reviews(
            business_name=business_name,
            location=location,
            max_reviews=max_reviews
        )
        
        if reviews:
            print(f"\n✅ {len(reviews)} yorum başarıyla çıkarıldı!")
            
            # İlk 3 yorumu göster
            print("\n📋 İlk birkaç yorum:")
            for i, review in enumerate(reviews[:3], 1):
                print(f"\n{i}. {review.reviewer_name} - {review.rating}")
                print(f"   📅 {review.date}")
                print(f"   💬 {review.review_text[:100]}...")
                if review.is_new:
                    print("   🆕 YENİ!")
            
            # CSV'ye kaydet
            filename = f"{business_name.replace(' ', '_')}_reviews.csv"
            scraper.save_to_csv(reviews, filename)
            
            print(f"\n💾 Tüm yorumlar '{filename}' dosyasına kaydedildi")
            
        else:
            print("❌ Hiç yorum bulunamadı")
            
    except KeyboardInterrupt:
        print("\n⚠️ İşlem durduruldu")
    except Exception as e:
        print(f"\n❌ Hata: {e}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
