"""
Chrome Test V2 - Daha robust selenium options ile
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def chrome_test_v2():
    """Chrome ile gelişmiş test"""
    
    print("🚀 Chrome Test V2 - Gelişmiş Ayarlar")
    print("=" * 50)
    
    # Chrome ayarları - bot detection'ı azaltacak şekilde
    chrome_options = Options()
    
    # Temel ayarlar
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    
    # Bot detection'ı azalt
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # Pencere boyutu
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = None
    try:
        # Chrome başlat
        print("🚀 Chrome başlatılıyor...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # WebDriver script'ini gizle
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        wait = WebDriverWait(driver, 15)
        print("✅ Chrome başlatıldı")
        
        # Direkt Google Maps'e git
        maps_url = "https://www.google.com/maps/search/Maxx+Royal+Kemer+Resort+Antalya"
        print(f"🗺️ Google Maps URL'sine gidiliyor...")
        driver.get(maps_url)
        time.sleep(5)
        
        # Sayfa bilgilerini al
        current_url = driver.current_url
        page_title = driver.title
        print(f"📍 Mevcut URL: {current_url}")
        print(f"📄 Sayfa başlığı: {page_title}")
        
        # İşletme sonuçlarını ara
        print("\n🎯 İşletme sonuçları aranıyor...")
        
        selectors_to_try = [
            "[role='article']",
            ".hfpxzc",
            ".Nv2PK",
            ".qBF1Pd",
            "a[data-result-index]",
            ".VkpGBb",
            "h3",
            ".qjESne"
        ]
        
        first_business = None
        for selector in selectors_to_try:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                print(f"📍 {selector}: {len(elements)} element bulundu")
                
                for i, elem in enumerate(elements[:5]):  # İlk 5'ini kontrol et
                    try:
                        if elem.is_displayed():
                            text = elem.text.strip()[:50]
                            if text:
                                print(f"   [{i+1}] Görünür: {text}...")
                                if not first_business and len(text) > 5:
                                    first_business = elem
                                    print(f"   🎯 Bu element seçildi!")
                                    break
                    except:
                        continue
                
                if first_business:
                    break
                    
            except Exception as e:
                print(f"⚠️ {selector} hatası: {e}")
        
        if first_business:
            print("\n✅ İşletme bulundu, tıklanıyor...")
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", first_business)
                time.sleep(2)
                first_business.click()
                print("✅ İşletmeye tıklandı")
                time.sleep(5)
                
                # Yorumlar sekmesini ara
                print("\n📝 Yorumlar sekmesi aranıyor...")
                
                tab_selectors = [
                    "button[role='tab']",
                    ".hh2c6",
                    "[data-tab-index='2']",
                    "button[aria-label*='review']",
                    "button[aria-label*='Review']",
                    ".G7m0Af"  # Active tab class
                ]
                
                all_tabs = []
                for selector in tab_selectors:
                    try:
                        tabs = driver.find_elements(By.CSS_SELECTOR, selector)
                        print(f"🔍 {selector}: {len(tabs)} tab bulundu")
                        all_tabs.extend(tabs)
                    except:
                        continue
                
                # Tüm tab'ları kontrol et
                reviews_tab = None
                for i, tab in enumerate(all_tabs):
                    try:
                        if tab.is_displayed():
                            tab_text = tab.text or tab.get_attribute("aria-label") or ""
                            tab_id = tab.get_attribute("data-tab-index") or ""
                            print(f"   Tab {i+1}: '{tab_text}' (index: {tab_id})")
                            
                            if ("review" in tab_text.lower() or 
                                "yorum" in tab_text.lower() or 
                                tab_id == "2"):
                                reviews_tab = tab
                                print(f"   🎯 Reviews tab bulundu: '{tab_text}'")
                                break
                    except:
                        continue
                
                if reviews_tab:
                    print("✅ Reviews tab'a tıklanıyor...")
                    driver.execute_script("arguments[0].click();", reviews_tab)
                    time.sleep(5)
                    
                    # Yorumları ara
                    print("\n💬 Yorumlar aranıyor...")
                    
                    review_selectors = [
                        ".jftiEf",
                        ".MyEned", 
                        "[data-review-id]",
                        ".gws-localreviews__google-review",
                        ".fontBodyMedium"
                    ]
                    
                    found_reviews = False
                    for selector in review_selectors:
                        try:
                            reviews = driver.find_elements(By.CSS_SELECTOR, selector)
                            if reviews:
                                print(f"✅ {selector}: {len(reviews)} yorum container bulundu")
                                
                                # İlk birkaç yorumu detaylı analiz et
                                for i, review in enumerate(reviews[:3]):
                                    try:
                                        print(f"\n   📝 Yorum {i+1} analizi:")
                                        
                                        # Yorumcu adı için farklı selector'lar dene
                                        name = "Unknown"
                                        name_selectors = [".d4r55", ".fontTitleMedium", ".reviewer-name", ".author-name"]
                                        for name_sel in name_selectors:
                                            try:
                                                name_elem = review.find_element(By.CSS_SELECTOR, name_sel)
                                                if name_elem.text.strip():
                                                    name = name_elem.text.strip()
                                                    break
                                            except:
                                                continue
                                        
                                        # Yorum metni
                                        text = "No text"
                                        text_selectors = [".wiI7pd", ".review-text", ".MyEned"]
                                        for text_sel in text_selectors:
                                            try:
                                                text_elem = review.find_element(By.CSS_SELECTOR, text_sel)
                                                if text_elem.text.strip():
                                                    text = text_elem.text.strip()[:100]
                                                    break
                                            except:
                                                continue
                                        
                                        print(f"      👤 İsim: {name}")
                                        print(f"      💬 Metin: {text}...")
                                        
                                        if name != "Unknown" and text != "No text":
                                            found_reviews = True
                                        
                                    except Exception as e:
                                        print(f"      ⚠️ Parse hatası: {e}")
                                
                                if found_reviews:
                                    print(f"\n🎉 BAŞARI! {len(reviews)} yorum bulundu ve parse edildi")
                                    break
                                else:
                                    print(f"⚠️ Yorumlar bulundu ama parse edilemedi")
                                    
                        except Exception as e:
                            print(f"⚠️ {selector} hatası: {e}")
                    
                    if not found_reviews:
                        print("❌ Hiç geçerli yorum bulunamadı")
                        
                else:
                    print("❌ Reviews tab bulunamadı")
                    
            except Exception as click_error:
                print(f"❌ İşletmeye tıklama hatası: {click_error}")
                
        else:
            print("❌ İşletme bulunamadı")
        
        print("\n🎯 Test Özeti:")
        print("- Chrome başlatıldı ✅")
        print("- Google Maps'e gidildi ✅")
        print(f"- İşletme bulundu: {'✅' if first_business else '❌'}")
        print(f"- Yorumlar parse edildi: {'✅' if 'found_reviews' in locals() and found_reviews else '❌'}")
        
        print("\n⏸️ Test tamamlandı!")
        input("Chrome'u kapatmak için Enter'a basın...")
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            driver.quit()
            print("🔒 Chrome kapatıldı")

if __name__ == "__main__":
    chrome_test_v2()
