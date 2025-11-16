import googlemaps
import pandas as pd
import time

# -------------------- AYARLAR --------------------
# Google Cloud Console'dan aldığın API Anahtarını buraya yapıştır.
API_KEY = 'AIzaSyB6QMvuAnLKLGyKxjLUZRo50hGgy_Z1O18'

# Sonuçların kaydedileceği dosya adı
OUTPUT_FILE = 'tum_turkiye_BIM_listesi.csv'

# Taranacak İller Listesi (81 İl)
TURKIYE_ILLERI = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Amasya", "Ankara", "Antalya", "Artvin", "Aydın", "Balıkesir",
    "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa", "Çanakkale", "Çankırı", "Çorum", "Denizli",
    "Diyarbakır", "Edirne", "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun", "Gümüşhane",
    "Hakkari", "Hatay", "Isparta", "Mersin", "İstanbul", "İzmir", "Kars", "Kastamonu", "Kayseri", "Kırklareli",
    "Kırşehir", "Kocaeli", "Konya", "Kütahya", "Malatya", "Manisa", "Kahramanmaraş", "Mardin", "Muğla", "Muş",
    "Nevşehir", "Niğde", "Ordu", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Tekirdağ", "Tokat",
    "Trabzon", "Tunceli", "Şanlıurfa", "Uşak", "Van", "Yozgat", "Zonguldak", "Aksaray", "Bayburt", "Karaman",
    "Kırıkkale", "Batman", "Şırnak", "Bartın", "Ardahan", "Iğdır", "Yalova", "Karabük", "Kilis", "Osmaniye", "Düzce"
]
# -------------------------------------------------

def scan_stores():
    gmaps = googlemaps.Client(key=API_KEY)
    all_stores = []
    seen_place_ids = set() # Tekrar eden şubeleri engellemek için

    print(f"Taramaya başlanıyor... Toplam {len(TURKIYE_ILLERI)} il taranacak.")
    print("-" * 50)

    for city in TURKIYE_ILLERI:
        query = f"Bim {city}"
        print(f"Şehir taranıyor: {city}...")
        
        try:
            # Text Search kullanarak o şehirdeki DeFacto'ları ara
            # Bu yöntem o bölgedeki en alakalı sonuçları (genellikle 20'ye kadar) getirir.
            places_result = gmaps.places(query=query)
            
            if places_result['status'] == 'OK':
                results = places_result['results']
                found_count = 0
                
                for place in results:
                    place_id = place.get('place_id')
                    name = place.get('name')
                    address = place.get('formatted_address')
                    
                    # Eğer this şube daha önce eklenmediyse listeye ekle
                    if place_id and place_id not in seen_place_ids:
                        # Sadece isminde 'BIM' geçenleri al (Bazen yan dükkanları getirebilir)
                        if "BIM" in name or "Bim" in name or "bim" in name or " BİM" in name:
                            all_stores.append({
                                'Sehir': city,
                                'Sube_Adi': name,
                                'Adres': address,
                                'Place_ID': place_id
                            })
                            seen_place_ids.add(place_id)
                            found_count += 1
                
                print(f"  -> {found_count} yeni şube bulundu.")
            else:
                print(f"  -> Sonuç bulunamadı.")

            # API limitlerine takılmamak için kısa bir bekleme
            time.sleep(2)

        except Exception as e:
            print(f"  -> HATA: {city} aranırken bir sorun oluştu: {e}")

    # Sonuçları Kaydet
    if all_stores:
        df = pd.DataFrame(all_stores)
        df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        print("-" * 50)
        print(f"TARAMA TAMAMLANDI!")
        print(f"Toplam {len(all_stores)} benzersiz Bim şubesi bulundu.")
        print(f"Dosya oluşturuldu: {OUTPUT_FILE}")
    else:
        print("Hiçbir şube bulunamadı. API anahtarınızı ve kotanızı kontrol edin.")

if __name__ == "__main__":
    # API Key kontrolü
    if API_KEY == 'BURAYA_API_ANAHTARINI_YAPISTIR':
        print("Lütfen kodun başındaki API_KEY alanına kendi anahtarınızı yazın.")
    else:
        scan_stores()