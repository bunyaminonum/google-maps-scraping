"""
Firefox için geliştirilmiş Google Maps Review Scraper Test
HTML analizi sonrası düzeltilmiş version
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

def setup_firefox_driver():
    """Firefox WebDriver'ı kurar"""
    print("🦊 Firefox WebDriver kuruluyor...")
    
    firefox_options = Options()
    firefox_options.add_argument("--width=1920")
    firefox_options.add_argument("--height=1080")
    firefox_options.set_preference("general.useragent.override", 
                                 "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
    
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=firefox_options)
    
    print("✅ Firefox başlatıldı")
    return driver

def search_business(driver, business_name, location=""):
    """İşletmeyi Google Maps'te arar"""
    print(f"🔍 Aranıyor: {business_name} {location}")
    
    try:
        # Google Maps'e git
        driver.get("https://www.google.com/maps")
        time.sleep(3)
        
        # Arama kutusunu bul
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "searchboxinput"))
        )
        
        # Aramayı yap
        search_query = f"{business_name} {location}".strip()
        search_box.clear()
        search_box.send_keys(search_query)
        
        # Arama butonuna tıkla
        search_button = driver.find_element(By.ID, "searchbox-searchbutton")
        search_button.click()
        
        print("🔍 Arama yapıldı, sonuçlar bekleniyor...")
        time.sleep(5)
        
        return True
        
    except Exception as e:
        print(f"❌ Arama hatası: {e}")
        return False

def click_first_result(driver):
    """İlk arama sonucuna tıklar"""
    print("🎯 İlk sonuca tıklanıyor...")
    
    try:
        # Çeşitli selector'ları dene
        selectors = [
            "a[data-value='Directions']",
            ".hfpxzc",
            "[data-result-index='1']",
            ".Nv2PK",
            "div[role='main'] a"
        ]
        
        for selector in selectors:
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                element.click()
                print(f"✅ Tıklandı: {selector}")
                time.sleep(3)
                return True
            except:
                continue
        
        # Alternatif: Koordinat ile tıklama
        try:
            results_area = driver.find_element(By.CSS_SELECTOR, "[role='main']")
            driver.execute_script("arguments[0].children[0].click();", results_area)
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

def navigate_to_reviews(driver):
    """Yorumlar sekmesine gider"""
    print("📝 Yorumlar sekmesine gidiliyor...")
    
    try:
        # Firefox için geliştirilmiş selector'lar
        tab_selectors = [
            "button[role='tab'][aria-label*='yorumlar' i]",
            "button[role='tab'][aria-label*='reviews' i]", 
            "button[data-tab-index='2']",
            "button[data-tab-index='1']",
            ".aLPB6c",
            ".T65V3d", 
            "button:contains('Yorumlar')",
            "button:contains('Reviews')"
        ]
        
        for selector in tab_selectors:
            try:
                print(f"🔍 Deneniyor: {selector}")
                
                if ":contains(" in selector:
                    # JavaScript ile contains arama
                    elements = driver.execute_script("""
                        return Array.from(document.querySelectorAll('button')).filter(
                            el => el.textContent.toLowerCase().includes('yorumlar') || 
                                  el.textContent.toLowerCase().includes('reviews')
                        );
                    """)
                    
                    if elements:
                        driver.execute_script("arguments[0].click();", elements[0])
                        print(f"✅ JavaScript ile yorumlar tab'ı bulundu ve tıklandı")
                        time.sleep(3)
                        return True
                else:
                    element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    element.click()
                    print(f"✅ Yorumlar tab'ı tıklandı: {selector}")
                    time.sleep(3)
                    return True
                    
            except Exception as inner_e:
                print(f"   ❌ Başarısız: {inner_e}")
                continue
        
        # Son çare: Tüm tab'ları listele ve manuel seç
        print("🔧 Tüm tab'lar listeleniyor...")
        try:
            tabs = driver.find_elements(By.CSS_SELECTOR, "button[role='tab'], .tab-strip button, [data-tab-index]")
            print(f"Bulunan tab sayısı: {len(tabs)}")
            
            for i, tab in enumerate(tabs):
                try:
                    tab_text = tab.text or tab.get_attribute("aria-label") or ""
                    print(f"Tab {i+1}: '{tab_text}'")
                    
                    if any(word in tab_text.lower() for word in ['yorumlar', 'reviews', 'review']):
                        tab.click()
                        print(f"✅ Manuel olarak yorumlar tab'ı tıklandı")
                        time.sleep(3)
                        return True
                        
                except Exception as tab_error:
                    print(f"Tab {i+1} hatası: {tab_error}")
                    continue
        except:
            pass
        
        print("❌ Yorumlar sekmesi bulunamadı")
        return False
        
    except Exception as e:
        print(f"❌ Yorumlar sekmesi hatası: {e}")
        return False

def extract_reviews_info(driver):
    """Yorumlar sayfasındaki bilgileri çıkarır"""
    print("📊 Yorumlar bilgisi çıkarılıyor...")
    
    try:
        # Sayfa HTML'ini al
        page_source = driver.page_source
        print(f"📄 Sayfa boyutu: {len(page_source)} karakter")
        
        # Mevcut URL'yi kontrol et
        current_url = driver.current_url
        print(f"🌐 Mevcut URL: {current_url}")
        
        # Yorumlarla ilgili elementleri ara
        review_selectors = [
            ".jftiEf.fontBodyMedium",  # HTML'de gözlenen ana selector
            ".aLPB6c",                # Tab selector
            ".T65V3d",                # Alternatif selector
            "[data-review-id]",        # Review ID'si olan elementler
            ".wiI7pd",                # Yorum metni
            ".d4r55.fontTitleMedium"   # Yorumcu adı
        ]
        
        found_elements = {}
        
        for selector in review_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                found_elements[selector] = len(elements)
                print(f"🔍 {selector}: {len(elements)} element")
                
                # İlk elementi detaylandır
                if elements:
                    first_element = elements[0]
                    element_text = first_element.text[:100] if first_element.text else "[metin yok]"
                    element_html = first_element.get_attribute("outerHTML")[:200] if first_element else "[HTML yok]"
                    print(f"   📝 İlk element metni: {element_text}")
                    print(f"   🏷️ İlk element HTML: {element_html}")
                    
            except Exception as selector_error:
                found_elements[selector] = f"HATA: {selector_error}"
                print(f"❌ {selector} hatası: {selector_error}")
        
        # JavaScript ile yorumları ara
        print("\n🔧 JavaScript ile yorum arama...")
        try:
            js_results = driver.execute_script("""
                // Yorumlarla ilgili tüm elementleri ara
                const reviewKeywords = ['review', 'yorum', 'rating', 'star'];
                const allElements = document.querySelectorAll('*');
                let foundReviews = [];
                
                for (let el of allElements) {
                    const text = el.textContent || '';
                    const className = el.className || '';
                    const id = el.id || '';
                    
                    for (let keyword of reviewKeywords) {
                        if (text.toLowerCase().includes(keyword) || 
                            className.toLowerCase().includes(keyword) ||
                            id.toLowerCase().includes(keyword)) {
                            foundReviews.push({
                                tag: el.tagName,
                                className: className,
                                id: id,
                                text: text.substring(0, 100)
                            });
                            break;
                        }
                    }
                }
                
                return foundReviews.slice(0, 10); // İlk 10 sonuç
            """)
            
            print(f"🎯 JavaScript ile bulunan yorumla ilgili element sayısı: {len(js_results)}")
            for i, result in enumerate(js_results[:5]):
                print(f"   {i+1}. {result['tag']}.{result['className']} - {result['text']}")
                
        except Exception as js_error:
            print(f"❌ JavaScript arama hatası: {js_error}")
        
        return found_elements
        
    except Exception as e:
        print(f"❌ Bilgi çıkarma hatası: {e}")
        return {}

def test_google_maps_firefox():
    """Ana test fonksiyonu"""
    print("🚀 Firefox Google Maps Review Scraper Test Başlıyor...")
    print("=" * 60)
    
    driver = None
    
    try:
        # 1. Firefox'u başlat
        driver = setup_firefox_driver()
        
        # 2. İşletme ara
        business_name = "Starbucks Zorlu Center"
        location = "İstanbul"
        
        if search_business(driver, business_name, location):
            print("✅ Arama başarılı")
            
            # 3. İlk sonuca tıkla
            if click_first_result(driver):
                print("✅ İşletme seçildi")
                
                # 4. Yorumlar sekmesine git
                if navigate_to_reviews(driver):
                    print("✅ Yorumlar sekmesi açıldı")
                    
                    # 5. Yorumları analiz et
                    review_info = extract_reviews_info(driver)
                    
                    if review_info:
                        print("\n📈 SONUÇLAR:")
                        print("=" * 40)
                        for selector, count in review_info.items():
                            print(f"{selector}: {count}")
                    else:
                        print("❌ Yorum bilgisi çıkarılamadı")
                else:
                    print("❌ Yorumlar sekmesi açılamadı")
                    
                    # Debug için sayfa durumunu kontrol et
                    print("\n🔧 DEBUG: Sayfa durumu...")
                    try:
                        tabs = driver.find_elements(By.CSS_SELECTOR, "button")
                        print(f"Bulunan buton sayısı: {len(tabs)}")
                        
                        for i, button in enumerate(tabs[:10]):
                            try:
                                button_text = button.text or button.get_attribute("aria-label") or ""
                                if button_text:
                                    print(f"Buton {i+1}: {button_text}")
                            except:
                                pass
                    except:
                        pass
            else:
                print("❌ İlk sonuca tıklanamadı")
        else:
            print("❌ Arama başarısız")
        
        # Test tamamlanana kadar bekle
        input("\n⏸️ Test tamamlandı. Tarayıcıyı kapatmak için Enter'a basın...")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"\n❌ Test hatası: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
            print("🔒 Firefox kapatıldı")
        
        print("\n✅ Test tamamlandı!")

if __name__ == "__main__":
    test_google_maps_firefox()
