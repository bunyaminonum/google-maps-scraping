
import requests
import json
import datetime  # Tarih çevirisi için bu kütüphaneyi ekliyoruz
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Ayarlarınızı Buraya Girin veya .env dosyasından alın ---
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')  # .env dosyasından alınır
PLACE_ID = "ChIJqZW8Cvb_n0ARBuUkyCzgDDg" # İstanbul Havalimanı
# ----------------------------------

if not API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY not found in .env file!")

# API URL'si (Dil olarak Türkçe istiyoruz)
url = (
    f"https://maps.googleapis.com/maps/api/place/details/json"
    f"?placeid={PLACE_ID}"
    f"&fields=reviews"
    f"&reviews_sort=newest"
    f"&key={API_KEY}"
    f"&language=tr"
)

response = requests.get(url)
data = response.json()

if response.status_code == 200 and 'result' in data and 'reviews' in data['result']:
    print(f"'{PLACE_ID}' için en yeni 5 yorumun tüm detayları:\n")
    
    reviews = data['result']['reviews']
    
    for i, review in enumerate(reviews):
        
        # UNIX timestamp'i al
        timestamp = review.get('time')
        # Okunabilir bir tarihe çevir
        readable_date = datetime.datetime.fromtimestamp(timestamp)
        
        print(f"--- Yorum {i+1} ---")
        print(f"Yazar: {review.get('author_name')}")
        print(f"Profil Linki: {review.get('author_url')}")
        print(f"Puan: {review.get('rating')}")
        print(f"Dil: {review.get('language')}")
        
        # İki farklı tarih formatını da yazdıralım
        print(f"Göreceli Tarih: {review.get('relative_time_description')}")
        print(f"KESİN TARİH: {readable_date}") 
        
        print(f"Metin: {review.get('text')}\n") # Bu sefer metnin tamamını alalım
        
else:
    print(f"Yorumlar alınamadı. Hata: {data.get('status')}")