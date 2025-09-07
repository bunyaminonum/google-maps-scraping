"""
Manuel Firefox Test - Kullanıcı kontrolü ile
"""

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
import time

def manual_test():
    """Manuel test - kullanıcı kontrolü ile"""
    
    print("🦊 Firefox Manuel Test")
    print("=" * 40)
    
    # Firefox ayarları
    firefox_options = Options()
    firefox_options.add_argument("--no-sandbox")
    firefox_options.set_preference("general.useragent.override", 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0")
    
    driver = None
    try:
        # Firefox başlat
        print("🚀 Firefox başlatılıyor...")
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=firefox_options)
        wait = WebDriverWait(driver, 10)
        
        print("✅ Firefox başlatıldı")
        
        # Google Maps'e git
        url = "https://www.google.com/maps/search/Maxx+Royal+Kemer+Resort+Antalya"
        print(f"🌐 URL'ye gidiliyor: {url}")
        driver.get(url)
        
        print("\n⏸️  MANUEL KONTROL:")
        print("1. Firefox penceresini kontrol edin")
        print("2. Google Maps açıldı mı?")
        print("3. Arama sonuçları görünüyor mu?")
        
        input("\n▶️  Enter'a basın devam etmek için...")
        
        # Sayfada ne var bakalım
        print("🔍 Sayfa analizi yapılıyor...")
        
        # Mevcut URL ve title
        current_url = driver.current_url
        page_title = driver.title
        print(f"📍 Mevcut URL: {current_url}")
        print(f"📄 Sayfa başlığı: {page_title}")
        
        # Sayfa üzerindeki önemli elementleri ara
        print("\n🎯 Element arama:")
        
        # Arama sonuçları
        try:
            results = driver.find_elements(By.CSS_SELECTOR, "[role='article']")
            print(f"📍 {len(results)} adet role='article' bulundu")
        except:
            print("❌ role='article' bulunamadı")
        
        # H3 başlıklar
        try:
            h3s = driver.find_elements(By.TAG_NAME, "h3")
            print(f"📝 {len(h3s)} adet h3 başlık bulundu")
            if h3s:
                print(f"   İlk h3: {h3s[0].text[:50]}...")
        except:
            print("❌ h3 bulunamadı")
        
        # Clickable elementler
        clickable_selectors = [
            "div.hfpxzc",
            ".Nv2PK", 
            ".qBF1Pd",
            "a[data-result-index]",
            ".VkpGBb"
        ]
        
        for selector in clickable_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ {selector}: {len(elements)} adet")
                    # İlk elementi test et
                    if elements[0].is_displayed():
                        print(f"   Görünür: Evet, Text: {elements[0].text[:30]}...")
                    else:
                        print(f"   Görünür: Hayır")
                else:
                    print(f"❌ {selector}: 0 adet")
            except Exception as e:
                print(f"⚠️ {selector}: Hata - {e}")
        
        print("\n⏸️  İkinci Manuel Kontrol:")
        print("Şimdi bir işletmeyi manuel olarak tıklayın")
        input("▶️  İşletmeyi tıkladıktan sonra Enter'a basın...")
        
        # Yorumlar sekmesini ara
        print("\n🔍 Yorumlar sekmesi aranıyor...")
        
        review_selectors = [
            "button[role='tab']",
            ".hh2c6",
            "[data-tab-index]",
            "button:contains('Reviews')",
            "button:contains('review')"
        ]
        
        for selector in review_selectors:
            try:
                if "contains" in selector:
                    continue  # XPath'i skip et
                    
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for i, elem in enumerate(elements):
                        if elem.is_displayed():
                            text = elem.text or elem.get_attribute("aria-label") or ""
                            print(f"✅ {selector}[{i}]: '{text[:50]}'")
                            if "review" in text.lower():
                                print(f"   🎯 Bu reviews tab olabilir!")
            except Exception as e:
                print(f"⚠️ {selector}: {e}")
        
        print("\n⏸️  Son kontrol:")
        print("Yorumlar sekmesini manuel olarak tıklayın")
        input("▶️  Yorumlar sekmesini tıkladıktan sonra Enter'a basın...")
        
        # Yorumları ara
        print("\n📝 Yorumlar aranıyor...")
        
        comment_selectors = [
            ".jftiEf",
            ".MyEned",
            ".d4r55",
            ".wiI7pd",
            "[data-review-id]"
        ]
        
        for selector in comment_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ {selector}: {len(elements)} adet")
                    for i, elem in enumerate(elements[:3]):  # İlk 3'ü göster
                        text = elem.text[:50] if elem.text else "Boş"
                        print(f"   [{i+1}]: {text}...")
                else:
                    print(f"❌ {selector}: 0 adet")
            except Exception as e:
                print(f"⚠️ {selector}: {e}")
        
        print("\n🎉 Manual test tamamlandı!")
        print("Bu bilgiler ile scraper'ı geliştirebiliriz")
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if driver:
            input("\n▶️  Firefox'u kapatmak için Enter'a basın...")
            driver.quit()
            print("🔒 Firefox kapatıldı")

if __name__ == "__main__":
    manual_test()
