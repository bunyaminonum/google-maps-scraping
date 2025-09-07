from dataclasses import dataclass
from typing import List, Optional
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
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
    """Google Haritalar yorum çıkarıcısı - Firefox Edition"""
    
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
        """Firefox WebDriver'ı kur"""
        firefox_options = Options()
        
        if self.headless:
            firefox_options.add_argument("--headless")
        
        # Bot detection'ı azaltmak için
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")
        
        # User agent ayarla
        firefox_options.set_preference("general.useragent.override", 
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
        
        # Otomasyonu gizle
        firefox_options.set_preference("dom.webdriver.enabled", False)
        firefox_options.set_preference('useAutomationExtension', False)
        
        try:
            service = Service(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=firefox_options)
            print("✅ Firefox başlatıldı")
        except Exception as e:
            print(f"❌ Firefox başlatma hatası: {e}")
            print("🔧 Firefox tarayıcısının kurulu olduğundan emin olun")
            raise
        
        self.wait = WebDriverWait(self.driver, 15)  # Firefox için daha uzun timeout
        
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
            google_maps_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
            
            print(f"🔍 Aranan: {search_query}")
            print(f"🌐 URL: {google_maps_url}")
            
            self.driver.get(google_maps_url)
            
            # Sayfanın yüklenmesini bekle
            print("⏳ Sayfa yükleniyor...")
            time.sleep(5)
            
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
            print("🎯 İlk işletmeyi arıyor...")
            
            # Farklı selector'ları dene
            selectors = [
                "div[role='article'] h3",
                "div.hfpxzc",
                "a[data-result-index='0']",
                ".Nv2PK",
                ".qBF1Pd"
            ]
            
            first_result = None
            for selector in selectors:
                try:
                    first_result = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    print(f"✅ Element bulundu: {selector}")
                    break
                except TimeoutException:
                    print(f"⚠️ Selector çalışmadı: {selector}")
                    continue
            
            if not first_result:
                print("❌ Hiçbir işletme elementi bulunamadı")
                return False
            
            # Scroll to element and click
            self.driver.execute_script("arguments[0].scrollIntoView(true);", first_result)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", first_result)
            print("✅ İlk işletme seçildi")
            
            # Detay sayfasının yüklenmesini bekle
            print("⏳ İşletme detayları yükleniyor...")
            time.sleep(5)
            
            return True
            
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
            print("📝 Yorumlar sekmesini arıyor...")
            
            # Farklı reviews tab selector'ları (Firefox özel)
            selectors = [
                "button[role='tab'][aria-label*='review' i]",
                "button[role='tab'][aria-label*='yorumlar' i]",  # Türkçe
                "button[data-tab-index='2']",  # Yorumlar genelde 3. tab (index 2)
                "button[aria-label*='Reviews' i]",
                ".hh2c6[data-tab-index='2']",
                ".RWPxGd button[data-tab-index='2']",  # Firefox tab yapısı
                "button[aria-label*='ile ilgili yorumlar']"  # Firefox Türkçe
            ]
            
            reviews_tab = None
            for selector in selectors:
                try:
                    if "contains" in selector:
                        # XPath için
                        reviews_tab = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), 'Reviews')]"))
                        )
                    else:
                        reviews_tab = self.wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    print(f"✅ Reviews tab bulundu: {selector}")
                    break
                except TimeoutException:
                    print(f"⚠️ Selector çalışmadı: {selector}")
                    continue
            
            if not reviews_tab:
                print("❌ Yorumlar sekmesi bulunamadı")
                return False
            
            self.driver.execute_script("arguments[0].scrollIntoView(true);", reviews_tab)
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", reviews_tab)
            print("✅ Yorumlar sekmesine geçildi")
            
            # Yorumların yüklenmesini bekle
            print("⏳ Yorumlar yükleniyor...")
            time.sleep(5)
            
            return True
            
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
            print("🔄 Sıralama seçeneklerini arıyor...")
            
            # Sort button selector'ları
            selectors = [
                "button[aria-label*='Most relevant']",
                "button[aria-label*='Newest']", 
                ".HQzyZ",
                "button.g88MCb",
                "[data-sort-id]"
            ]
            
            sort_button = None
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            sort_button = element
                            print(f"✅ Sort button bulundu: {selector}")
                            break
                    if sort_button:
                        break
                except:
                    continue
            
            if not sort_button:
                print("⚠️ Sıralama butonu bulunamadı, mevcut sıralama ile devam ediliyor")
                return True
            
            # Button text kontrol et
            button_text = sort_button.text or sort_button.get_attribute("aria-label") or ""
            if "Newest" in button_text:
                print("✅ Zaten en yeni yorumlar seçili")
                return True
            
            # Sort button'a tıkla
            self.driver.execute_script("arguments[0].click();", sort_button)
            time.sleep(2)
            
            # Dropdown'dan Newest seç
            try:
                newest_option = None
                dropdown_selectors = [
                    "//div[contains(text(), 'Newest')]",
                    "//span[contains(text(), 'Newest')]",
                    "//button[contains(text(), 'Newest')]"
                ]
                
                for xpath in dropdown_selectors:
                    try:
                        newest_option = self.driver.find_element(By.XPATH, xpath)
                        if newest_option.is_displayed():
                            break
                    except:
                        continue
                
                if newest_option:
                    self.driver.execute_script("arguments[0].click();", newest_option)
                    print("✅ En yeni yorumlar seçildi")
                    time.sleep(3)
                else:
                    print("⚠️ Newest seçeneği bulunamadı")
                
            except Exception as dropdown_error:
                print(f"⚠️ Dropdown seçim hatası: {dropdown_error}")
            
            return True
                
        except Exception as e:
            print(f"⚠️ Sıralama seçim hatası: {e}")
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
            print("📋 Yorumları arıyor...")
            
            # Yorumları bul - Firefox için güncellenmiş seçiciler
            review_containers = []
            
            # Firefox için güncellenmiş selectors
            review_selectors = [
                ".jftiEf.fontBodyMedium",  # Chrome seçici
                ".aLPB6c",  # Firefox travel review cards
                ".T65V3d",  # Firefox review content
                "[data-review-id]",  # Review ID attribute
                ".gws-localreviews__google-review",  # Alternative
                ".review-item",  # Generic
                ".TSUbDb",  # Alternative Google Maps
                ".lqU9qb"  # Firefox specific review elements
            ]
            
            for selector in review_selectors:
                try:
                    containers = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if containers:
                        review_containers = containers
                        print(f"✅ Yorumlar bulundu: {selector} ({len(containers)} adet)")
                        break
                except Exception as e:
                    continue
            
            # Eğer hiç yorum bulunamadıysa, tüm sayfayı kontrol et
            if not review_containers:
                # JavaScript ile yorum arayalım
                try:
                    review_containers = self.driver.execute_script("""
                        // Text içerik ile yorum container'larını bul
                        var allDivs = document.querySelectorAll('div');
                        var reviewContainers = [];
                        
                        for (var i = 0; i < allDivs.length; i++) {
                            var div = allDivs[i];
                            var text = div.textContent || '';
                            
                            // Yorum göstergelerini ara
                            if (text.includes('yıldız') || text.includes('star') || 
                                text.includes('önce') || text.includes('ago') ||
                                text.includes('gün') || text.includes('day') ||
                                text.includes('hafta') || text.includes('week')) {
                                
                                // Parent container'ı kontrol et
                                var parent = div.parentElement;
                                if (parent && parent.children.length > 2) {
                                    reviewContainers.push(parent);
                                }
                            }
                        }
                        
                        return Array.from(new Set(reviewContainers));
                    """)
                    
                    if review_containers:
                        print(f"✅ JavaScript ile {len(review_containers)} yorum container'ı bulundu")
                        
                except Exception as js_error:
                    print(f"⚠️ JavaScript arama hatası: {js_error}")
                    review_containers = []
            
            print(f"📝 {len(review_containers)} yorum container'ı bulundu")
            
            if len(review_containers) == 0:
                print("❌ Hiç yorum bulunamadı - sayfa içeriğini kontrol edin")
                self.debug_page_content()
                return []
            
            for i, container in enumerate(review_containers[:max_reviews]):
                try:
                    review = self._extract_single_review(container)
                    if review:
                        reviews.append(review)
                        print(f"✅ Yorum {i+1}: {review.reviewer_name[:30]}...")
                    
                except Exception as e:
                    print(f"⚠️ Yorum {i+1} çıkarılırken hata: {e}")
                    continue
            
            print(f"🎉 Toplam {len(reviews)} yorum başarıyla çıkarıldı")
            
        except Exception as e:
            print(f"❌ Yorum çıkarma hatası: {e}")
        
        return reviews
    
    def debug_page_content(self):
        """Debug için sayfa içeriğini kontrol et"""
        try:
            print("\n🔍 DEBUG: Sayfa içeriği kontrol ediliyor...")
            current_url = self.driver.current_url
            page_title = self.driver.title
            print(f"📍 Mevcut URL: {current_url}")
            print(f"📄 Sayfa başlığı: {page_title}")
            
            # Sayfa üzerindeki elementleri kontrol et
            body_text = self.driver.find_element(By.TAG_NAME, "body").text[:500]
            print(f"📝 Sayfa içeriği (ilk 500 karakter): {body_text}")
            
        except Exception as e:
            print(f"❌ Debug hatası: {e}")
    
    def _extract_single_review(self, container) -> Optional[Review]:
        """
        Tek bir yorumu çıkar - Firefox için optimize edilmiş
        
        Args:
            container: Yorum container elementi
            
        Returns:
            Optional[Review]: Yorum objesi
        """
        try:
            # Yorumcu adı - Firefox yapısına göre
            reviewer_name = "Unknown"
            name_selectors = [
                ".JxYnKd",  # Firefox özel
                ".d4r55.fontTitleMedium", 
                ".reviewer-name", 
                ".author-name",
                ".kK9mfd"  # Firefox alternative
            ]
            for selector in name_selectors:
                try:
                    reviewer_name_elem = container.find_element(By.CSS_SELECTOR, selector)
                    reviewer_name = reviewer_name_elem.text.strip()
                    if reviewer_name:
                        break
                except:
                    continue
            
            # Eğer isim bulunamadıysa, container'ın tüm text içeriğini kontrol et
            if reviewer_name == "Unknown":
                try:
                    container_text = container.text
                    # İlk satırı isim olarak al
                    lines = container_text.split('\n')
                    if lines:
                        reviewer_name = lines[0][:50]  # İlk 50 karakter
                except:
                    pass
            
            # Yorum metni - Firefox yapısına göre
            review_text = "No text"
            text_selectors = [
                ".vKrbfc span",  # Firefox özel yorum text
                ".wiI7pd", 
                ".review-text", 
                ".review-content",
                ".fontBodyMedium"
            ]
            for selector in text_selectors:
                try:
                    review_text_elem = container.find_element(By.CSS_SELECTOR, selector)
                    review_text = review_text_elem.text.strip()
                    if review_text and len(review_text) > 10:  # Anlamlı bir metin olsun
                        break
                except:
                    continue
            
            # Eğer metin bulunamadıysa, container'dan çıkar
            if review_text == "No text":
                try:
                    full_text = container.text
                    # Uzun satırları yorum metni olarak değerlendir
                    lines = full_text.split('\n')
                    for line in lines:
                        if len(line) > 20:  # 20 karakterden uzun satırlar
                            review_text = line
                            break
                except:
                    pass
            
            # Puan - Firefox yapısına göre
            rating = "No rating"
            rating_selectors = [
                "[aria-label*='yıldız']",
                "[aria-label*='star']", 
                ".fzvQIb",
                ".rating-value",
                ".star-rating"
            ]
            
            for selector in rating_selectors:
                try:
                    rating_elem = container.find_element(By.CSS_SELECTOR, selector)
                    rating_text = rating_elem.get_attribute("aria-label") or rating_elem.text
                    if rating_text:
                        # "5/5" veya "5 yıldız" gibi formatlardan sayıyı çıkar
                        import re
                        numbers = re.findall(r'(\d+[.,]?\d*)', rating_text)
                        if numbers:
                            rating = numbers[0]
                            break
                except:
                    continue
            
            # Tarih - Firefox yapısına göre  
            date = "Unknown date"
            date_selectors = [
                ".DtSNhc",  # Firefox özel
                ".xRkPPb", 
                ".review-date", 
                ".relative-time"
            ]
            
            for selector in date_selectors:
                try:
                    date_elem = container.find_element(By.CSS_SELECTOR, selector)
                    date = date_elem.text.strip()
                    if date:
                        break
                except:
                    continue
            
            # Tarih bulunamadıysa container text'inden çıkarmaya çalış
            if date == "Unknown date":
                try:
                    text = container.text
                    # "X gün önce", "X hafta önce" gibi pattern'leri ara
                    import re
                    date_patterns = [
                        r'(\d+\s+gün\s+önce)',
                        r'(\d+\s+hafta\s+önce)', 
                        r'(\d+\s+ay\s+önce)',
                        r'(\d+\s+days?\s+ago)',
                        r'(\d+\s+weeks?\s+ago)',
                        r'(\d+\s+months?\s+ago)'
                    ]
                    
                    for pattern in date_patterns:
                        match = re.search(pattern, text)
                        if match:
                            date = match.group(1)
                            break
                except:
                    pass
            
            # Review objesi oluştur
            if reviewer_name != "Unknown" or review_text != "No text":
                return Review(
                    reviewer_name=reviewer_name,
                    review_text=review_text,
                    rating=rating,
                    date=date,
                    is_new=False,
                    platform="Google Maps (Firefox)"
                )
            
            return None
            
        except Exception as e:
            print(f"⚠️ Tek yorum çıkarma hatası: {e}")
            return None
            rating_selectors = [".fzvQIb", ".rating", ".stars"]
            for selector in rating_selectors:
                try:
                    rating_elem = container.find_element(By.CSS_SELECTOR, selector)
                    rating = rating_elem.text.strip()
                    if rating:
                        break
                except:
                    continue
            
            # Tarih
            date = "No date"
            date_selectors = [".xRkPPb", ".date", ".review-date"]
            for selector in date_selectors:
                try:
                    date_elem = container.find_element(By.CSS_SELECTOR, selector)
                    date = date_elem.text.strip()
                    if date:
                        break
                except:
                    continue
            
            # "New" etiketi var mı?
            is_new = False
            try:
                new_elem = container.find_element(By.CSS_SELECTOR, ".J7sVM.W8gobe")
                is_new = "New" in new_elem.text
            except:
                pass
            
            # En azından isim ve yorum varsa kabul et
            if reviewer_name != "Unknown" and review_text != "No text":
                return Review(
                    reviewer_name=reviewer_name,
                    review_text=review_text,
                    rating=rating,
                    date=date,
                    is_new=is_new
                )
            else:
                print(f"⚠️ Eksik veri: name='{reviewer_name}', text='{review_text[:50]}'")
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
        print(f"🦊 Firefox WebDriver kullanılıyor")
        
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
            print("🔒 Firefox kapatıldı")


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
