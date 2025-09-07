from database_scraper import DatabaseGoogleMapsScraper
import time

# Test için debug scripti
scraper = DatabaseGoogleMapsScraper('main_reviews.db')

try:
    # İstanbul Havalimanı Starbucks
    url = 'https://www.google.com/maps/place/Starbucks+Coffee/@41.2754219,28.7429885,17z/data=!3m1!4b1!4m6!3m5!1s0x14b572ac6b2bdba3:0xd35ab7ed82f0c63a!8m2!3d41.2754179!4d28.7455634!16s%2Fg%2F11t28_jz0x?entry=ttu&g_ep=EgoyMDI0MTIxOC4wIKXMDSoASAFQAw%3D%3D'
    
    print('🚀 DEBUG: Tablari arastiriyoruz...')
    
    # Firefox'u başlat
    scraper.setup_driver()  # Driver'ı kur
    # Driver zaten scraper.driver'a atanmış olmalı
    scraper.driver.get(url)
    time.sleep(5)
    
    print('📋 Sayfa yuklendi, tablari kontrol ediliyor...')
    
    # Tüm button elementlerini kontrol et
    buttons = scraper.driver.find_elements("tag name", "button")
    print(f'🔍 Toplam {len(buttons)} buton bulundu')
    
    tab_buttons = scraper.driver.find_elements("css selector", 'button[role="tab"]')
    print(f'📑 {len(tab_buttons)} adet role="tab" bulundu')
    
    for i, tab in enumerate(tab_buttons[:10]):  # İlk 10 tab'ı kontrol et
        aria_label = tab.get_attribute('aria-label') or 'Boş'
        text_content = tab.text or 'Boş'
        print(f'   Tab {i+1}: aria="{aria_label[:50]}" text="{text_content[:30]}"')
    
    # reviews/yorum içeren tüm elementleri ara
    print('\n🔍 Review/Yorum içeren elementler:')
    all_elements = scraper.driver.find_elements("css selector", "*")
    
    review_count = 0
    for elem in all_elements[:100]:  # İlk 100 elementi kontrol et
        try:
            aria = (elem.get_attribute('aria-label') or '').lower()
            text = (elem.text or '').lower()
            if ('review' in aria or 'yorum' in aria or 
                'review' in text or 'yorum' in text):
                tag_name = elem.tag_name
                print(f'   {tag_name}: aria="{aria[:40]}" text="{text[:30]}"')
                review_count += 1
                
                if review_count >= 10:  # İlk 10 tanesi yeterli
                    break
        except:
            continue
    
    print(f'\n✅ Debug tamamlandı. {review_count} review elementi bulundu.')
    
except Exception as e:
    print(f'❌ Hata: {e}')
    import traceback
    traceback.print_exc()
    
finally:
    try:
        if hasattr(scraper, 'driver'):
            scraper.driver.quit()
    except:
        pass
