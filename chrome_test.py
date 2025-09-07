"""
Chrome Driver Test
"""

def test_chrome_driver():
    """Chrome driver'ın çalışıp çalışmadığını test et"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("🔧 Chrome driver test başlıyor...")
        
        # Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        
        # Service
        service = Service(ChromeDriverManager().install())
        
        # Driver başlat
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("✅ Chrome driver başlatıldı")
        
        # Basit test
        driver.get("https://www.google.com")
        title = driver.title
        print(f"✅ Google'a bağlanıldı: {title}")
        
        # Temizle
        driver.quit()
        print("✅ Chrome driver kapatıldı")
        
        return True
        
    except Exception as e:
        print(f"❌ Chrome driver hatası: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Chrome Driver Test")
    print("=" * 30)
    
    if test_chrome_driver():
        print("\n🎉 Chrome driver çalışıyor!")
        print("Ana scripti çalıştırmaya hazır.")
    else:
        print("\n❌ Chrome driver sorunu var.")
        print("Chrome tarayıcısının kurulu olduğundan emin olun.")
