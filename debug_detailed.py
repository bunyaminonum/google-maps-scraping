from database_scraper import DatabaseGoogleMapsScraper
import time

# Test için debug scripti - kapsamlı
scraper = DatabaseGoogleMapsScraper('main_reviews.db')

try:
    # İstanbul Havalimanı Starbucks
    url = 'https://www.google.com/maps/place/Starbucks+Coffee/@41.2754219,28.7429885,17z/data=!3m1!4b1!4m6!3m5!1s0x14b572ac6b2bdba3:0xd35ab7ed82f0c63a!8m2!3d41.2754179!4d28.7455634!16s%2Fg%2F11t28_jz0x?entry=ttu&g_ep=EgoyMDI0MTIxOC4wIKXMDSoASAFQAw%3D%3D'
    
    print('🚀 DEBUG: Kapsamli tab arastirmasi...')
    
    # Firefox'u başlat
    scraper.setup_driver()  # Driver'ı kur
    scraper.driver.get(url)
    time.sleep(8)  # Daha uzun bekle
    
    print('📋 Sayfa yuklendi, tum elementleri kontrol ediliyor...')
    
    # HTML source'ta reviews/yorumlar kelimelerini ara
    page_source = scraper.driver.page_source.lower()
    
    print(f'🔍 Sayfa kaynak kodunda:')
    print(f'   - "reviews" geciyor mu: {"reviews" in page_source}')
    print(f'   - "yorum" geciyor mu: {"yorum" in page_source}')
    print(f'   - "review" geciyor mu: {"review" in page_source}')
    
    # Tüm click edilebilir elementleri kontrol et
    clickable_elements = []
    
    # Çeşitli click edilebilir selector'lar
    selectors = [
        'button',
        '[role="button"]', 
        'a',
        '[role="tab"]',
        'div[data-tab]',
        'div[jsaction]',
        '.hh2c6',  # Google Maps tab container'ı
        '[data-value]'
    ]
    
    for selector in selectors:
        try:
            elements = scraper.driver.find_elements("css selector", selector)
            print(f'🔍 {selector}: {len(elements)} adet')
            
            # İlk birkaçını kontrol et
            for i, elem in enumerate(elements[:5]):
                try:
                    text = (elem.text or '').strip()[:50]
                    aria = (elem.get_attribute('aria-label') or '').strip()[:50]
                    data_value = elem.get_attribute('data-value') or ''
                    
                    if (text and ('review' in text.lower() or 'yorum' in text.lower() or 
                                 'comment' in text.lower() or 'rating' in text.lower())) or \
                       (aria and ('review' in aria.lower() or 'yorum' in aria.lower() or 
                                 'comment' in aria.lower() or 'rating' in aria.lower())):
                        
                        print(f'   -> Element {i+1}: text="{text}" aria="{aria}" data-value="{data_value}"')
                        clickable_elements.append((elem, text, aria))
                        
                except:
                    continue
                    
        except Exception as e:
            print(f'   {selector} hatası: {e}')
    
    print(f'\n📊 Toplam {len(clickable_elements)} potansiyel click elementı bulundu')
    
    # Eğer hiçbir review elementi bulunamadıysa, tüm visible text'leri kontrol et
    if len(clickable_elements) == 0:
        print('\n🔍 Hiç review elementi bulunamadı. Tüm görünür metinleri kontrol ediliyor...')
        
        # Sayfadaki tüm görünür metinleri al
        all_text_elements = scraper.driver.find_elements("xpath", "//*[text()]")
        
        review_texts = []
        for elem in all_text_elements[:50]:  # İlk 50 text elementı
            try:
                text = elem.text.strip()
                if text and len(text) > 5:
                    if any(word in text.lower() for word in ['review', 'yorum', 'rating', 'star', 'comment']):
                        review_texts.append(text[:100])
                        
            except:
                continue
        
        print(f'📝 Review/yorum içeren {len(review_texts)} metin bulundu:')
        for i, text in enumerate(review_texts[:10]):
            print(f'   Text {i+1}: "{text}"')
    
    print('\n✅ Kapsamli debug tamamlandi.')
    
except Exception as e:
    print(f'❌ Hata: {e}')
    import traceback
    traceback.print_exc()
    
finally:
    try:
        if hasattr(scraper, 'driver') and scraper.driver:
            scraper.driver.quit()
    except:
        pass
