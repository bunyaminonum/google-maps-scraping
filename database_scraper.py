"""
Google Maps Review Scraper with Database Integration
Full integration with SQLite database
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
from turkish_time_parser import TurkishTimeParser

@dataclass
class Review:
    reviewer_name: str
    review_text: str
    rating: str
    date: str
    timestamp: Optional[datetime] = None
    time_category: str = "today"
    is_new: bool = False
    platform: str = "Google Maps"

class DatabaseGoogleMapsScraper:
    """Google Maps Review Scraper with database integration"""
    
    def __init__(self, headless: bool = False, db_path: str = "reviews.db"):
        self.driver = None
        self.wait = None
        self.headless = headless
        self.reviews = []
        
        # Database connection
        self.db = ReviewsDatabase(db_path)
        
        # Turkish time parser
        self.time_parser = TurkishTimeParser()
        
        # Statistics
        self.scraped_count = 0
        self.text_review_count = 0
        self.rating_only_count = 0
        
        print("✅ Database connection established")

    def setup_driver(self):
        """Set up Firefox WebDriver"""
        print("🦊 Setting up Firefox WebDriver...")
        
        try:
            options = Options()
            
            if self.headless:
                options.add_argument("--headless")
            
            # Performance improvements
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-logging")
            options.add_argument("--disable-images")
            
            # User agent
            options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # Automatic driver management with GeckoDriverManager
            service = Service(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=options)
            
            # Page load timeout
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)
            
            # WebDriverWait
            self.wait = WebDriverWait(self.driver, 20)
            
            print("✅ Firefox started successfully")
            
        except Exception as e:
            print(f"❌ WebDriver setup error: {e}")
            raise

    def close_driver(self):
        """Close WebDriver"""
        if self.driver:
            self.driver.quit()
            print("🔒 Firefox closed")

    def go_to_business_page(self, business_url: str = "", search_query: str = ""):
        """Navigate to business page"""
        try:
            if business_url and business_url.startswith("http"):
                print(f"🔗 Navigating to URL: {business_url[:50]}...")
                self.driver.get(business_url)
                print("✅ Navigated to business page")
                return True
            
            elif search_query:
                print(f"🔍 Searching on Google Maps: {search_query}")
                self.driver.get("https://www.google.com/maps")
                
                # Search box
                search_box = self.wait.until(
                    EC.presence_of_element_located((By.ID, "searchboxinput"))
                )
                search_box.clear()
                search_box.send_keys(search_query)
                search_box.send_keys(Keys.ENTER)
                
                time.sleep(3)
                
                # Click first result
                first_result = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".hfpxzc"))
                )
                first_result.click()
                time.sleep(2)
                
                print("✅ Navigated to business page")
                return True
            
            else:
                print("❌ No URL or search query provided")
                return False
                
        except Exception as e:
            print(f"❌ Page loading error: {e}")
            return False

    def go_to_reviews_tab(self):
        """Navigate to reviews tab"""
        print("📝 Navigating to reviews tab...")
        
        try:
            # Find and click reviews tab
            reviews_tab_selectors = [
                "button[role='tab'][aria-label*='yorumlar' i]",
                "button[role='tab'][aria-label*='review' i]",
                "button[data-tab-index='2']",
                ".hh2c6[data-tab-index='2']"
            ]
            
            reviews_tab = None
            for selector in reviews_tab_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        aria_label = element.get_attribute("aria-label") or ""
                        if "yorumlar" in aria_label.lower() or "review" in aria_label.lower():
                            reviews_tab = element
                            print(f"✅ Reviews tab found: {selector} -> '{aria_label}'")
                            break
                    if reviews_tab:
                        break
                except:
                    continue
            
            if not reviews_tab:
                print("❌ Reviews tab not found")
                return False
            
            # Click tab
            self.driver.execute_script("arguments[0].click();", reviews_tab)
            time.sleep(3)
            print("✅ Reviews tab clicked")
            return True
            
        except Exception as e:
            print(f"❌ Reviews tab error: {e}")
            return False

    def set_to_newest_reviews(self):
        """Switch to newest reviews mode"""
        print("🔄 Checking newest reviews status...")
        
        try:
            # Find dropdown button
            dropdown_selectors = [
                "button[aria-label*='En alakalı']",
                "button[aria-label*='Most relevant']",
                "button[data-value='Sort']",
                ".P1hlSl",
                ".fxNQSd"
            ]
            
            dropdown_button = None
            for selector in dropdown_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.get_attribute("aria-label") or element.text
                        if any(keyword in text.lower() for keyword in ['alakalı', 'relevant', 'sort']):
                            dropdown_button = element
                            print(f"✅ Dropdown found: {selector}")
                            break
                    if dropdown_button:
                        break
                except:
                    continue
            
            if not dropdown_button:
                print("⚠️ Sort dropdown not found, continuing...")
                return True
            
            # Check dropdown status
            current_text = dropdown_button.get_attribute("aria-label") or dropdown_button.text
            print(f"📋 Dropdown status: '{current_text}' (aria-label: '{dropdown_button.get_attribute('aria-label')}')")
            
            # If already in "Newest" mode, no need to change
            if "yeni" in current_text.lower() or "newest" in current_text.lower():
                print("✅ Already in newest reviews mode")
                return True
            
            # Switch from "Most relevant" to "Newest"
            if "alakalı" in current_text.lower() or "relevant" in current_text.lower():
                print("🔄 Switching from 'Most relevant' to 'Newest'...")
                
                # Open dropdown
                self.driver.execute_script("arguments[0].click();", dropdown_button)
                time.sleep(2)
                print("✅ Dropdown opened")
                
                # Find and click "Newest" option
                print("🎯 Searching for 'Newest' option...")
                newest_selectors = [
                    "[role='menuitemradio'][aria-label*='yeni' i]",
                    "[role='menuitemradio'][aria-label*='newest' i]",
                    "[data-index='1']",
                    ".fxNQSd[data-index='1']"
                ]
                
                newest_option = None
                for selector in newest_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed():
                                aria_label = element.get_attribute("aria-label") or ""
                                text_content = element.text.strip()
                                if ("yeni" in aria_label.lower() or "newest" in aria_label.lower() or 
                                    "yeni" in text_content.lower() or "newest" in text_content.lower()):
                                    newest_option = element
                                    break
                        if newest_option:
                            break
                    except:
                        continue
                
                if newest_option:
                    self.driver.execute_script("arguments[0].click();", newest_option)
                    time.sleep(3)
                    print("✅ 'Newest' selected successfully!")
                    return True
                else:
                    print("⚠️ 'Newest' option not found, continuing with current sorting")
                    return True
            
            return True
            
        except Exception as e:
            print(f"❌ Sort change error: {e}")
            print("⚠️ Continuing with current sorting...")
            return True

    def smart_scroll_and_load_reviews(self, target_count: int = 60):
        """Akıllı scroll ile yeterli veriyi yükle"""
        print(f"🎯 Google Maps yorumları için gerçek scroll başlıyor (hedef: {target_count})")
        
        try:
            # Scroll yapılacak container'ı bul
            scrollable_container = None
            container_selectors = [
                ".m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde",  # Ana yorum container'ı
                "[role='main']",
                ".m6QErb.DxyBCb",
                "[aria-label*='yorumlar' i]"
            ]
            
            for selector in container_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            scrollable_container = element
                            print(f"✅ Scrollable container bulundu: {selector}")
                            break
                    if scrollable_container:
                        break
                except:
                    continue
            
            if not scrollable_container:
                print("❌ Scrollable container bulunamadı!")
                return False
            
            scroll_count = 0
            max_scrolls = 20
            stable_count = 0
            last_review_count = 0
            
            while scroll_count < max_scrolls:
                scroll_count += 1
                
                # Mevcut yorum sayısını kontrol et
                review_containers = self.driver.find_elements(By.CSS_SELECTOR, ".jftiEf")
                current_count = len(review_containers)
                
                print(f"📊 Scroll {scroll_count}: {current_count} yorum (hedef: {target_count})")
                
                # Hedef sayıya ulaştıysak dur
                if current_count >= target_count:
                    print("✅ Hedef ulaşıldı:", current_count, "yorum")
                    break
                
                # Yeni yorum eklendi mi kontrol et
                if current_count > last_review_count:
                    added = current_count - last_review_count
                    print(f"   ➕ {added} yeni yorum yüklendi")
                    last_review_count = current_count
                    stable_count = 0
                else:
                    stable_count += 1
                    print(f"   ⏳ Yeni yorum yüklenmedi (stable: {stable_count})")
                    
                    # 3 kez üst üste yeni yorum gelmezse dur
                    if stable_count >= 3:
                        print(f"   🛑 {stable_count} kez üst üste yeni yorum yüklenmedi, scroll durduruldu")
                        break
                
                # Container'ı scroll et
                try:
                    print(f"   🎯 Container scroll (direkt)")
                    self.driver.execute_script("""
                        arguments[0].scrollTop = arguments[0].scrollHeight;
                    """, scrollable_container)
                except:
                    # Alternatif scroll
                    try:
                        print(f"   🎯 Sayfa scroll (alternatif)")
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    except:
                        print(f"   ❌ Scroll hatası")
                
                # Scroll sonrası bekleme
                time.sleep(2)
            
            # Son durum
            final_containers = self.driver.find_elements(By.CSS_SELECTOR, ".jftiEf")
            final_count = len(final_containers)
            
            print("🏁 Scroll tamamlandı!")
            print(f"   📈 Toplam yorum: {final_count}")
            print(f"   🔢 Hedef: {target_count}")
            print(f"   ✨ Başarı oranı: %{(min(final_count, target_count) / target_count * 100):.1f}")
            
            return final_count > 0
            
        except Exception as e:
            print(f"❌ Scroll hatası: {e}")
            return False

    def expand_review_text(self, container):
        """Yorum metnini genişlet"""
        try:
            # Mevcut metni al
            review_element = container.find_element(By.CSS_SELECTOR, ".wiI7pd")
            initial_text = review_element.text.strip()
            initial_length = len(initial_text)
            
            # Kısa yorumlar için genişletme denenmesin
            if initial_length < 50:
                return initial_text
            
            print(f"   🔍 Genişletme denenecek: {initial_length} karakter, bitisi: '{initial_text[-10:]}'")
            
            # 1. JavaScript ile 'Daha fazla' butonlarını bul
            expand_buttons = self.driver.execute_script("""
                var container = arguments[0];
                var buttons = container.querySelectorAll('button');
                var expandButtons = [];
                
                for (var i = 0; i < buttons.length; i++) {
                    var btn = buttons[i];
                    var text = btn.textContent || btn.innerText || '';
                    var ariaLabel = btn.getAttribute('aria-label') || '';
                    
                    if (text.includes('Daha fazla') || text.includes('More') || 
                        ariaLabel.includes('Daha fazla') || ariaLabel.includes('More') ||
                        text.includes('Show more') || ariaLabel.includes('Show more')) {
                        expandButtons.push(btn);
                    }
                }
                
                return expandButtons.length;
            """, container)
            
            if expand_buttons > 0:
                print(f"   🔍 JavaScript ile {expand_buttons} adet 'Daha fazla' butonu bulundu")
                
                # Butonları tıkla
                clicked = self.driver.execute_script("""
                    var container = arguments[0];
                    var buttons = container.querySelectorAll('button');
                    var clickCount = 0;
                    
                    for (var i = 0; i < buttons.length; i++) {
                        var btn = buttons[i];
                        var text = btn.textContent || btn.innerText || '';
                        var ariaLabel = btn.getAttribute('aria-label') || '';
                        
                        if (text.includes('Daha fazla') || text.includes('More') || 
                            ariaLabel.includes('Daha fazla') || ariaLabel.includes('More') ||
                            text.includes('Show more') || ariaLabel.includes('Show more')) {
                            try {
                                btn.click();
                                clickCount++;
                            } catch(e) {
                                console.log('Button click error:', e);
                            }
                        }
                    }
                    
                    return clickCount;
                """, container)
                
                if clicked > 0:
                    print(f"   🔄 JS bulduğu buton tıklanıyor...")
                    time.sleep(1)
                    print(f"   ✅ JS buton tıklandı!")
                    print(f"   📈 {clicked} adet 'Daha fazla' butonu genişletildi")
            else:
                # 2. Manuel buton arama (yedek yöntem)
                all_buttons = container.find_elements(By.TAG_NAME, "button")
                print(f"   🔍 Container'da toplam {len(all_buttons)} buton var")
                
                for i, button in enumerate(all_buttons, 1):
                    try:
                        btn_text = button.text.strip()
                        btn_aria = button.get_attribute("aria-label") or ""
                        print(f"     Buton {i}: '{btn_text[:30]}' / '{btn_aria[:30]}'")
                    except:
                        pass
            
            # Genişletme sonrası metni kontrol et
            time.sleep(0.5)
            new_review_element = container.find_element(By.CSS_SELECTOR, ".wiI7pd")
            final_text = new_review_element.text.strip()
            final_length = len(final_text)
            
            if final_length > initial_length:
                growth = final_length - initial_length
                print(f"   📈 ✅ Metin GENİŞLETİLDİ: {initial_length} → {final_length} karakter (+{growth})")
                return final_text
            else:
                print(f"   📊 Metin değişmedi: {final_length} karakter")
                return final_text
                
        except Exception as e:
            print(f"   ❌ Genişletme hatası: {e}")
            try:
                review_element = container.find_element(By.CSS_SELECTOR, ".wiI7pd")
                return review_element.text.strip()
            except:
                return ""

    def extract_reviews_with_database(self, business_name: str, business_url: str = "", 
                                    search_query: str = "", target_text_reviews: int = 30, 
                                    target_ratings: int = 50):
        """Extract reviews and save to database"""
        
        print(f"📊 Target: {target_text_reviews} text reviews + {target_ratings} ratings")
        print("=" * 60)
        
        if not self.driver:
            self.setup_driver()
        
        # Navigate to business page
        if not self.go_to_business_page(business_url, search_query):
            return {"success": False, "error": "Page could not be loaded"}
        
        # Go to reviews tab
        if not self.go_to_reviews_tab():
            return {"success": False, "error": "Reviews tab could not be opened"}
        
        # Switch to newest reviews mode
        self.set_to_newest_reviews()
        
        # Smart data collection
        print("📊 Smart data collection starting...")
        print(f"🎯 Target: {target_text_reviews} text reviews + {target_ratings} ratings")
        
        # Determine target review count (for more scrolling)
        total_target = max(target_text_reviews + target_ratings, 60)
        
        # Scroll and load reviews
        print("📜 Smart scroll to load sufficient data...")
        if not self.smart_scroll_and_load_reviews(total_target):
            return {"success": False, "error": "Reviews could not be loaded"}
        
        # Yorumları çek
        try:
            review_containers = self.driver.find_elements(By.CSS_SELECTOR, ".jftiEf")
            print(f"🎯 {len(review_containers)} toplam yorum container'ı bulundu\n")
            
            if not review_containers:
                return {"success": False, "error": "Yorum container'ları bulunamadı"}
            
            reviews = []
            text_review_count = 0
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
                    
                    # Puan - Yeni HTML yapısına göre güncellenmiş
                    try:
                        # İlk önce aria-label ile rating değerini arıyoruz
                        rating_elements = container.find_elements(By.CSS_SELECTOR, "span[aria-label*='yıldızlı']")
                        
                        if rating_elements:
                            rating_aria = rating_elements[0].get_attribute("aria-label")
                            # "4,7 yıldızlı" şeklindeki text'ten rakam çıkar
                            rating_match = re.search(r'(\d+[,.]?\d*)', rating_aria)
                            if rating_match:
                                rating_str = rating_match.group(1).replace(',', '.')
                                rating = float(rating_str)
                                print(f"   ⭐ Rating bulundu (aria-label): {rating}")
                            else:
                                rating = 0
                        else:
                            # Alternatif: .kvMYJc sınıfını dene
                            try:
                                rating_element = container.find_element(By.CSS_SELECTOR, ".kvMYJc")
                                rating_aria = rating_element.get_attribute("aria-label")
                                rating_match = re.search(r'(\d+)', rating_aria) if rating_aria else None
                                rating = int(rating_match.group(1)) if rating_match else 0
                                print(f"   ⭐ Rating bulundu (kvMYJc): {rating}")
                            except:
                                # Son alternatif: sayısal değeri direkt al
                                try:
                                    numeric_rating = container.find_element(By.CSS_SELECTOR, "span[aria-hidden='true']")
                                    rating_text = numeric_rating.text.strip().replace(',', '.')
                                    if rating_text and re.match(r'\d+[,.]?\d*', rating_text):
                                        rating = float(rating_text)
                                        print(f"   ⭐ Rating bulundu (numeric): {rating}")
                                    else:
                                        rating = 0
                                except:
                                    rating = 0
                                    print(f"   ❌ Rating bulunamadı")
                    except Exception as e:
                        print(f"   ❌ Rating hatası: {e}")
                        rating = 0
                    
                    if rating > 0:
                        ratings_sum += rating
                        total_ratings_count += 1
                        print(f"   📈 Puanlama eklendi: {rating} yıldız")
                    
                    # Tarih ve timestamp
                    try:
                        date_element = container.find_element(By.CSS_SELECTOR, ".rsqaWe")
                        date_text = date_element.text.strip()
                        
                        # Türkçe zaman ifadesini timestamp'e çevir
                        timestamp, time_category = self.time_parser.parse_turkish_time(date_text)
                        print(f"   📅 Tarih: {date_text} → {timestamp.strftime('%Y-%m-%d %H:%M')} ({time_category})")
                        
                    except:
                        date_text = "Tarih bilinmiyor"
                        timestamp = datetime.now(self.time_parser.timezone)
                        time_category = "today"
                    
                    # Yorum metni - SON HALİ: DAHA FAZLA GENİŞLETME
                    try:
                        # İlk olarak mevcut yorum metnini al
                        review_element = container.find_element(By.CSS_SELECTOR, ".wiI7pd")
                        initial_text = review_element.text.strip()
                        initial_length = len(initial_text)
                        
                        # Genişletme yapmaya değer mi?
                        if initial_length >= 250:
                            print(f"   📏 Genişletme gerekmiyor: {initial_length} karakter")
                            review_text = initial_text
                        else:
                            # Genişletmeyi dene
                            review_text = self.expand_review_text(container)
                        
                        # Metin yorumu sayısını kontrol et
                        if len(review_text) > 5:  # Minimum metin uzunluğu
                            if text_review_count < target_text_reviews:
                                text_review_count += 1
                                print(f"   ✅ Metin yorumu eklendi: {reviewer_name[:15]}... ({len(review_text)} karakter)")
                            else:
                                print(f"   ℹ️ Metin yorumu hedef aşıldı, atlandı")
                                review_text = ""  # Hedef aşıldıysa metni kaydetme
                        else:
                            print(f"   ⚠️ Yorum metni çok kısa: {len(review_text)} karakter")
                            continue  # Çok kısa yorumları atla
                            
                    except:
                        review_text = ""
                    
                    # Review objesi oluştur - timestamp ile
                    review = Review(
                        reviewer_name=reviewer_name,
                        review_text=review_text,
                        rating=str(rating) if rating > 0 else "0",
                        date=date_text,
                        timestamp=timestamp,
                        time_category=time_category,
                        is_new=True
                    )
                    
                    reviews.append(review)
                    
                    # Hedef kontrolü
                    if (text_review_count >= target_text_reviews and 
                        total_ratings_count >= target_ratings):
                        print(f"   🎯 Hedefler ulaşıldı! Metin: {text_review_count}, Rating: {total_ratings_count}")
                        break
                        
                except Exception as e:
                    print(f"   ❌ Container işleme hatası: {e}")
                    continue
            
            print(f"\n🎉 Veri toplama tamamlandı!")
            print(f"📝 Metin yorumları: {text_review_count}")
            print(f"📊 Toplam puanlama: {total_ratings_count}")
            
            # Veritabanına kaydet
            if reviews:
                print(f"\n💾 Veritabanına kaydediliyor...")
                
                # Session bilgileri
                session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
                
                # Session kaydı
                session_data = {
                    'session_id': session_id,
                    'business_name': business_name,
                    'business_url': business_url or search_query,
                    'total_reviews': len(reviews),
                    'text_reviews': text_review_count,
                    'ratings_count': total_ratings_count,
                    'average_rating': round(ratings_sum / total_ratings_count, 2) if total_ratings_count > 0 else 0,
                    'scrape_date': datetime.now().isoformat(),
                    'platform': 'Google Maps'
                }
                
                self.db.add_session(session_data)
                print(f"✅ Scrape session kaydedildi: {session_id}")
                
                # Yorumları kaydet
                saved_count = 0
                for review in reviews:
                    review_data = {
                        'session_id': session_id,
                        'business_name': business_name,
                        'reviewer_name': review.reviewer_name,
                        'review_text': review.review_text,
                        'rating': review.rating,
                        'review_date': review.date,
                        'timestamp_parsed': review.timestamp.isoformat() if review.timestamp else None,
                        'time_category': review.time_category,
                        'scrape_date': datetime.now().isoformat(),
                        'platform': review.platform,
                        'is_new': review.is_new
                    }
                    
                    if self.db.add_review(review_data):
                        saved_count += 1
                
                print(f"✅ {saved_count} yorum veritabanına kaydedildi")
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "total_reviews": len(reviews),
                    "text_reviews": text_review_count,
                    "ratings_count": total_ratings_count,
                    "average_rating": round(ratings_sum / total_ratings_count, 2) if total_ratings_count > 0 else 0,
                    "business_name": business_name
                }
            else:
                return {"success": False, "error": "Hiç yorum toplanmadı"}
                
        except Exception as e:
            print(f"❌ Yorum çekme hatası: {e}")
            return {"success": False, "error": str(e)}

    def run_interactive_mode(self):
        """Interaktif mod - kullanıcıdan input al"""
        print("🚀 Veritabanı Entegrasyonlu Google Maps Review Scraper Başlıyor...")
        
        # İşletme bilgileri
        business_name = input("📍 İşletme adı: ").strip()
        if not business_name:
            business_name = "İstanbul Sabiha Gökçen Uluslararası Havalimanı"
        
        print(f"📍 İşletme: {business_name}")
        
        # URL veya arama
        url_input = input("🔗 Direkt Google Maps URL'si (boş bırakırsanız arama yaparım): ").strip()
        
        if url_input:
            business_url = url_input
            search_query = ""
            print(f"🔗 Direkt URL kullanılıyor: {business_url[:50]}...")
        else:
            business_url = ""
            search_query = business_name
            print(f"🔍 Arama yapılacak: {search_query}")
        
        # Hedef sayılar
        try:
            target_text = int(input("📝 Kaç metin yorumu hedefliyorsunuz? (varsayılan: 30): ").strip() or "30")
            target_ratings = int(input("📊 Kaç puanlama hedefliyorsunuz? (varsayılan: 50): ").strip() or "50")
        except:
            target_text = 30
            target_ratings = 50
        
        print(f"📊 Hedef: {target_text} metin yorumu + {target_ratings} puanlama")
        print("=" * 60)
        
        try:
            # Scraping işlemi
            result = self.extract_reviews_with_database(
                business_name=business_name,
                business_url=business_url,
                search_query=search_query,
                target_text_reviews=target_text,
                target_ratings=target_ratings
            )
            
            if result["success"]:
                print(f"\n✅ İşlem tamamlandı!")
                print(f"📊 Metin yorumları: {result['text_reviews']}")
                print(f"📈 Toplam puanlama: {result['ratings_count']}")
                print(f"🎯 Başarı oranı: %{(result['text_reviews'] / target_text * 100):.1f}")
                print(f"📁 Session ID: {result['session_id']}")
            else:
                print(f"❌ Hata: {result.get('error', 'Bilinmeyen hata')}")
                
        except KeyboardInterrupt:
            print("\n⏹️ İşlem kullanıcı tarafından durduruldu")
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}")
        finally:
            self.close_driver()

if __name__ == "__main__":
    # Streamlit ile GUI başlat
    import streamlit as st
    
    st.set_page_config(
        page_title="Google Maps Review Scraper",
        page_icon="🗺️",
        layout="wide"
    )
    
    st.title("🗺️ Google Maps Review Scraper")
    st.write("Veritabanı entegrasyonlu Google Maps yorum toplayıcı")
    
    # Varsayılan değerler
    default_business = "İstanbul Sabiha Gökçen Uluslararası Havalimanı"
    default_url = "https://www.google.com/maps/place/%C4%B0stanbul+Sabiha+G%C3%B6k%C3%A7en+Uluslararas%C4%B1+Havaliman%C4%B1/@40.9066532,29.3107929,16z/data=!4m8!3m7!1s0x14cadbcbf424a153:0xacefca4d8098da74!8m2!3d40.8944747!4d29.3130928!9m1!1b1!16zL20vMDJnbmhx?entry=ttu&g_ep=EgoyMDI1MDkwMy4wIKXMDSoASAFQAw%3D%3D"
    
    with st.form("scraper_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            business_name = st.text_input("📍 İşletme Adı", value=default_business)
            business_url = st.text_input("🔗 Google Maps URL (opsiyonel)", value=default_url)
        
        with col2:
            target_text = st.number_input("📝 Hedef Metin Yorumu", min_value=1, max_value=100, value=30)
            target_ratings = st.number_input("📊 Hedef Puanlama", min_value=1, max_value=200, value=50)
        
        submitted = st.form_submit_button("🚀 Scraping Başlat", type="primary")
    
    if submitted:
        if business_name:
            st.info(f"🎯 Hedef: {target_text} metin yorumu + {target_ratings} puanlama")
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Scraper başlat
                scraper = DatabaseGoogleMapsScraper(headless=True)
                
                status_text.text("🦊 Firefox başlatılıyor...")
                progress_bar.progress(10)
                
                # Scraping işlemi
                status_text.text("🔍 Yorumlar toplanıyor...")
                progress_bar.progress(30)
                
                result = scraper.extract_reviews_with_database(
                    business_name=business_name,
                    business_url=business_url if business_url else "",
                    search_query=business_name if not business_url else "",
                    target_text_reviews=target_text,
                    target_ratings=target_ratings
                )
                
                progress_bar.progress(100)
                
                if result["success"]:
                    st.success("✅ İşlem başarıyla tamamlandı!")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("📝 Metin Yorumları", result['text_reviews'])
                    with col2:
                        st.metric("📊 Toplam Puanlama", result['ratings_count'])
                    with col3:
                        st.metric("⭐ Ortalama Puan", f"{result['average_rating']:.1f}")
                    with col4:
                        success_rate = (result['text_reviews'] / target_text * 100)
                        st.metric("🎯 Başarı Oranı", f"%{success_rate:.1f}")
                    
                    st.info(f"📁 Session ID: `{result['session_id']}`")
                    st.info("📊 Verileri görmek için dashboard'u kullanabilirsiniz: `streamlit run database_dashboard.py`")
                    
                else:
                    st.error(f"❌ Hata: {result.get('error', 'Bilinmeyen hata')}")
                    
            except Exception as e:
                st.error(f"❌ Beklenmeyen hata: {str(e)}")
            finally:
                status_text.text("🔒 Tarayıcı kapatılıyor...")
                try:
                    scraper.close_driver()
                except:
                    pass
                status_text.text("✅ İşlem tamamlandı!")
        else:
            st.warning("⚠️ Lütfen işletme adını girin!")
