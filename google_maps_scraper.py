from dataclasses import dataclass
from typing import List, Optional
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException


@dataclass
class Review:
    """Yorum veri modeli"""
    reviewer_name: str
    review_text: str
    rating: str
    date: str
    is_new: bool
    platform: str = "Google Maps"


class GoogleMapsReviewScraper:
    """Google Haritalar yorum çıkarıcısı"""
    
    def __init__(self, headless: bool = False):
        """
        Scraper'ı başlat
        
        Args:
            headless: Tarayıcı görünür olmasın mı?
        """
        self.driver = None
        self.wait = None
        self.headless = headless
        self._setup_driver()
    
    def _setup_driver(self):
        """Selenium WebDriver'ı kur"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Bot detection'ı azaltmak için
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent ayarla
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # WebDriver script'ini gizle
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 10)
        
    def search_business(self, business_name: str, location: str = "") -> bool:
        """
        İşletmeyi ara
        
        Args:
            business_name: İşletme adı
            location: Lokasyon (opsiyonel)
            
        Returns:
            bool: Arama başarılı mı?
        """
        try:
            search_query = f"{business_name} {location}".strip()
            google_maps_url = f"https://www.google.com/maps/search/{search_query}"
            
            print(f"🔍 Aranan: {search_query}")
            self.driver.get(google_maps_url)
            
            # Sayfanın yüklenmesini bekle
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"❌ Arama hatası: {e}")
            return False
    
    def select_first_business(self) -> bool:
        """
        İlk işletmeyi seç
        
        Returns:
            bool: Seçim başarılı mı?
        """
        try:
            # İlk işletme sonucunu bekle ve tıkla
            first_result = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='article'] h3, div.hfpxzc"))
            )
            
            self.driver.execute_script("arguments[0].click();", first_result)
            print("✅ İlk işletme seçildi")
            
            # Detay sayfasının yüklenmesini bekle
            time.sleep(3)
            
            return True
            
        except TimeoutException:
            print("❌ İşletme bulunamadı")
            return False
        except Exception as e:
            print(f"❌ İşletme seçim hatası: {e}")
            return False
    
    def navigate_to_reviews(self) -> bool:
        """
        Yorumlar sekmesine git
        
        Returns:
            bool: Navigasyon başarılı mı?
        """
        try:
            # Reviews tab'ını bekle ve tıkla
            reviews_tab = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[role='tab'][aria-label*='review'], button[data-tab-index='2']"))
            )
            
            self.driver.execute_script("arguments[0].click();", reviews_tab)
            print("✅ Yorumlar sekmesine geçildi")
            
            # Yorumların yüklenmesini bekle
            time.sleep(3)
            
            return True
            
        except TimeoutException:
            print("❌ Yorumlar sekmesi bulunamadı")
            return False
        except Exception as e:
            print(f"❌ Yorumlar sekmesi hatası: {e}")
            return False
    
    def select_newest_reviews(self) -> bool:
        """
        En yeni yorumları seç
        
        Returns:
            bool: Seçim başarılı mı?
        """
        try:
            # "Most relevant" veya sorting dropdown'ını bekle ve tıkla
            sort_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label*='Most relevant'], button[aria-label*='Newest'], .HQzyZ"))
            )
            
            # Eğer zaten "Newest" seçiliyse, tekrar tıklamaya gerek yok
            if "Newest" in sort_button.get_attribute("aria-label"):
                print("✅ Zaten en yeni yorumlar seçili")
                return True
            
            self.driver.execute_script("arguments[0].click();", sort_button)
            time.sleep(1)
            
            # Dropdown menüsünden "Newest" seçeneğini bul ve tıkla
            try:
                newest_option = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Newest') or contains(text(), 'newest')]"))
                )
                self.driver.execute_script("arguments[0].click();", newest_option)
                print("✅ En yeni yorumlar seçildi")
                
                # Yorumların yeniden yüklenmesini bekle
                time.sleep(3)
                
                return True
                
            except TimeoutException:
                print("⚠️ Newest seçeneği bulunamadı, mevcut sıralama ile devam ediliyor")
                return True
                
        except TimeoutException:
            print("⚠️ Sıralama butonu bulunamadı, mevcut sıralama ile devam ediliyor")
            return True
        except Exception as e:
            print(f"❌ Sıralama seçim hatası: {e}")
            return True  # Hata olsa bile devam et
    
    def extract_reviews(self, max_reviews: int = 10) -> List[Review]:
        """
        Yorumları çıkar
        
        Args:
            max_reviews: Maksimum yorum sayısı
            
        Returns:
            List[Review]: Yorum listesi
        """
        reviews = []
        
        try:
            # Yorumları bul
            # HTML analizi sonucu bulunan selector'lar
            review_containers = self.driver.find_elements(By.CSS_SELECTOR, ".jftiEf.fontBodyMedium")
            
            print(f"📝 {len(review_containers)} yorum bulundu")
            
            for i, container in enumerate(review_containers[:max_reviews]):
                try:
                    review = self._extract_single_review(container)
                    if review:
                        reviews.append(review)
                        print(f"✅ Yorum {i+1}: {review.reviewer_name[:20]}...")
                    
                except Exception as e:
                    print(f"⚠️ Yorum {i+1} çıkarılırken hata: {e}")
                    continue
            
            print(f"🎉 Toplam {len(reviews)} yorum başarıyla çıkarıldı")
            
        except Exception as e:
            print(f"❌ Yorum çıkarma hatası: {e}")
        
        return reviews
    
    def _extract_single_review(self, container) -> Optional[Review]:
        """
        Tek bir yorumu çıkar
        
        Args:
            container: Yorum container elementi
            
        Returns:
            Optional[Review]: Yorum objesi
        """
        try:
            # Yorumcu adı
            reviewer_name_elem = container.find_element(By.CSS_SELECTOR, ".d4r55.fontTitleMedium")
            reviewer_name = reviewer_name_elem.text.strip()
            
            # Yorum metni
            review_text_elem = container.find_element(By.CSS_SELECTOR, ".wiI7pd")
            review_text = review_text_elem.text.strip()
            
            # Puan
            rating_elem = container.find_element(By.CSS_SELECTOR, ".fzvQIb")
            rating = rating_elem.text.strip()
            
            # Tarih
            date_elem = container.find_element(By.CSS_SELECTOR, ".xRkPPb")
            date = date_elem.text.strip()
            
            # "New" etiketi var mı?
            is_new = False
            try:
                new_elem = container.find_element(By.CSS_SELECTOR, ".J7sVM.W8gobe")
                is_new = "New" in new_elem.text
            except NoSuchElementException:
                pass
            
            return Review(
                reviewer_name=reviewer_name,
                review_text=review_text,
                rating=rating,
                date=date,
                is_new=is_new
            )
            
        except NoSuchElementException as e:
            print(f"⚠️ Yorum elementi bulunamadı: {e}")
            return None
        except Exception as e:
            print(f"⚠️ Yorum çıkarma hatası: {e}")
            return None
    
    def get_latest_reviews(self, business_name: str, location: str = "", max_reviews: int = 10) -> List[Review]:
        """
        Ana fonksiyon: İşletmenin en son yorumlarını getir
        
        Args:
            business_name: İşletme adı
            location: Lokasyon
            max_reviews: Maksimum yorum sayısı
            
        Returns:
            List[Review]: Yorum listesi
        """
        print(f"\n🚀 {business_name} işletmesi için yorum çıkarma başlıyor...")
        
        # 1. İşletmeyi ara
        if not self.search_business(business_name, location):
            return []
        
        # 2. İlk işletmeyi seç
        if not self.select_first_business():
            return []
        
        # 3. Yorumlar sekmesine git
        if not self.navigate_to_reviews():
            return []
        
        # 4. En yeni yorumları seç
        self.select_newest_reviews()
        
        # 5. Yorumları çıkar
        reviews = self.extract_reviews(max_reviews)
        
        return reviews
    
    def save_to_csv(self, reviews: List[Review], filename: str = "google_maps_reviews.csv"):
        """
        Yorumları CSV'ye kaydet
        
        Args:
            reviews: Yorum listesi
            filename: Dosya adı
        """
        if not reviews:
            print("❌ Kaydedilecek yorum yok")
            return
        
        # DataFrame oluştur
        data = []
        for review in reviews:
            data.append({
                'Yorumcu Adı': review.reviewer_name,
                'Yorum': review.review_text,
                'Puan': review.rating,
                'Tarih': review.date,
                'Yeni Mi': review.is_new,
                'Platform': review.platform
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"💾 {len(reviews)} yorum '{filename}' dosyasına kaydedildi")
    
    def close(self):
        """Tarayıcıyı kapat"""
        if self.driver:
            self.driver.quit()
            print("🔒 Tarayıcı kapatıldı")


# Ana kullanım örneği
if __name__ == "__main__":
    # Scraper'ı başlat
    scraper = GoogleMapsReviewScraper(headless=False)  # Görünür mod
    
    try:
        # İşletme adı ve lokasyon
        business_name = "Maxx Royal Kemer Resort"
        location = "Antalya"
        
        # En son 5 yorumu getir
        reviews = scraper.get_latest_reviews(
            business_name=business_name,
            location=location,
            max_reviews=5
        )
        
        # Sonuçları göster
        print(f"\n📋 {len(reviews)} Yorum Bulundu:")
        print("=" * 80)
        
        for i, review in enumerate(reviews, 1):
            print(f"\n{i}. YORUM:")
            print(f"👤 Yorumcu: {review.reviewer_name}")
            print(f"⭐ Puan: {review.rating}")
            print(f"📅 Tarih: {review.date}")
            print(f"🆕 Yeni: {'Evet' if review.is_new else 'Hayır'}")
            print(f"💬 Yorum: {review.review_text[:200]}...")
            print("-" * 80)
        
        # CSV'ye kaydet
        scraper.save_to_csv(reviews, "latest_reviews.csv")
        
    except KeyboardInterrupt:
        print("\n⚠️ İşlem kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"\n❌ Hata oluştu: {e}")
    finally:
        # Tarayıcıyı kapat
        scraper.close()
