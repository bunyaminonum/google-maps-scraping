# Google Maps Review Scraper

Bu proje Google Haritalar'dan işletme yorumlarını çıkarmak için geliştirilmiştir.

## 🌟 Özellikler

- İşletme arama ve seçimi
- En yeni yorumları filtreleme
- Yorum detaylarını çıkarma (ad, puan, tarih, metin)
- "New" etiketli yorumları belirleme
- CSV formatında kaydetme
- Bot detection koruması
- Headless/görünür mod seçeneği

## 📋 Gereksinimler

- Python 3.7+
- Chrome tarayıcısı
- requirements.txt'teki paketler

## 🚀 Kurulum

1. **Gerekli paketleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Chrome tarayıcısının kurulu olduğundan emin olun**

## 💻 Kullanım

### Basit Kullanım
```bash
python example.py
```

### Programatik Kullanım
```python
from google_maps_scraper import GoogleMapsReviewScraper

# Scraper'ı başlat
scraper = GoogleMapsReviewScraper(headless=False)

try:
    # Yorumları al
    reviews = scraper.get_latest_reviews(
        business_name="Maxx Royal Kemer Resort",
        location="Antalya",
        max_reviews=10
    )
    
    # CSV'ye kaydet
    scraper.save_to_csv(reviews, "reviews.csv")
    
finally:
    scraper.close()
```

## 📁 Dosya Yapısı

```
google-maps-scraping/
├── google_maps_scraper.py  # Ana scraper class'ı
├── example.py              # Interaktif örnek
├── demo.py                 # Basit demo
├── test_setup.py          # Kurulum testi
├── requirements.txt        # Python bağımlılıkları
└── README.md              # Bu dosya
```

## 🧪 Test

Kurulumun doğru olup olmadığını test etmek için:
```bash
python test_setup.py
```

## ⚠️ Önemli Notlar

1. **Etik Kullanım**: Bu araç eğitim amaçlıdır
2. **Rate Limiting**: Çok hızlı istek göndermeyin
3. **Robot.txt**: Google'ın kurallarına uyun
4. **Chrome Gerekli**: Chrome tarayıcısı kurulu olmalı

## 🛠️ Teknik Detaylar

### Analiz Edilen HTML Elementler

HTML dosyalarından çıkarılan key selector'lar:

- **Yorum Container**: `.jftiEf.fontBodyMedium`
- **Yorumcu Adı**: `.d4r55.fontTitleMedium`
- **Yorum Metni**: `.wiI7pd`
- **Puan**: `.fzvQIb`
- **Tarih**: `.xRkPPb`
- **"New" Etiketi**: `.J7sVM.W8gobe`
- **"Newest" Butonu**: `button[aria-label*='Newest']`

### Review Veri Modeli

```python
@dataclass
class Review:
    reviewer_name: str    # Yorumcu adı
    review_text: str      # Yorum metni
    rating: str          # Puan (örn: "5/5")
    date: str           # Tarih (örn: "1 day ago")
    is_new: bool        # "New" etiketi var mı?
    platform: str       # Platform adı
```

## 🐛 Sorun Giderme

### ChromeDriver Hatası
```bash
# WebDriver Manager otomatik çözer, manuel kurulum gerekmez
```

### Selenium Import Hatası
```bash
pip install --upgrade selenium
```

### Element Bulunamadı Hatası
- Google Maps arayüzü değişmiş olabilir
- Selector'ları güncellemeniz gerekebilir

## 📊 Çıktı Örneği

```
🚀 Maxx Royal Kemer Resort işletmesi için yorum çıkarma başlıyor...
🔍 Aranan: Maxx Royal Kemer Resort Antalya
✅ İlk işletme seçildi
✅ Yorumlar sekmesine geçildi
✅ En yeni yorumlar seçildi
📝 12 yorum bulundu
✅ Yorum 1: Office Restaurant 26...
✅ Yorum 2: Andrzej Glen...
🎉 Toplam 10 yorum başarıyla çıkarıldı
💾 10 yorum 'latest_reviews.csv' dosyasına kaydedildi
🔒 Tarayıcı kapatıldı
```

---
**Versiyon**: 1.0.0  
**Geliştirici**: Google Maps Scraper Project
