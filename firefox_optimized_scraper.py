"""
Firefox Test Sonuçlarına Göre Optimize Edilmiş Google Maps Review Scraper
Test sonucunda çalışan selector'lar kullanılmıştır
"""

import time
import re
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

@dataclass
class Review:
    reviewer_name: str
    review_text: str
    rating: str
    date: str
    is_new: bool = False
    platform: str = "Google Maps"

class FirefoxGoogleMapsReviewScraper:
    """Firefox için optimize edilmiş Google Maps Review Scraper"""
    
    def __init__(self, headless: bool = False):
        self.driver = None
        self.headless = headless
        self.wait = None
    
    def setup_driver(self):
        """Firefox WebDriver'ı kurar"""
        print("🦊 Firefox WebDriver kuruluyor...")
        
        firefox_options = Options()
        
        if self.headless:
            firefox_options.add_argument("--headless")
            
        firefox_options.add_argument("--width=1920")
        firefox_options.add_argument("--height=1080")
        firefox_options.set_preference("general.useragent.override", 
                                     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
        
        service = Service(GeckoDriverManager().install())
        self.driver = webdriver.Firefox(service=service, options=firefox_options)
        self.wait = WebDriverWait(self.driver, 10)
        
        print("✅ Firefox başlatıldı")
    
    def search_business(self, business_name: str, location: str = "") -> bool:
        """İşletmeyi Google Maps'te arar"""
        print(f"🔍 Aranıyor: {business_name} {location}")
        
        try:
            # Google Maps'e git
            self.driver.get("https://www.google.com/maps")
            time.sleep(3)
            
            # Arama kutusunu bul ve ara
            search_box = self.wait.until(
                EC.presence_of_element_located((By.ID, "searchboxinput"))
            )
            
            search_query = f"{business_name} {location}".strip()
            search_box.clear()
            search_box.send_keys(search_query)
            
            # Arama butonuna tıkla
            search_button = self.driver.find_element(By.ID, "searchbox-searchbutton")
            search_button.click()
            
            print("🔍 Arama yapıldı, sonuçlar bekleniyor...")
            time.sleep(5)
            
            return True
            
        except Exception as e:
            print(f"❌ Arama hatası: {e}")
            return False
    
    def navigate_to_business_url(self, google_maps_url: str) -> bool:
        """
        Direkt Google Maps URL'sine gider - YENİ ÖZELLİK!
        
        Args:
            google_maps_url: İşletmenin Google Maps URL'si
            
        Returns:
            bool: Başarılı ise True
        """
        print(f"🔗 Direkt URL'ye gidiliyor: {google_maps_url[:50]}...")
        
        try:
            # Direkt işletme sayfasına git
            self.driver.get(google_maps_url)
            print("✅ İşletme sayfasına gidildi")
            time.sleep(5)  # Sayfa yüklenmesini bekle
            
            return True
            
        except Exception as e:
            print(f"❌ URL navigasyon hatası: {e}")
            return False
    
    def click_first_result(self) -> bool:
        """İlk arama sonucuna tıklar"""
        print("🎯 İlk sonuca tıklanıyor...")
        
        try:
            # JavaScript ile ilk sonuca tıkla
            try:
                results_area = self.driver.find_element(By.CSS_SELECTOR, "[role='main']")
                self.driver.execute_script("arguments[0].children[0].click();", results_area)
                print("✅ JavaScript ile tıklandı")
                time.sleep(3)
                return True
            except:
                pass
                
            print("❌ İlk sonuca tıklanamadı")
            return False
            
        except Exception as e:
            print(f"❌ Tıklama hatası: {e}")
            return False
    
    def navigate_to_reviews(self) -> bool:
        """Yorumlar sekmesine gider - Test sonuçlarına göre optimize edilmiş"""
        print("📝 Yorumlar sekmesine gidiliyor...")
        
        try:
            # Test'te çalışan selector kullanılıyor
            review_tab_selector = "button[role='tab'][aria-label*='yorumlar' i]"
            
            try:
                element = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, review_tab_selector))
                )
                element.click()
                print(f"✅ Yorumlar tab'ı tıklandı: {review_tab_selector}")
                time.sleep(3)
                return True
            except:
                pass
            
            # Alternatif: JavaScript ile tüm button'ları tara
            try:
                success = self.driver.execute_script("""
                    const buttons = document.querySelectorAll('button');
                    for (let button of buttons) {
                        const text = button.textContent || '';
                        const ariaLabel = button.getAttribute('aria-label') || '';
                        
                        if (text.toLowerCase().includes('yorumlar') || 
                            text.toLowerCase().includes('reviews') ||
                            ariaLabel.toLowerCase().includes('yorumlar') ||
                            ariaLabel.toLowerCase().includes('reviews')) {
                            button.click();
                            return true;
                        }
                    }
                    return false;
                """)
                
                if success:
                    print("✅ JavaScript ile yorumlar tab'ı bulundu ve tıklandı")
                    time.sleep(3)
                    return True
            except:
                pass
            
            print("❌ Yorumlar sekmesi bulunamadı")
            return False
            
        except Exception as e:
            print(f"❌ Yorumlar sekmesi hatası: {e}")
            return False
    
    def select_newest_reviews(self) -> bool:
        """
        En yeni yorumları seçer - HTML analizi sonrası optimize edilmiş
        HTML'de zaten "En yeni" seçili olup olmadığını kontrol eder
        """
        print("🔄 En yeni yorumlar durumu kontrol ediliyor...")
        
        try:
            # Önce mevcut dropdown durumunu kontrol et
            time.sleep(2)  # Sayfanın tam yüklenmesini bekle
            
            # HTML'de gözlenen dropdown button'ı bul
            dropdown_button = None
            dropdown_selectors = [
                "button.HQzyZ",  # CSS class from HTML
                "button[aria-label*='En yeni']",  # Eğer zaten "En yeni" seçiliyse
                "button[aria-label*='En alakalı']",  # Eğer hala "En alakalı" ise
                ".m6QErb button[aria-expanded]"  # Generic dropdown button
            ]
            
            for selector in dropdown_selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if buttons:
                        dropdown_button = buttons[0]
                        aria_label = dropdown_button.get_attribute("aria-label") or ""
                        text_content = dropdown_button.text.strip()
                        
                        print(f"📋 Dropdown durumu: '{text_content}' (aria-label: '{aria_label}')")
                        
                        # Eğer zaten "En yeni" seçiliyse, işlem tamamlandı
                        if "En yeni" in text_content or "En yeni" in aria_label:
                            print("✅ Zaten 'En yeni' seçili durumda!")
                            return True
                        
                        # Eğer "En alakalı" seçiliyse, değiştir
                        if "En alakalı" in text_content or "En alakalı" in aria_label:
                            print("🔄 'En alakalı'dan 'En yeni'ye geçiliyor...")
                            break
                            
                except Exception as e:
                    continue
            
            # Eğer dropdown button bulunamadıysa
            if not dropdown_button:
                print("⚠️ Dropdown button bulunamadı, JavaScript ile aranıyor...")
                
                # JavaScript ile dropdown'ı ara
                try:
                    button_info = self.driver.execute_script("""
                        const buttons = document.querySelectorAll('button');
                        for (let button of buttons) {
                            const ariaLabel = button.getAttribute('aria-label') || '';
                            const text = button.textContent.trim() || '';
                            
                            if (text.includes('En yeni') || ariaLabel.includes('En yeni')) {
                                return {found: true, status: 'already_newest', text: text, ariaLabel: ariaLabel};
                            }
                            
                            if (text.includes('En alakalı') || ariaLabel.includes('En alakalı')) {
                                return {found: true, status: 'need_change', text: text, ariaLabel: ariaLabel, element: button};
                            }
                        }
                        return {found: false};
                    """)
                    
                    if button_info['found']:
                        if button_info['status'] == 'already_newest':
                            print("✅ JavaScript kontrolü: Zaten 'En yeni' seçili!")
                            return True
                        elif button_info['status'] == 'need_change':
                            print("🔄 JavaScript kontrolü: 'En alakalı'dan değiştiriliyor...")
                            # Button element'ini al ve tıkla
                            self.driver.execute_script("""
                                const buttons = document.querySelectorAll('button');
                                for (let button of buttons) {
                                    const text = button.textContent.trim() || '';
                                    const ariaLabel = button.getAttribute('aria-label') || '';
                                    if (text.includes('En alakalı') || ariaLabel.includes('En alakalı')) {
                                        button.click();
                                        return;
                                    }
                                }
                            """)
                            time.sleep(2)
                        else:
                            print("❌ Dropdown durumu belirsiz")
                            return False
                    else:
                        print("❌ JavaScript ile de dropdown bulunamadı")
                        return False
                        
                except Exception as js_error:
                    print(f"❌ JavaScript dropdown hatası: {js_error}")
                    return False
            
            else:
                # Dropdown button bulundu ve "En alakalı" durumunda, tıkla
                try:
                    self.driver.execute_script("arguments[0].click();", dropdown_button)
                    time.sleep(2)
                    print("✅ Dropdown açıldı")
                except Exception as click_error:
                    print(f"❌ Dropdown tıklama hatası: {click_error}")
                    return False
            
            # Şimdi "En yeni" seçeneğini bul ve tıkla
            print("🎯 'En yeni' seçeneği aranıyor...")
            
            # JavaScript ile "En yeni" seçeneğini bul ve tıkla
            try:
                success = self.driver.execute_script("""
                    // Kısa bir süre bekle dropdown'ın açılması için
                    setTimeout(function() {
                        const allElements = document.querySelectorAll('*');
                        for (let element of allElements) {
                            const text = element.textContent.trim();
                            const ariaLabel = element.getAttribute('aria-label') || '';
                            
                            if ((text === 'En yeni' || ariaLabel.includes('En yeni')) && 
                                (element.tagName === 'BUTTON' || element.tagName === 'DIV' || element.click)) {
                                element.click();
                                return true;
                            }
                        }
                        return false;
                    }, 500);
                    return true; // İlk return success indicator
                """)
                
                time.sleep(3)  # "En yeni" seçiminin etkili olması için bekle
                
                # Son kontrol: gerçekten "En yeni" seçildi mi?
                final_check = self.driver.execute_script("""
                    const buttons = document.querySelectorAll('button');
                    for (let button of buttons) {
                        const text = button.textContent.trim();
                        const ariaLabel = button.getAttribute('aria-label') || '';
                        if (text.includes('En yeni') || ariaLabel.includes('En yeni')) {
                            return true;
                        }
                    }
                    return false;
                """)
                
                if final_check:
                    print("✅ 'En yeni' başarıyla seçildi!")
                    return True
                else:
                    print("⚠️ 'En yeni' seçimi doğrulanamadı, ama devam ediliyor...")
                    return True  # Devam et, belki zaten seçilmiştir
                    
            except Exception as newest_error:
                print(f"❌ 'En yeni' seçim hatası: {newest_error}")
                return True  # Hata olsa da devam et
                
        except Exception as e:
            print(f"❌ Dropdown seçim genel hatası: {e}")
            return True  # Hata olsa da scraping'e devam et

    def extract_reviews(self, max_reviews: int = 20) -> List[Review]:
        """
        Yorumları çıkar - Test sonuçlarına göre optimize edilmiş
        TEST SONUÇLARI:
        - .jftiEf.fontBodyMedium: 10 element ✅
        - [data-review-id]: 98 element ✅
        - .wiI7pd: 10 element (yorum metni) ✅
        - .d4r55.fontTitleMedium: 10 element (yorumcu adı) ✅
        """
        print(f"📝 Yorumlar çıkarılıyor... (Hedef: {max_reviews})")
        reviews = []
        
        try:
            # Gelişmiş scroll stratejisi - daha fazla yorum yüklemek için
            print("📜 Daha fazla yorum yüklemek için akıllı scroll yapılıyor...")
            self._smart_scroll_for_reviews(max_reviews)
            
            # HTML analizine göre gerçek yorum container'larını seç
            # Sadece full review data'ya sahip container'ları al
            main_containers = self.driver.find_elements(By.CSS_SELECTOR, ".jftiEf.fontBodyMedium[data-review-id][aria-label]")
            
            print(f"🎯 {len(main_containers)} ana yorum container'ı bulundu")
            
            if not main_containers:
                print("⚠️ Ana container'lar bulunamadı, alternatif selector deneniyor...")
                # Fallback: daha geniş selector
                main_containers = self.driver.find_elements(By.CSS_SELECTOR, "[data-review-id]")
                print(f"🔄 Fallback ile {len(main_containers)} container bulundu")
            
            containers = main_containers
            
            if not containers:
                print("❌ Hiç yorum container'ı bulunamadı!")
                return []
            
            # Her container'dan yorum çıkar - duplicate detection ile
            seen_reviews = set()  # (reviewer_name, review_text) tuple'ları için
            
            for i, container in enumerate(containers[:max_reviews]):
                try:
                    print(f"\n📋 Yorum {i+1}/{min(max_reviews, len(containers))} işleniyor...")
                    
                    review = self._extract_single_review(container)
                    
                    if review:
                        # Duplicate kontrolü
                        review_signature = (review.reviewer_name, review.review_text[:50])
                        
                        if review_signature in seen_reviews:
                            print(f"⚠️ Duplicate yorum atlandı: {review.reviewer_name}")
                            continue
                            
                        seen_reviews.add(review_signature)
                        reviews.append(review)
                        print(f"✅ Yorum eklendi: {review.reviewer_name[:20]}...")
                    else:
                        print(f"⚠️ Yorum {i+1} çıkarılamadı")
                        
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    print(f"❌ Container {i+1} işleme hatası: {e}")
                    continue
            
            print(f"\n🎉 Toplam {len(reviews)} yorum başarıyla çıkarıldı!")
            return reviews
            
        except Exception as e:
            print(f"❌ Yorum çıkarma genel hatası: {e}")
            return reviews
    
    def extract_reviews_with_stats(self, text_reviews_count: int = 15, rating_reviews_count: int = 30):
        """
        Hem metin yorumları hem de tüm puanlamaları çıkarır ve istatistik hesaplar
        
        Args:
            text_reviews_count: Sadece metin içeren yorum sayısı
            rating_reviews_count: Toplam puanlama sayısı (istatistik için)
            
        Returns:
            {
                'text_reviews': List[Review],  # Sadece metin içeren yorumlar
                'all_ratings': List[dict],     # Tüm puanlamalar
                'statistics': dict             # İstatistiksel veriler
            }
        """
        print(f"📊 Akıllı veri toplama başlıyor...")
        print(f"🎯 Hedef: {text_reviews_count} metin yorumu + {rating_reviews_count} puanlama")
        
        # Maksimum container sayısını hesapla (biraz daha fazla yükleyelim)
        max_containers_needed = max(text_reviews_count * 2, rating_reviews_count + 10)
        
        try:
            # 1. Scroll ile yeterli container yükle
            print("📜 Yeterli veri yüklemek için akıllı scroll...")
            self._smart_scroll_for_reviews(max_containers_needed)
            
            # 2. Tüm container'ları al
            all_containers = self.driver.find_elements(By.CSS_SELECTOR, ".jftiEf.fontBodyMedium[data-review-id][aria-label]")
            print(f"🎯 {len(all_containers)} toplam yorum container'ı bulundu")
            
            if not all_containers:
                print("❌ Hiç yorum container'ı bulunamadı!")
                return {'text_reviews': [], 'all_ratings': [], 'statistics': {}}
            
            # 3. Verileri kategorize et
            text_reviews = []       # Sadece metin içeren yorumlar
            all_ratings = []        # Tüm puanlamalar (istatistik için)
            
            for i, container in enumerate(all_containers):
                try:
                    print(f"\n📋 Container {i+1}/{len(all_containers)} işleniyor...")
                    
                    # Temel verileri çıkar
                    review_data = self._extract_basic_review_data(container)
                    if not review_data:
                        continue
                    
                    # Puanlama her zaman ekle (istatistik için)
                    if review_data['rating'] and review_data['rating'] != "No rating":
                        rating_entry = {
                            'rating': int(review_data['rating']) if review_data['rating'].isdigit() else None,
                            'date': review_data['date'],
                            'reviewer_name': review_data['reviewer_name']
                        }
                        all_ratings.append(rating_entry)
                        print(f"   📈 Puanlama eklendi: {review_data['rating']} yıldız")
                    
                    # Metin yorumu varsa text_reviews'a ekle
                    if (review_data['review_text'] and 
                        review_data['review_text'] != "No text" and 
                        len(review_data['review_text']) > 15):
                        
                        review = Review(
                            reviewer_name=review_data['reviewer_name'],
                            review_text=review_data['review_text'],
                            rating=review_data['rating'],
                            date=review_data['date'],
                            is_new=self._is_recent_review(review_data['date']),
                            platform="Google Maps (Firefox)"
                        )
                        text_reviews.append(review)
                        print(f"   ✅ Metin yorumu eklendi: {review_data['reviewer_name'][:20]}...")
                    
                    # Hedeflere ulaştık mı kontrol et
                    if (len(text_reviews) >= text_reviews_count and 
                        len(all_ratings) >= rating_reviews_count):
                        print(f"🎯 Her iki hedefe de ulaşıldı!")
                        break
                        
                except Exception as e:
                    print(f"❌ Container {i+1} işleme hatası: {e}")
                    continue
            
            # 4. İstatistikleri hesapla
            statistics = self._calculate_statistics(all_ratings, text_reviews)
            
            # 5. Hedeflere göre kırp
            final_text_reviews = text_reviews[:text_reviews_count]
            final_ratings = all_ratings[:rating_reviews_count]
            
            print(f"\n🎉 Veri toplama tamamlandı!")
            print(f"📝 Metin yorumları: {len(final_text_reviews)}")
            print(f"📊 Toplam puanlama: {len(final_ratings)}")
            
            return {
                'text_reviews': final_text_reviews,
                'all_ratings': final_ratings,
                'statistics': statistics
            }
            
        except Exception as e:
            print(f"❌ Akıllı veri toplama hatası: {e}")
            return {'text_reviews': [], 'all_ratings': [], 'statistics': {}}
    
    def _extract_basic_review_data(self, container):
        """
        Container'dan temel veri çıkarır (Review objesi oluşturmadan)
        """
        try:
            # İsim çıkar
            name_elements = container.find_elements(By.CSS_SELECTOR, ".d4r55.fontTitleMedium")
            reviewer_name = name_elements[0].text.strip() if name_elements else "Unknown"
            
            # Metin çıkar
            text_elements = container.find_elements(By.CSS_SELECTOR, ".wiI7pd")
            review_text = text_elements[0].text.strip() if text_elements else "No text"
            
            # Rating çıkar
            rating_elements = container.find_elements(By.CSS_SELECTOR, ".kvMYJc")
            rating = "No rating"
            if rating_elements:
                aria_label = rating_elements[0].get_attribute("aria-label")
                if aria_label:
                    rating_match = re.search(r'(\d+)', aria_label)
                    if rating_match:
                        rating = rating_match.group(1)
            
            # Tarih çıkar
            date = self._extract_date_from_container(container)
            
            return {
                'reviewer_name': reviewer_name,
                'review_text': review_text,
                'rating': rating,
                'date': date
            }
            
        except Exception as e:
            print(f"   ❌ Temel veri çıkarma hatası: {e}")
            return None
    
    def _calculate_statistics(self, all_ratings: list, text_reviews: list) -> dict:
        """
        İstatistikleri hesaplar
        """
        try:
            stats = {}
            
            # Puanlama istatistikleri
            if all_ratings:
                valid_ratings = [r['rating'] for r in all_ratings if r['rating'] is not None]
                if valid_ratings:
                    stats['rating_average'] = sum(valid_ratings) / len(valid_ratings)
                    stats['rating_count'] = len(valid_ratings)
                    stats['rating_distribution'] = {
                        str(i): valid_ratings.count(i) for i in range(1, 6)
                    }
                else:
                    stats['rating_average'] = 0
                    stats['rating_count'] = 0
                    stats['rating_distribution'] = {}
            
            # Metin yorumu istatistikleri
            stats['text_review_count'] = len(text_reviews)
            stats['text_review_percentage'] = (len(text_reviews) / len(all_ratings) * 100) if all_ratings else 0
            
            # Son güncellemeler
            if text_reviews:
                recent_count = sum(1 for r in text_reviews if r.is_new)
                stats['recent_reviews_count'] = recent_count
                stats['recent_reviews_percentage'] = (recent_count / len(text_reviews) * 100)
            
            return stats
            
        except Exception as e:
            print(f"❌ İstatistik hesaplama hatası: {e}")
            return {}
    
    def display_results_with_stats(self, data):
        """
        Sonuçları istatistiklerle birlikte gösterir
        """
        reviews = data['text_reviews']
        stats = data['statistics']
        
        print(f"\n📊 İSTATİSTİKLER:")
        print("=" * 50)
        
        if 'rating_average' in stats:
            print(f"⭐ Ortalama Puan: {stats['rating_average']:.1f}/5")
            print(f"📈 Toplam Puanlama: {stats['rating_count']}")
            print(f"📝 Metin Yorumu: {stats['text_review_count']} (%{stats['text_review_percentage']:.1f})")
            
            if 'recent_reviews_count' in stats:
                print(f"🆕 Son Yorumlar: {stats['recent_reviews_count']} (%{stats['recent_reviews_percentage']:.1f})")
        
        print(f"\n📊 İLK 5 YORUM:")
        print("=" * 80)
        
        for i, review in enumerate(reviews[:5], 1):
            print(f"\n{i}. YORUM:")
            print(f"👤 Yorumcu: {review.reviewer_name}")
            print(f"⭐ Puan: {review.rating}")
            print(f"📅 Tarih: {review.date}")
            print(f"💬 Yorum: {review.review_text[:100]}{'...' if len(review.review_text) > 100 else ''}")
            print("-" * 80)
    
    def _extract_date_from_container(self, container):
        """
        Container'dan tarih çıkarır
        """
        try:
            # Önce .rsqaWe class'ını bul
            date_elements = container.find_elements(By.CSS_SELECTOR, ".rsqaWe")
            if date_elements:
                return date_elements[0].text.strip()
            
            # Alternatif: container text'inden tarih arama
            container_text = container.text
            date_patterns = [
                r'(\d+\s+dakika\s+önce)',
                r'(\d+\s+saat\s+önce)',
                r'(\d+\s+gün\s+önce)',
                r'(\d+\s+hafta\s+önce)', 
                r'(\d+\s+ay\s+önce)',
                r'(\d+\s+yıl\s+önce)',
                r'(bir\s+saat\s+önce)',
                r'(bir\s+gün\s+önce)',
                r'(düzenlendi)',
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, container_text, re.IGNORECASE)
                if match:
                    lines = container_text.split('\n')
                    for line in lines:
                        if 'önce' in line or 'ago' in line or 'düzenlendi' in line:
                            return line.strip()
            
            return "Unknown date"
            
        except Exception as e:
            print(f"   ❌ Tarih çıkarma hatası: {e}")
            return "Unknown date"
            if valid_name and (valid_text or valid_rating):
                return Review(
                    reviewer_name=reviewer_name,
                    review_text=review_text,
                    rating=rating,
                    date=date,
                    is_new=is_recent,  # En yeni mi kontrol et
                    platform="Google Maps (Firefox)"
                )
            else:
                print(f"   ❌ Geçersiz veri: name={valid_name}, text={valid_text}, rating={valid_rating}")
                return None
            
        except Exception as e:
            print(f"⚠️ Tek yorum çıkarma hatası: {e}")
            return None
    
    def _smart_scroll_for_reviews(self, target_reviews: int = 20):
        """
        Google Maps için gerçek yorumlar scroll fonksiyonu
        HTML analizi sonucunda: yorumlar .m6QErb.XiKgde container'ında
        """
        print(f"🎯 Google Maps yorumları için gerçek scroll başlıyor (hedef: {target_reviews})")
        
        # ADIM 1: Gerçek scrollable container'ı bul
        scrollable_container = None
        container_attempts = [
            # Google Maps yorumların ana scroll container'ı
            ".m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde",
            ".m6QErb.XiKgde", 
            # Panel level container
            "[role='main']",
            "#pane",
            # Fallback
            "body"
        ]
        
        for selector in container_attempts:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    element = elements[0]
                    # Scroll edilebilir mi kontrol et
                    is_scrollable = self.driver.execute_script("""
                        var elem = arguments[0];
                        return elem.scrollHeight > elem.clientHeight || 
                               getComputedStyle(elem).overflowY === 'scroll' ||
                               getComputedStyle(elem).overflowY === 'auto';
                    """, element)
                    
                    if is_scrollable or selector == "body":
                        scrollable_container = element
                        print(f"✅ Scrollable container bulundu: {selector}")
                        break
            except Exception as e:
                print(f"⚠️ Container arama hatası {selector}: {e}")
                continue
                
        if not scrollable_container:
            print("❌ Hiç scroll container bulunamadı!")
            return 0
            
        # ADIM 2: Smart scroll döngüsü
        previous_count = 0
        stable_count = 0
        max_stable = 3
        scroll_attempt = 0
        max_attempts = 15
        
        while scroll_attempt < max_attempts and stable_count < max_stable:
            # Mevcut yorum sayısını say
            reviews = self.driver.find_elements(By.CSS_SELECTOR, ".jftiEf.fontBodyMedium[data-review-id]")
            current_count = len(reviews)
            
            print(f"📊 Scroll {scroll_attempt + 1}: {current_count} yorum (hedef: {target_reviews})")
            
            # Hedef sayıya ulaştık mı?
            if current_count >= target_reviews:
                print(f"✅ Hedef ulaşıldı: {current_count} yorum")
                break
                
            # Yeni yorum geldi mi?
            if current_count == previous_count:
                stable_count += 1
                print(f"   ⏳ Sabit kalma: {stable_count}/{max_stable}")
            else:
                stable_count = 0
                new_reviews = current_count - previous_count
                print(f"   ➕ {new_reviews} yeni yorum yüklendi")
                
            previous_count = current_count
            
            # ADIM 3: Farklı scroll teknikleri uygula
            try:
                scroll_technique = scroll_attempt % 5
                
                if scroll_technique == 0:
                    # Direkt container scroll
                    print("   🎯 Container scroll (direkt)")
                    self.driver.execute_script("""
                        var container = arguments[0];
                        container.scrollTop = container.scrollHeight;
                    """, scrollable_container)
                    
                elif scroll_technique == 1:
                    # Son görünen yoruma scroll
                    if reviews:
                        last_review = reviews[-1]
                        print("   ⬇️ Son yoruma scroll")
                        self.driver.execute_script("""
                            arguments[0].scrollIntoView({
                                behavior: 'smooth',
                                block: 'end'
                            });
                        """, last_review)
                    
                elif scroll_technique == 2:
                    # Container içinde kademeli scroll
                    print("   📜 Kademeli scroll")
                    self.driver.execute_script("""
                        var container = arguments[0];
                        var currentScroll = container.scrollTop;
                        container.scrollTop = currentScroll + (window.innerHeight * 0.8);
                    """, scrollable_container)
                    
                elif scroll_technique == 3:
                    # Mouse wheel simülasyonu
                    print("   🖱️ Mouse wheel scroll")
                    if reviews:
                        middle_review = reviews[min(len(reviews)//2, len(reviews)-1)]
                        middle_review.click()
                        middle_review.send_keys(Keys.PAGE_DOWN)
                        
                else:
                    # Kombinasyon: container + page scroll
                    print("   🔄 Kombinasyon scroll")
                    self.driver.execute_script("""
                        var container = arguments[0];
                        // Container scroll
                        container.scrollTop += window.innerHeight;
                        // Page scroll de dene
                        setTimeout(function() {
                            window.scrollBy(0, 400);
                        }, 200);
                    """, scrollable_container)
                
                # Scroll sonrası bekleme
                scroll_wait = 2.5 if scroll_attempt < 5 else 3.5
                time.sleep(scroll_wait)
                scroll_attempt += 1
                
            except Exception as scroll_error:
                print(f"   ❌ Scroll hatası: {scroll_error}")
                # Basit fallback
                try:
                    self.driver.execute_script("window.scrollBy(0, 1000);")
                    time.sleep(2)
                except:
                    pass
                scroll_attempt += 1
        
        # ADIM 4: Final kontrol
        final_reviews = self.driver.find_elements(By.CSS_SELECTOR, ".jftiEf.fontBodyMedium[data-review-id]")
        final_count = len(final_reviews)
        
        print(f"🏁 Scroll tamamlandı!")
        print(f"   📈 Toplam yorum: {final_count}")
        print(f"   🔢 Hedef: {target_reviews}")
        print(f"   ✨ Başarı oranı: %{(min(final_count, target_reviews) / target_reviews * 100):.1f}")
        
        return final_count
    
    def _is_recent_review(self, date: str) -> bool:
        """
        Yorumun yakın zamanda yazılıp yazılmadığını kontrol eder
        
        Args:
            date: Tarih string'i (örn: "3 gün önce", "2 hafta önce")
            
        Returns:
            bool: Son 1 ay içinde yazılmışsa True
        """
        try:
            if not date or date == "Unknown date":
                return False
            
            date_lower = date.lower()
            
            # Günlük kontrolü (son 30 gün)
            if 'gün önce' in date_lower or 'days ago' in date_lower:
                import re
                numbers = re.findall(r'(\d+)', date_lower)
                if numbers:
                    days = int(numbers[0])
                    return days <= 30  # Son 30 gün
            
            # Haftalık kontrolü (son 4 hafta)
            elif 'hafta önce' in date_lower or 'weeks ago' in date_lower:
                import re
                numbers = re.findall(r'(\d+)', date_lower)
                if numbers:
                    weeks = int(numbers[0])
                    return weeks <= 4  # Son 4 hafta
            
            # "1 ay önce" kontrolü
            elif 'ay önce' in date_lower or 'month ago' in date_lower:
                import re
                numbers = re.findall(r'(\d+)', date_lower)
                if numbers:
                    months = int(numbers[0])
                    return months <= 1  # Son 1 ay
            
            return False
            
        except:
            return False
    
    def save_to_csv(self, reviews: List[Review], business_name: str) -> str:
        """Yorumları CSV'ye kaydet"""
        if not reviews:
            print("❌ Kaydedilecek yorum yok")
            return ""
        
        # Dosya adı oluştur
        import re
        clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', business_name)
        clean_name = clean_name.replace(' ', '_')
        filename = f"google_maps_reviews_{clean_name}.csv"
        
        # DataFrame oluştur
        data = []
        for review in reviews:
            data.append({
                'Yorumcu_Adi': review.reviewer_name,
                'Yorum_Metni': review.review_text,
                'Puan': review.rating,
                'Tarih': review.date,
                'Platform': review.platform
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"💾 {len(reviews)} yorum '{filename}' dosyasına kaydedildi")
        
        return filename
    
    def display_results(self, reviews: List[Review]):
        """Sonuçları göster - En yeni yorumları vurgula"""
        if not reviews:
            print("📋 Gösterilecek yorum yok")
            return
        
        # En yeni yorumları say
        recent_reviews = [r for r in reviews if r.is_new]
        
        print(f"\n📊 İLK {len(reviews)} YORUM:")
        if recent_reviews:
            print(f"🆕 Bunlardan {len(recent_reviews)} tanesi son 1 ay içinde yazılmış!")
        print("=" * 80)
        
        for i, review in enumerate(reviews, 1):
            print(f"\n{i}. YORUM:")
            if review.is_new:
                print(f"👤 Yorumcu: {review.reviewer_name} 🆕")
            else:
                print(f"👤 Yorumcu: {review.reviewer_name}")
            print(f"⭐ Puan: {review.rating}")
            print(f"📅 Tarih: {review.date}")
            print(f"💬 Yorum: {review.review_text}")
            print("-" * 80)
    
    def cleanup(self):
        """Tarayıcıyı kapat"""
        if self.driver:
            self.driver.quit()
            print("🔒 Firefox kapatıldı")
    
    def scrape_reviews(self, business_name: str, location: str = "", 
                      text_reviews_count: int = 15, rating_reviews_count: int = 30, 
                      google_maps_url: str = None):
        """
        Ana fonksiyon - hem metin içeren yorumları hem de tüm puanlamaları toplar
        
        Args:
            business_name: İşletme adı  
            location: Konum (URL verilmemişse kullanılır)
            text_reviews_count: Sadece metin içeren yorum sayısı (analiz için)
            rating_reviews_count: Tüm puanlamalar (istatistik için)
            google_maps_url: İşletmenin direkt Google Maps URL'si
        """
        print(f"🚀 Firefox Google Maps Review Scraper Başlıyor...")
        print(f"📍 İşletme: {business_name}")
        
        if google_maps_url:
            print(f"🔗 Direkt URL kullanılıyor: {google_maps_url[:60]}...")
        else:
            print(f"🌍 Konum: {location}")
            
        print(f"📊 Hedef: {text_reviews_count} metin yorumu + {rating_reviews_count} puanlama")
        print("=" * 60)
        
        try:
            # 1. WebDriver'ı başlat
            self.setup_driver()
            
            # 2. İşletmeye git (URL varsa direkt, yoksa arama yap)
            if google_maps_url:
                # YENİ: Direkt URL'ye git
                if not self.navigate_to_business_url(google_maps_url):
                    print("❌ Direkt URL'ye gidilemedi!")
                    return []
                # URL kullanırken ilk sonuca tıklama adımı atlanır
            else:
                # ESKİ YOL: Arama yap
                if not self.search_business(business_name, location):
                    print("❌ İşletme aranamadı!")
                    return []
                
                # 3. İlk sonuca tıkla (sadece arama yapıldığında)
                if not self.click_first_result():
                    print("❌ İlk sonuca tıklanamadı!")
                    return []
            
            # 4. Yorumlar sekmesine git
            if not self.navigate_to_reviews():
                print("❌ Yorumlar sekmesine gidilemedi!")
                return []
            
            # 4.5. En yeni yorumları seç - YENİ ÖZELLİK!
            if not self.select_newest_reviews():
                print("⚠️ En yeni yorumlar seçilemedi, mevcut sıralama ile devam ediliyor...")
            
            # 5. Yorumları çıkar - YENİ: İki farklı sayaç ile
            reviews = self.extract_reviews_with_stats(text_reviews_count, rating_reviews_count)
            
            if reviews['text_reviews']:
                # 6. Sonuçları göster
                self.display_results_with_stats(reviews)
                
                # 7. CSV'ye kaydet  
                csv_file = self.save_to_csv(reviews['text_reviews'], business_name)
                
                print(f"\n✅ İşlem tamamlandı!")
                print(f"📊 Metin yorumları: {len(reviews['text_reviews'])}")
                print(f"📈 Toplam puanlama: {len(reviews['all_ratings'])}")
                print(f"📁 Dosya: {csv_file}")
                
                return reviews
            else:
                print("❌ Hiç yorum çıkarılamadı!")
                return {'text_reviews': [], 'all_ratings': [], 'statistics': {}}
                
        except Exception as e:
            print(f"❌ Ana süreç hatası: {e}")
            import traceback
            traceback.print_exc()
            return {'text_reviews': [], 'all_ratings': [], 'statistics': {}}
            
        finally:
            self.cleanup()

# Test fonksiyonu
def test_scraper():
    """Scraper'ı test et"""
    print("🧪 Test başlıyor...")
    
    scraper = FirefoxGoogleMapsReviewScraper(headless=False)
    
    # Test verileri
    business_name = "Starbucks Zorlu Center"
    location = "İstanbul"
    max_reviews = 5
    
    reviews = scraper.scrape_reviews(business_name, location, max_reviews)
    
    if reviews:
        print(f"\n🎉 Test başarılı! {len(reviews)} yorum çıkarıldı.")
    else:
        print("\n❌ Test başarısız!")

def test_with_url():
    """URL ile test et - YENİ PARAMETRİK SİSTEM"""
    print("🧪 URL ile test başlıyor...")
    
    scraper = FirefoxGoogleMapsReviewScraper(headless=False)
    
    # Test verileri - direkt URL ile (Sabiha Gökçen Havalimanı)
    business_name = "Sabiha Gökçen Havalimanı"
    google_maps_url = "https://www.google.com/maps/place/%C4%B0stanbul+Sabiha+G%C3%B6k%C3%A7en+Uluslararas%C4%B1+Havaliman%C4%B1/@40.9066492,29.3133517,17z/data=!3m1!4b1!4m6!3m5!1s0x14cadbcbf424a153:0xacefca4d8098da74!8m2!3d40.8944747!4d29.3130928!16zL20vMDJnbmhx?entry=ttu&g_ep=EgoyMDI1MDkwMy4wIKXMDSoASAFQAw%3D%3D"
    
    # Yeni parametrik sistem
    text_reviews = 15    # Sadece metin içeren yorumlar
    rating_reviews = 30  # Toplam puanlamalar (istatistik için)
    
    results = scraper.scrape_reviews(
        business_name=business_name,
        text_reviews_count=text_reviews,
        rating_reviews_count=rating_reviews,
        google_maps_url=google_maps_url
    )
    
    if results and results['text_reviews']:
        text_count = len(results['text_reviews'])
        rating_count = len(results['all_ratings'])
        print(f"\n🎉 URL Test başarılı!")
        print(f"📝 Metin yorumları: {text_count}")
        print(f"📊 Toplam puanlama: {rating_count}")
        if results['statistics']:
            avg = results['statistics'].get('rating_average', 0)
            print(f"⭐ Ortalama puan: {avg:.1f}/5")
    else:
        print("\n❌ URL Test başarısız!")

if __name__ == "__main__":
    # Kullanıcıya seçenek sun
    print("🔥 Google Maps Review Scraper")
    print("=" * 40)
    print("1. Normal test (arama ile)")
    print("2. URL test (direkt link ile)")
    
    choice = input("Seçiminizi yapın (1 veya 2): ").strip()
    
    if choice == "2":
        test_with_url()
    else:
        test_scraper()
