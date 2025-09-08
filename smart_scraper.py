#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 Akıllı Google Maps Scraper - Ban-Safe Hızlandırma
Multiple strategies for faster, safer scraping
"""

import asyncio
import time
import random
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from dataclasses import dataclass
from typing import List, Optional
import queue
import json

@dataclass
class ScrapingTask:
    """Scraping görevi"""
    business_name: str
    business_url: str
    target_reviews: int = 50
    target_text_reviews: int = 10
    priority: int = 1  # 1=yüksek, 5=düşük

class SmartGoogleMapsScraper:
    """Akıllı, Ban-Safe Google Maps Scraper"""
    
    def __init__(self, max_workers=3, base_delay=2.0, randomize_delay=True):
        """
        Args:
            max_workers: Maksimum eşzamanlı browser sayısı (Google için 2-3 ideal)
            base_delay: Temel gecikme süresi (saniye)
            randomize_delay: Rastgele gecikme ekle
        """
        self.max_workers = max_workers
        self.base_delay = base_delay
        self.randomize_delay = randomize_delay
        self.request_times = []  # Rate limiting için
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0", 
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"
        ]
        
    def create_safe_driver(self, worker_id: int):
        """Ban-safe browser oluştur"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-web-security")
        
        # Rastgele User-Agent
        user_agent = random.choice(self.user_agents)
        options.add_argument(f"--user-agent={user_agent}")
        
        # Viewport rastgeleleştir
        widths = [1366, 1920, 1440, 1536]
        heights = [768, 1080, 900, 864]
        width = random.choice(widths)
        height = random.choice(heights)
        options.add_argument(f"--window-size={width},{height}")
        
        # Worker'a özel profile
        profile_path = f"/tmp/firefox_profile_{worker_id}"
        options.add_argument(f"--profile={profile_path}")
        
        driver = webdriver.Firefox(options=options)
        
        # Navigator özelliklerini gizle
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        return driver
    
    def smart_delay(self, operation_type="default"):
        """Akıllı gecikme sistemi"""
        delays = {
            "page_load": (3.0, 6.0),
            "scroll": (1.5, 3.0), 
            "click": (1.0, 2.5),
            "text_input": (0.5, 1.5),
            "default": (2.0, 4.0)
        }
        
        min_delay, max_delay = delays.get(operation_type, delays["default"])
        
        if self.randomize_delay:
            delay = random.uniform(min_delay, max_delay)
        else:
            delay = min_delay
            
        # Rate limiting kontrolü
        now = time.time()
        self.request_times = [t for t in self.request_times if now - t < 60]  # Son 1 dakika
        
        if len(self.request_times) > 20:  # Dakikada 20'den fazla istek
            delay *= 2.0  # Gecikmeyi artır
            
        self.request_times.append(now)
        time.sleep(delay)
        
        return delay
    
    def scrape_single_business(self, task: ScrapingTask, worker_id: int):
        """Tek işletme için güvenli scraping"""
        driver = None
        try:
            print(f"🔧 Worker {worker_id}: {task.business_name} işleniyor...")
            
            # Browser oluştur
            driver = self.create_safe_driver(worker_id)
            self.smart_delay("page_load")
            
            # URL'ye git
            driver.get(task.business_url)
            self.smart_delay("page_load")
            
            # Reviews tab'ını bul ve tıkla
            wait = WebDriverWait(driver, 10)
            reviews_tab = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[role='tab'][aria-label*='yorumlar' i]"))
            )
            reviews_tab.click()
            self.smart_delay("click")
            
            # En yeni yorumları seç
            try:
                dropdown = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label*='En alakalı']"))
                )
                dropdown.click()
                self.smart_delay("click")
                
                newest_option = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'En yeni')]"))
                )
                newest_option.click()
                self.smart_delay("click")
            except:
                print(f"⚠️ Worker {worker_id}: Dropdown değiştirilemedi")
            
            # Akıllı scroll - hedefe ulaşana kadar
            reviews_collected = 0
            scroll_attempts = 0
            max_scrolls = task.target_reviews // 10 + 5
            
            while reviews_collected < task.target_reviews and scroll_attempts < max_scrolls:
                # Mevcut yorum sayısını kontrol et
                review_containers = driver.find_elements(By.CSS_SELECTOR, "[data-review-id]")
                reviews_collected = len(review_containers)
                
                if reviews_collected >= task.target_reviews:
                    break
                
                # Scroll yap
                scrollable = driver.find_element(By.CSS_SELECTOR, ".m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde")
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)
                
                self.smart_delay("scroll")
                scroll_attempts += 1
                
                print(f"📊 Worker {worker_id}: {reviews_collected}/{task.target_reviews} yorum yüklendi")
            
            # Yorumları topla (basit sürüm - detay extractiona gerek yok şimdilik)
            final_containers = driver.find_elements(By.CSS_SELECTOR, "[data-review-id]")
            
            print(f"✅ Worker {worker_id}: {task.business_name} tamamlandı - {len(final_containers)} yorum")
            
            return {
                "business_name": task.business_name,
                "worker_id": worker_id,
                "reviews_found": len(final_containers),
                "success": True
            }
            
        except Exception as e:
            print(f"❌ Worker {worker_id}: {task.business_name} hatası - {e}")
            return {
                "business_name": task.business_name,
                "worker_id": worker_id,
                "error": str(e),
                "success": False
            }
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def parallel_scrape(self, tasks: List[ScrapingTask]):
        """Paralel scraping - Ana fonksiyon"""
        print(f"🚀 Paralel Scraping Başlıyor:")
        print(f"   📋 İşletme sayısı: {len(tasks)}")
        print(f"   🔧 Worker sayısı: {self.max_workers}")
        print(f"   ⏱️ Base delay: {self.base_delay}s")
        print("="*60)
        
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Task'ları worker'lara dağıt
            future_to_task = {}
            
            for i, task in enumerate(tasks):
                worker_id = (i % self.max_workers) + 1
                future = executor.submit(self.scrape_single_business, task, worker_id)
                future_to_task[future] = task
            
            # Sonuçları topla
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result["success"]:
                        print(f"✅ {result['business_name']}: {result['reviews_found']} yorum")
                    else:
                        print(f"❌ {result['business_name']}: {result.get('error', 'Bilinmeyen hata')}")
                        
                except Exception as e:
                    print(f"❌ {task.business_name}: Future hatası - {e}")
                    results.append({
                        "business_name": task.business_name,
                        "error": str(e),
                        "success": False
                    })
        
        return results

def demo_parallel_scraping():
    """Paralel scraping demo"""
    print("🎯 Paralel Google Maps Scraping Demo")
    print("="*50)
    
    # Test için işletmeler
    test_businesses = [
        ScrapingTask(
            business_name="İstanbul Havalimanı",
            business_url="https://www.google.com/maps/place/İstanbul+Havalimanı",
            target_reviews=30
        ),
        ScrapingTask(
            business_name="Sabiha Gökçen Havalimanı", 
            business_url="https://www.google.com/maps/place/İstanbul+Sabiha+Gökçen+Uluslararası+Havalimanı",
            target_reviews=30
        ),
        ScrapingTask(
            business_name="Starbucks Zorlu Center",
            business_url="https://www.google.com/maps/place/Starbucks",
            target_reviews=25
        )
    ]
    
    # Paralel scraper oluştur (konservatiif ayarlar)
    scraper = SmartGoogleMapsScraper(
        max_workers=2,  # Güvenli için 2 worker
        base_delay=3.0,  # 3 saniye base delay
        randomize_delay=True
    )
    
    # Scraping başlat
    start_time = time.time()
    results = scraper.parallel_scrape(test_businesses)
    end_time = time.time()
    
    # Sonuçları göster
    print("\n" + "="*60)
    print("📊 PARALEL SCRAPING SONUÇLARI:")
    print("="*60)
    
    successful = 0
    total_reviews = 0
    
    for result in results:
        if result["success"]:
            successful += 1
            total_reviews += result["reviews_found"]
            print(f"✅ {result['business_name']}: {result['reviews_found']} yorum")
        else:
            print(f"❌ {result['business_name']}: HATA")
    
    print(f"\n📈 ÖZET:")
    print(f"   ⏱️ Toplam süre: {end_time - start_time:.1f} saniye")
    print(f"   ✅ Başarılı: {successful}/{len(test_businesses)}")
    print(f"   📊 Toplam yorum: {total_reviews}")
    print(f"   🚀 Yorum/dakika: {(total_reviews / (end_time - start_time)) * 60:.1f}")

if __name__ == "__main__":
    demo_parallel_scraping()
