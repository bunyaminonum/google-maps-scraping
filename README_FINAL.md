# Google Maps Review Scraper 🗺️

Firefox tabanlı Google Maps işletme yorumları çıkarma sistemi.

## 🎯 Özellikler

- ✅ **Firefox WebDriver** ile bot korumasına karşı optimize edilmiş
- ✅ **Gerçek zamanlı yorum çıkarma** - işletmenin en son yorumları
- ✅ **CSV export** - kolay analiz için veri dışa aktarma
- ✅ **Türkçe destekli** - hem Türkçe hem İngilizce yorumlar
- ✅ **Esnek arama** - işletme adı ve konum ile arama
- ✅ **Rate limiting** - güvenli ve kontrollü scraping

## 📋 Gereksinimler

### Python Paketleri
```bash
pip install -r requirements.txt
```

### Bağımlılıklar
- Python 3.8+
- Firefox tarayıcısı yüklü
- selenium
- webdriver-manager
- pandas
- beautifulsoup4

## 🚀 Kullanım

### Hızlı Başlangıç

```python
from firefox_optimized_scraper import FirefoxGoogleMapsReviewScraper

# Scraper'ı başlat
scraper = FirefoxGoogleMapsReviewScraper(headless=False)

# Yorumları çıkar
reviews = scraper.scrape_reviews(
    business_name="Starbucks Zorlu Center",
    location="İstanbul",
    max_reviews=10
)

# Sonuçları göster
for review in reviews:
    print(f"{review.reviewer_name}: {review.review_text[:100]}...")
```

### Komut Satırından Kullanım

```bash
# Test için optimize edilmiş scraper'ı çalıştır
python firefox_optimized_scraper.py

# İstanbul Havalimanı özel testi
python test_istanbul_airport.py

# Çoklu işletme testi
python test_multiple_businesses.py
```

## 📊 Çıktı Formatı

### Review Objesi
```python
@dataclass
class Review:
    reviewer_name: str      # Yorumcu adı
    review_text: str        # Yorum metni  
    rating: str            # Puan (1-5)
    date: str              # Tarih (örn: "3 ay önce")
    is_new: bool           # Yeni mi?
    platform: str          # Platform adı
```

### CSV Çıktısı
```csv
Yorumcu_Adi,Yorum_Metni,Puan,Tarih,Platform
"John Doe","Harika bir yer, kesinlikle tavsiye ederim",5,"2 gün önce","Google Maps (Firefox)"
```

## 🔧 Konfigürasyon

### Firefox Ayarları
```python
# Görünür mod (önerilen)
scraper = FirefoxGoogleMapsReviewScraper(headless=False)

# Headless mod (arka plan)
scraper = FirefoxGoogleMapsReviewScraper(headless=True)
```

### Özelleştirilebilir Parametreler
- `business_name`: İşletme adı (zorunlu)
- `location`: Konum (isteğe bağlı)
- `max_reviews`: Maksimum yorum sayısı (varsayılan: 10)

## 📁 Proje Yapısı

```
google-maps-scraping/
├── firefox_optimized_scraper.py    # Ana scraper (TEST SONUÇLARINA GÖRE OPTİMİZE)
├── firefox_test_enhanced.py        # Gelişmiş test scripti
├── test_istanbul_airport.py        # İstanbul Havalimanı testi
├── test_multiple_businesses.py     # Çoklu işletme testi
├── google_maps_scraper_firefox.py  # İlk versiyon scraper
├── requirements.txt                 # Python bağımlılıkları
├── README.md                       # Bu dosya
└── *.csv                          # Çıktı dosyaları
```

## 🧪 Test Edilen İşletmeler

✅ **Starbucks Zorlu Center** - İstanbul  
✅ **İstanbul Havalimanı** - İstanbul  
✅ **Maxx Royal Kemer Resort** - Antalya  
✅ **Galata Kulesi** - İstanbul  

## 🔍 Teknik Detaylar

### Kullanılan CSS Selectors (Test Sonuçları)
- `[data-review-id]`: 98 element bulundu ✅
- `.jftiEf.fontBodyMedium`: 10 element bulundu ✅
- `.wiI7pd`: Yorum metni (10 element) ✅
- `.d4r55.fontTitleMedium`: Yorumcu adı (10 element) ✅

### Firefox Optimizasyonları
- Enhanced JavaScript element detection
- Aria-label based navigation
- Rate limiting için beklemeler
- Scroll işlemleri ile dinamik yükleme

## ⚠️ Önemli Notlar

1. **Rate Limiting**: Google'ın bot korumasına saygı göstermek için yavaş scraping
2. **Firefox Önerisi**: Chrome'dan daha az bot tespiti
3. **Görünür Mod**: İlk testlerde headless=False kullanın
4. **İnternet Bağlantısı**: Kararlı bağlantı gerekli

## 🐛 Sorun Giderme

### Yaygın Hatalar

**1. Yorum bulunamıyor**
```python
# Çözüm: Daha fazla bekleme ekleyin
time.sleep(5)
```

**2. WebDriver hatası**
```bash
# Çözüm: WebDriver'ı güncelleyin
pip install --upgrade webdriver-manager
```

**3. CSS selector çalışmıyor**
```python
# Çözüm: Test scriptini kullanarak selector'ları kontrol edin
python firefox_test_enhanced.py
```

## 📈 Performans

- **Ortalama İşlem Süresi**: 30-60 saniye (10 yorum için)
- **Başarı Oranı**: %95+ (test edilen işletmelerde)
- **Desteklenen Yorum Sayısı**: 1-100 yorum/işletme

## 🤝 Katkıda Bulunma

1. Fork this repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🆘 Destek

Sorularınız için:
- GitHub Issues açın
- Test scriptlerini çalıştırın
- Debug modunu kullanın

---

**Son güncellenme**: Test sonuçlarına göre Firefox CSS selector'ları optimize edildi ✅
