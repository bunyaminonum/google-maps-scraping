"""
Veritabanı Entegrasyonlu Google Maps Review Scraper
SQLite veritabanı ile tam entegrasyon
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
from datetime import datetime, timezone
import uuid
import sqlite3
import pytz

# Database sınıfını import et
from database_test import ReviewsDatabase

@dataclass
class Review:
    reviewer_name: str
    review_text: str
    rating: str
    date: str
    is_new: bool = False
    platform: str = "Google Maps"

class DatabaseGoogleMapsScraper:
    """Veritabanı entegrasyonlu Google Maps Review Scraper"""
    
    def __init__(self, headless: bool = False, db_path: str = "reviews.db"):
        self.driver = None
        self.headless = headless
        self.wait = None
        self.db = ReviewsDatabase(db_path)
        
    def parse_relative_time_to_timestamp(self, relative_time_str):
        """Türkçe göreceli zaman ifadelerini timestamp'e çevirir"""
        try:
            # Türkiye saat dilimi
            tr_tz = pytz.timezone('Europe/Istanbul')
            now = datetime.now(tr_tz)
            
            # Boşlukları temizle ve küçük harfe çevir
            time_str = relative_time_str.strip().lower()
            
            # Farklı formatları kontrol et
            if any(word in time_str for word in ['şimdi', 'az önce', 'biraz önce']):
                return now
            
            # Saat kontrolü
            hour_patterns = [
                r'(\d+)\s*saat\s*önce',
                r'bir\s*saat\s*önce'
            ]
            
            for pattern in hour_patterns:
                match = re.search(pattern, time_str)
                if match:
                    if 'bir saat' in time_str:
                        hours = 1
                    else:
                        hours = int(match.group(1))
                    return now - pd.Timedelta(hours=hours)
            
            # Gün kontrolü
            day_patterns = [
                r'(\d+)\s*gün\s*önce',
                r'bir\s*gün\s*önce',
                r'(\d+)\s*gün\s*önce\s*düzenlendi',
                r'bir\s*gün\s*önce\s*düzenlendi'
            ]
            
            for pattern in day_patterns:
                match = re.search(pattern, time_str)
                if match:
                    if 'bir gün' in time_str:
                        days = 1
                    else:
                        days = int(match.group(1))
                    return now - pd.Timedelta(days=days)
            
            # Hafta kontrolü
            week_patterns = [
                r'(\d+)\s*hafta\s*önce',
                r'bir\s*hafta\s*önce'
            ]
            
            for pattern in week_patterns:
                match = re.search(pattern, time_str)
                if match:
                    if 'bir hafta' in time_str:
                        weeks = 1
                    else:
                        weeks = int(match.group(1))
                    return now - pd.Timedelta(weeks=weeks)
            
            # Ay kontrolü
            month_patterns = [
                r'(\d+)\s*ay\s*önce',
                r'bir\s*ay\s*önce'
            ]
            
            for pattern in month_patterns:
                match = re.search(pattern, time_str)
                if match:
                    if 'bir ay' in time_str:
                        months = 1
                    else:
                        months = int(match.group(1))
                    return now - pd.DateOffset(months=months)
            
            # Yıl kontrolü
            year_patterns = [
                r'(\d+)\s*yıl\s*önce',
                r'bir\s*yıl\s*önce'
            ]
            
            for pattern in year_patterns:
                match = re.search(pattern, time_str)
                if match:
                    if 'bir yıl' in time_str:
                        years = 1
                    else:
                        years = int(match.group(1))
                    return now - pd.DateOffset(years=years)
            
            print(f"⚠️ Zaman formatı tanınmadı: '{relative_time_str}'")
            return now
            
        except Exception as e:
            print(f"❌ Zaman parsing hatası: {e}")
            return datetime.now(pytz.timezone('Europe/Istanbul'))
    
    def categorize_timestamp(self, timestamp):
        """Timestamp'i kategorilere ayırır"""
        try:
            tr_tz = pytz.timezone('Europe/Istanbul')
            now = datetime.now(tr_tz)
            
            # Timezone aware hale getir
            if timestamp.tzinfo is None:
                timestamp = tr_tz.localize(timestamp)
            
            diff = now - timestamp
            
            if diff.days == 0:
                return "Bugün"
            elif diff.days == 1:
                return "Dün"
            elif diff.days <= 7:
                return "Bu Hafta"
            elif diff.days <= 30:
                return "Bu Ay"
            else:
                return "Eski"
                
        except Exception as e:
            print(f"❌ Kategori belirleme hatası: {e}")
            return "Belirsiz"
    
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
        
        try:
            service = Service(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=firefox_options)
            self.wait = WebDriverWait(self.driver, 10)
            print("✅ Firefox başlatıldı")
            return True
        except Exception as e:
            print(f"❌ Firefox başlatma hatası: {e}")
            return False
    
    def go_to_url(self, url: str):
        """Verilen URL'ye gider"""
        print(f"🔗 Direkt URL'ye gidiliyor: {url[:50]}...")
        self.driver.get(url)
        time.sleep(3)
        print("✅ İşletme sayfasına gidildi")
    
    def click_reviews_tab(self):
        """Yorumlar sekmesine tıklar"""
        print("📝 Yorumlar sekmesine gidiliyor...")
        
        try:
            # Çoklu selector ile yorumlar tab'ını ara
            reviews_selectors = [
                "button[role='tab'][aria-label*='yorumlar' i]",
                "button[role='tab'][aria-label*='Yorumlar']",
                "button[role='tab'][aria-label*='reviews' i]",
                "button[role='tab'][aria-label*='Reviews']",
                "[role='tab'][aria-label*='yorum']",
                "button[data-tab-index='1']",  # İkinci tab genelde yorumlar
                ".hh2c6:nth-child(2) button",  # 2. tab pozisyonu
                "button[aria-label*='comment']"
            ]
            
            reviews_tab = None
            for selector in reviews_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        aria_label = element.get_attribute('aria-label') or ''
                        if ('yorum' in aria_label.lower() or 
                            'review' in aria_label.lower() or
                            'comment' in aria_label.lower()):
                            reviews_tab = element
                            print(f"✅ Yorumlar tab'ı bulundu: {selector} -> '{aria_label}'")
                            break
                    if reviews_tab:
                        break
                except:
                    continue
            
            if not reviews_tab:
                # Eğer spesifik tab bulunamazsa, tüm tab'ları kontrol et
                print("⚠️ Spesifik yorumlar tab'ı bulunamadı, tüm tab'ları kontrol ediliyor...")
                all_tabs = self.driver.find_elements(By.CSS_SELECTOR, "button[role='tab']")
                
                for i, tab in enumerate(all_tabs):
                    aria_label = tab.get_attribute('aria-label') or ''
                    text_content = tab.text or ''
                    print(f"   Tab {i+1}: '{aria_label}' / '{text_content}'")
                    
                    if (i == 1 or  # İkinci tab genelde yorumlar
                        'yorum' in aria_label.lower() or 
                        'review' in aria_label.lower()):
                        reviews_tab = tab
                        print(f"✅ Tab {i+1} yorumlar olarak seçildi")
                        break
            
            if reviews_tab:
                self.driver.execute_script("arguments[0].click();", reviews_tab)
                print(f"✅ Yorumlar tab'ı tıklandı")
                time.sleep(3)  # Yorumlar yüklensin
                return True
            else:
                print("❌ Hiç uygun yorumlar tab'ı bulunamadı")
                return False
            
        except Exception as e:
            print(f"❌ Yorumlar tab'ı tıklama hatası: {e}")
            return False
    
    def select_newest_reviews(self):
        """En yeni yorumları seçer - Firefox optimized scraper metodunu kullanır"""
        print("🔄 En yeni yorumlar durumu kontrol ediliyor...")
        
        try:
            # Dropdown'ı bul - çoklu selector ile
            dropdown_selectors = [
                "button[data-value='Sort']",
                "button[aria-label*='En alakalı']", 
                "button[aria-label*='En yeni']",  # Eğer zaten "En yeni" seçiliyse
                ".RWPxGd button[role='button']"  # Backup selector
            ]
            
            dropdown_button = None
            for selector in dropdown_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        dropdown_button = elements[0]
                        print(f"✅ Dropdown bulundu: {selector}")
                        break
                except:
                    continue
            
            if not dropdown_button:
                print("❌ Dropdown buton bulunamadı")
                return False
            
            # Mevcut durumu kontrol et
            aria_label = dropdown_button.get_attribute('aria-label') or ''
            text_content = dropdown_button.text or ''
            
            print(f"📋 Dropdown durumu: '{aria_label}' (aria-label: '{aria_label}')")
            
            # Eğer zaten "En yeni" seçiliyse, işlem tamamlandı
            if "En yeni" in text_content or "En yeni" in aria_label:
                print("✅ Zaten 'En yeni' seçili durumda!")
                return True
            else:
                print("🔄 'En alakalı'dan 'En yeni'ye geçiliyor...")
                
                # Dropdown'ı aç
                self.driver.execute_script("arguments[0].click();", dropdown_button)
                print("✅ Dropdown açıldı")
                time.sleep(2)  # Dropdown'ın açılması için bekle
                
                # JavaScript ile "En yeni" seçeneğini bul ve tıkla
                print("🎯 'En yeni' seçeneği aranıyor...")
                
                select_newest_script = """
                // Tüm tıklanabilir elementleri bul
                const elements = document.querySelectorAll('div, button, span');
                let found = false;
                
                for (let element of elements) {
                    const text = element.textContent || '';
                    const ariaLabel = element.getAttribute('aria-label') || '';
                    
                    if ((text === 'En yeni' || ariaLabel.includes('En yeni')) && 
                        element.offsetParent !== null) {
                        element.click();
                        found = true;
                        break;
                    }
                }
                
                return found;
                """
                
                result = self.driver.execute_script(select_newest_script)
                
                if result:
                    print("✅ 'En yeni' başarıyla seçildi!")
                    time.sleep(3)  # "En yeni" seçiminin etkili olması için bekle
                    return True
                else:
                    print("❌ 'En yeni' seçeneği bulunamadı")
                    return False
                
        except Exception as e:
            print(f"❌ 'En yeni' seçme hatası: {e}")
            return False
    
    def _expand_review_if_needed(self, container):
        """Yorumda 'Daha fazla' butonu varsa tıklar - Gelişmiş versiyon"""
        try:
            expanded_count = 0
            
            # Çoklu stratejilerle "Daha fazla" butonunu bul
            strategies = [
                # Strateji 1: En spesifik selector - verdiğiniz HTML'den
                ".w8nwRe.kyuRq",
                
                # Strateji 2: Aria-label ile farklı varyasyonlar
                "button[aria-label*='Daha fazla']",
                "button[aria-label*='daha fazla']", 
                "button[aria-label='Daha fazla göster']",
                
                # Strateji 3: JS action ile
                "button[jsaction*='review']",
                
                # Strateji 4: Genel button arama
                "button.w8nwRe",
                "button[class*='w8nwRe']",
                
                # Strateji 5: Parent container içinde herhangi bir "more" butonu
                "[role='button'][aria-label*='fazla']"
            ]
            
            # İlk olarak JavaScript ile "Daha fazla" içeren butonları ara
            try:
                js_buttons = self.driver.execute_script("""
                    var container = arguments[0];
                    var buttons = container.querySelectorAll('button, [role="button"]');
                    var foundButtons = [];
                    
                    for(var i = 0; i < buttons.length; i++) {
                        var btn = buttons[i];
                        var text = (btn.textContent || '').toLowerCase();
                        var aria = (btn.getAttribute('aria-label') || '').toLowerCase();
                        
                        if(text.includes('daha fazla') || aria.includes('daha fazla') || 
                           text.includes('more') || aria.includes('more')) {
                            foundButtons.push(btn);
                        }
                    }
                    return foundButtons;
                """, container)
                
                if js_buttons:
                    print(f"   🔍 JavaScript ile {len(js_buttons)} adet 'Daha fazla' butonu bulundu")
                    
                    for button in js_buttons:
                        try:
                            if (button.is_displayed() and 
                                button.is_enabled() and
                                button.get_attribute('aria-expanded') != 'true'):
                                
                                print(f"   🔄 JS bulduğu buton tıklanıyor...")
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                time.sleep(0.2)
                                self.driver.execute_script("arguments[0].click();", button)
                                print(f"   ✅ JS buton tıklandı!")
                                time.sleep(0.8)
                                expanded_count += 1
                                
                        except Exception:
                            continue
                            
            except Exception as js_e:
                print(f"   ⚠️ JavaScript arama hatası: {js_e}")
            
            # Eğer JS ile bulunamadıysa, klasik CSS selectors ile dene
            
            for strategy in strategies:
                try:
                    # Container içinde butonları ara
                    buttons = container.find_elements(By.CSS_SELECTOR, strategy)
                    
                    for button in buttons:
                        try:
                            # Butonun metin içeriğini kontrol et
                            text_content = button.text.strip().lower()
                            aria_label = (button.get_attribute('aria-label') or '').lower()
                            
                            # "Daha fazla" içeren metinleri ara
                            if ('daha fazla' in text_content or 
                                'daha fazla' in aria_label or
                                'more' in text_content.lower()):
                                
                                # Butonun durumunu kontrol et
                                if (button.is_displayed() and 
                                    button.is_enabled() and
                                    button.get_attribute('aria-expanded') != 'true'):
                                    
                                    print(f"   🔄 'Daha fazla' butonu bulundu: {strategy}")
                                    print(f"   📝 Buton metni: '{button.text}' / Aria: '{button.get_attribute('aria-label')}'")
                                    
                                    # Scroll to button first
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                    time.sleep(0.2)
                                    
                                    # JavaScript ile tıkla
                                    self.driver.execute_script("arguments[0].click();", button)
                                    print(f"   ✅ 'Daha fazla' butonu tıklandı!")
                                    
                                    time.sleep(0.8)  # Expansion için bekle
                                    expanded_count += 1
                                    
                        except Exception as btn_e:
                            continue
                            
                except Exception as strategy_e:
                    continue
            
            if expanded_count > 0:
                print(f"   📈 {expanded_count} adet 'Daha fazla' butonu genişletildi")
                return True
            else:
                # Hiç buton bulunamadı - debug için kontrol et
                all_buttons = container.find_elements(By.TAG_NAME, "button")
                print(f"   🔍 Container'da toplam {len(all_buttons)} buton var")
                
                for i, btn in enumerate(all_buttons[:5]):  # İlk 5 butonu kontrol et
                    btn_text = btn.text.strip()[:30]
                    btn_aria = (btn.get_attribute('aria-label') or '')[:30]
                    if btn_text or btn_aria:
                        print(f"     Buton {i+1}: '{btn_text}' / '{btn_aria}'")
                
                return False
            
        except Exception as e:
            print(f"   ⚠️ _expand_review_if_needed hatası: {e}")
            return False
    
    def _smart_scroll_for_reviews(self, target_count: int = 30) -> int:
        """Google Maps yorumları için akıllı scroll sistemi"""
        print(f"🎯 Google Maps yorumları için gerçek scroll başlıyor (hedef: {target_count})")
        
        try:
            # Reviews container'ı bul
            container = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde"))
            )
            print("✅ Scrollable container bulundu: .m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde")
            
            last_count = 0
            stable_count = 0
            scroll_attempt = 0
            max_attempts = 20
            
            while scroll_attempt < max_attempts:
                scroll_attempt += 1
                
                # Mevcut yorum sayısını say
                current_reviews = self.driver.find_elements(By.CSS_SELECTOR, ".jftiEf.fontBodyMedium")
                current_count = len(current_reviews)
                
                print(f"📊 Scroll {scroll_attempt}: {current_count} yorum (hedef: {target_count})")
                
                # Hedef ulaşıldı mı?
                if current_count >= target_count:
                    print("✅ Hedef ulaşıldı: {} yorum".format(current_count))
                    break
                
                # Yeni yorum yüklendi mi?
                if current_count > last_count:
                    print(f"   ➕ {current_count - last_count} yeni yorum yüklendi")
                    last_count = current_count
                    stable_count = 0
                    
                    # Container'ın içinde scroll yap
                    print("   🎯 Container scroll (direkt)")
                    self.driver.execute_script("""
                        arguments[0].scrollTop = arguments[0].scrollHeight;
                    """, container)
                    
                else:
                    stable_count += 1
                    print(f"   ⏳ Sabit kalma: {stable_count}/3")
                    
                    if stable_count >= 3:
                        print("   📜 Kademeli scroll")
                        # Daha küçük adımlarla scroll
                        for i in range(3):
                            self.driver.execute_script(f"""
                                arguments[0].scrollTop += 500;
                            """, container)
                            time.sleep(0.5)
                    else:
                        # Son yoruma git
                        print("   ⬇️ Son yoruma scroll")
                        if current_reviews:
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", current_reviews[-1])
                
                time.sleep(2)
            
            final_reviews = self.driver.find_elements(By.CSS_SELECTOR, ".jftiEf.fontBodyMedium")
            final_count = len(final_reviews)
            
            print("🏁 Scroll tamamlandı!")
            print(f"   📈 Toplam yorum: {final_count}")
            print(f"   🔢 Hedef: {target_count}")
            print(f"   ✨ Başarı oranı: %{(min(final_count, target_count) / target_count) * 100:.1f}")
            
            return final_count
            
        except Exception as e:
            print(f"❌ Scroll hatası: {e}")
            return 0
    
    def extract_reviews_with_database(self, business_name: str, business_url: str = "", 
                                    text_reviews_target: int = 10, 
                                    total_ratings_target: int = 20) -> dict:
        """Yorumları çıkarır ve veritabanına kaydeder"""
        
        print("📊 Akıllı veri toplama başlıyor...")
        print(f"🎯 Hedef: {text_reviews_target} metin yorumu + {total_ratings_target} puanlama")
        
        # Session ID oluştur
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Yeterli veri için scroll
        print("📜 Yeterli veri yüklemek için akıllı scroll...")
        scroll_target = max(total_ratings_target, text_reviews_target * 2)
        loaded_count = self._smart_scroll_for_reviews(scroll_target)
        
        try:
            # Tüm yorum container'larını bul
            review_containers = self.driver.find_elements(By.CSS_SELECTOR, ".jftiEf.fontBodyMedium")
            print(f"🎯 {len(review_containers)} toplam yorum container'ı bulundu\\n")
            
            reviews_data = []
            text_reviews_count = 0
            total_ratings_count = 0
            ratings_sum = 0
            
            for i, container in enumerate(review_containers, 1):
                print(f"📋 Container {i}/{len(review_containers)} işleniyor...")
                
                try:
                    # Yorumcu ismi
                    try:
                        reviewer_element = container.find_element(By.CSS_SELECTOR, ".d4r55")
                        reviewer_name = reviewer_element.text.strip()
                    except:
                        reviewer_name = "Anonim"
                    
                    # Puan
                    try:
                        rating_element = container.find_element(By.CSS_SELECTOR, ".kvMYJc")
                        rating_aria = rating_element.get_attribute("aria-label")
                        rating = re.search(r'(\\d+)', rating_aria).group(1) if rating_aria else "0"
                        rating = int(rating)
                    except:
                        rating = 0
                    
                    if rating > 0:
                        ratings_sum += rating
                        total_ratings_count += 1
                        print(f"   📈 Puanlama eklendi: {rating} yıldız")
                    
                    # Tarih
                    try:
                        date_element = container.find_element(By.CSS_SELECTOR, ".rsqaWe")
                        date_text = date_element.text.strip()
                    except:
                        date_text = "Tarih bilinmiyor"
                    
                    # Yorum metni - SON HALİ: DAHA FAZLA GENİŞLETME
                    try:
                        # İlk olarak mevcut yorum metnini al
                        review_element = container.find_element(By.CSS_SELECTOR, ".wiI7pd")
                        initial_text = review_element.text.strip()
                        initial_length = len(initial_text)
                        
                        # Eğer metin çok kısaysa veya "..." ile bitiyorsa genişletmeye çalış
                        needs_expansion = (initial_length < 200 or 
                                         initial_text.endswith('...') or 
                                         initial_text.endswith('…'))
                        
                        if needs_expansion:
                            print(f"   🔍 Genişletme denenecek: {initial_length} karakter, bitisi: '{initial_text[-10:]}'")
                            
                            # "Daha fazla" butonunu kontrol et ve tıkla
                            expansion_success = self._expand_review_if_needed(container)
                            
                            # Genişletme sonrası yeniden metin al
                            time.sleep(0.8)  # DOM'un güncellenmesi için bekle
                            
                            try:
                                review_element = container.find_element(By.CSS_SELECTOR, ".wiI7pd")
                                final_text = review_element.text.strip()
                                final_length = len(final_text)
                                
                                if final_length > initial_length:
                                    print(f"   📈 ✅ Metin GENİŞLETİLDİ: {initial_length} → {final_length} karakter (+{final_length-initial_length})")
                                else:
                                    print(f"   📊 Metin değişmedi: {final_length} karakter")
                                    
                            except:
                                final_text = initial_text
                                final_length = initial_length
                                print(f"   ⚠️ Genişletme sonrası metin alınamadı")
                        else:
                            final_text = initial_text
                            final_length = initial_length
                            print(f"   📏 Genişletme gerekmiyor: {initial_length} karakter")
                        
                        review_text = final_text
                        
                        if review_text and len(review_text) > 5:
                            text_reviews_count += 1
                            print(f"   ✅ Metin yorumu eklendi: {reviewer_name[:15]}... ({len(review_text)} karakter)")
                            
                            # Timestamp parse et
                            timestamp_parsed = self.parse_relative_time_to_timestamp(date_text)
                            time_category = self.categorize_timestamp(timestamp_parsed)
                            
                            # Veritabanı için veri hazırla
                            review_data = {
                                'business_name': business_name,
                                'business_url': business_url,
                                'reviewer_name': reviewer_name,
                                'rating': rating,
                                'date': date_text,
                                'review_text': review_text,
                                'timestamp_parsed': timestamp_parsed.isoformat(),
                                'time_category': time_category
                            }
                            
                            reviews_data.append(review_data)
                        else:
                            review_text = ""
                    except:
                        review_text = ""
                    
                    # Hedeflere ulaşıldı mı kontrol et
                    if (text_reviews_count >= text_reviews_target and 
                        total_ratings_count >= total_ratings_target):
                        print("🎯 Her iki hedefe de ulaşıldı!")
                        break
                        
                except Exception as e:
                    print(f"   ❌ Container {i} işleme hatası: {e}")
                    continue
            
            print("\\n🎉 Veri toplama tamamlandı!")
            print(f"📝 Metin yorumları: {text_reviews_count}")
            print(f"📊 Toplam puanlama: {total_ratings_count}")
            
            # Session bilgilerini hazırla
            average_rating = ratings_sum / total_ratings_count if total_ratings_count > 0 else 0
            
            session_data = {
                'session_id': session_id,
                'business_name': business_name,
                'business_url': business_url,
                'target_text_reviews': text_reviews_target,
                'target_total_ratings': total_ratings_target,
                'actual_text_reviews': text_reviews_count,
                'actual_total_ratings': total_ratings_count,
                'average_rating': round(average_rating, 1),
                'status': 'completed'
            }
            
            # Veritabanına kaydet
            print("\\n💾 Veritabanına kaydediliyor...")
            self.db.save_scrape_session(session_data)
            self.db.save_reviews(reviews_data, session_id)
            
            return {
                'session_data': session_data,
                'reviews_data': reviews_data,
                'statistics': {
                    'text_reviews_count': text_reviews_count,
                    'total_ratings_count': total_ratings_count,
                    'average_rating': average_rating,
                    'success_rate': (min(text_reviews_count, text_reviews_target) / text_reviews_target) * 100
                }
            }
            
        except Exception as e:
            print(f"❌ Veri çıkarma hatası: {e}")
            return {'error': str(e)}
    
    def scrape_business_reviews(self, business_name: str = None, business_url: str = None,
                              text_reviews_target: int = 10, total_ratings_target: int = 20):
        """İşletme yorumlarını toplar"""
        
        if not business_url:
            print("❌ business_url parametresi gerekli!")
            return None
        
        if not business_name:
            business_name = "Bilinmeyen İşletme"
        
        print("🚀 Veritabanı Entegrasyonlu Google Maps Review Scraper Başlıyor...")
        print(f"📍 İşletme: {business_name}")
        print(f"🔗 Direkt URL kullanılıyor: {business_url[:60]}...")
        print(f"📊 Hedef: {text_reviews_target} metin yorumu + {total_ratings_target} puanlama")
        print("=" * 60)
        
        # WebDriver'ı başlat
        if not self.setup_driver():
            return None
        
        try:
            # URL'ye git
            self.go_to_url(business_url)
            
            # Yorumlar sekmesine geç
            if not self.click_reviews_tab():
                return None
            
            # En yeni yorumları seç
            if not self.select_newest_reviews():
                print("⚠️ 'En yeni' seçilemedi, mevcut sıralama ile devam ediliyor")
            
            # Yorumları çıkar ve veritabanına kaydet
            result = self.extract_reviews_with_database(
                business_name=business_name,
                business_url=business_url,
                text_reviews_target=text_reviews_target,
                total_ratings_target=total_ratings_target
            )
            
            if 'error' not in result:
                print("\\n✅ İşlem tamamlandı!")
                stats = result['statistics']
                print(f"📊 Metin yorumları: {stats['text_reviews_count']}")
                print(f"📈 Toplam puanlama: {stats['total_ratings_count']}")
                print(f"🎯 Başarı oranı: %{stats['success_rate']:.1f}")
                print(f"📁 Session ID: {result['session_data']['session_id']}")
            
            return result
            
        except Exception as e:
            print(f"❌ Ana scraping hatası: {e}")
            return None
            
        finally:
            if self.driver:
                self.driver.quit()
                print("🔒 Firefox kapatıldı")

def main():
    """Test amaçlı ana fonksiyon"""
    
    # Test URL'si - Güncellenmiş tam URL
    test_url = "https://www.google.com/maps/place/%C4%B0stanbul+Sabiha+G%C3%B6k%C3%A7en+Uluslararas%C4%B1+Havaliman%C4%B1/@40.9066374,29.3133253,17z/data=!4m8!3m7!1s0x14cadbcbf424a153:0xacefca4d8098da74!8m2!3d40.8944747!4d29.3130928!9m1!1b1!16zL20vMDJnbmhx?entry=ttu&g_ep=EgoyMDI1MDkwMy4wIKXMDSoASAFQAw%3D%3D"
    
    # Scraper'ı başlat
    scraper = DatabaseGoogleMapsScraper(headless=False, db_path="main_reviews.db")
    
    # Yorumları topla
    result = scraper.scrape_business_reviews(
        business_name="İstanbul Sabiha Gökçen Uluslararası Havalimanı",
        business_url=test_url,
        text_reviews_target=5,
        total_ratings_target=10
    )
    
    if result and 'error' not in result:
        print("\\n🎉 Veritabanı entegrasyonu başarılı!")

if __name__ == "__main__":
    main()
