#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🕒 Türkçe Zaman İfadeleri Parser
Google Maps'teki "X önce" ifadelerini gerçek timestamp'lere çevirir
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple

class TurkishTimeParser:
    """Türkçe zaman ifadelerini parse eder"""
    
    def __init__(self):
        # Zaman ifadeleri regex pattern'leri
        self.time_patterns = [
            # "X saat önce" pattern'i
            (r'(\d+)\s*saat\s*önce', 'hours'),
            # "X gün önce" pattern'i  
            (r'(\d+)\s*gün\s*önce', 'days'),
            # "X hafta önce" pattern'i
            (r'(\d+)\s*hafta\s*önce', 'weeks'),
            # "X ay önce" pattern'i
            (r'(\d+)\s*ay\s*önce', 'months'),
            # "X yıl önce" pattern'i
            (r'(\d+)\s*yıl\s*önce', 'years'),
            # Tekil versiyonlar
            (r'bir\s*saat\s*önce', 'hours'),
            (r'bir\s*gün\s*önce', 'days'), 
            (r'bir\s*hafta\s*önce', 'weeks'),
            (r'bir\s*ay\s*önce', 'months'),
            (r'bir\s*yıl\s*önce', 'years'),
            # Bugün, dün gibi ifadeler
            (r'bugün', 'today'),
            (r'dün', 'yesterday'),
        ]
        
    def parse_turkish_time(self, time_text: str, reference_time: Optional[datetime] = None) -> Tuple[datetime, str]:
        """
        Türkçe zaman ifadesini parse eder
        
        Args:
            time_text: "2 saat önce", "bir gün önce" gibi metinler
            reference_time: Referans zaman (varsayılan: şimdi)
            
        Returns:
            (parsed_datetime, time_category)
        """
        if reference_time is None:
            reference_time = datetime.now()
            
        time_text = time_text.lower().strip()
        
        # Pattern'leri kontrol et
        for pattern, unit in self.time_patterns:
            match = re.search(pattern, time_text, re.IGNORECASE)
            if match:
                return self._calculate_timestamp(match, unit, reference_time, time_text)
        
        # Eğer pattern eşleşmezse bugün olarak kabul et
        return reference_time, 'today'
    
    def _calculate_timestamp(self, match, unit: str, reference_time: datetime, original_text: str) -> Tuple[datetime, str]:
        """Timestamp hesapla"""
        
        # Sayısal değeri al
        if match.groups():
            number = int(match.group(1))
        else:
            # "bir" gibi kelimeler için
            number = 1
        
        # Zaman kategorisini belirle
        time_category = self._get_time_category(number, unit)
        
        # Timestamp hesapla
        if unit == 'hours':
            calculated_time = reference_time - timedelta(hours=number)
        elif unit == 'days':
            calculated_time = reference_time - timedelta(days=number)
        elif unit == 'weeks':
            calculated_time = reference_time - timedelta(weeks=number)
        elif unit == 'months':
            # Ortalama 30 gün kabul edelim
            calculated_time = reference_time - timedelta(days=number * 30)
        elif unit == 'years':
            # Ortalama 365 gün kabul edelim
            calculated_time = reference_time - timedelta(days=number * 365)
        elif unit == 'today':
            calculated_time = reference_time
            time_category = 'today'
        elif unit == 'yesterday':
            calculated_time = reference_time - timedelta(days=1)
            time_category = 'yesterday'
        else:
            calculated_time = reference_time
            time_category = 'today'
        
        return calculated_time, time_category
    
    def _get_time_category(self, number: int, unit: str) -> str:
        """Zaman kategorisi belirle"""
        if unit == 'hours':
            if number < 24:
                return 'today'
            elif number < 48:
                return 'yesterday'
            else:
                return 'this_week'
        elif unit == 'days':
            if number == 0:
                return 'today'
            elif number == 1:
                return 'yesterday'
            elif number <= 7:
                return 'this_week'
            elif number <= 30:
                return 'this_month'
            else:
                return 'older'
        elif unit == 'weeks':
            if number == 1:
                return 'this_week'
            elif number <= 4:
                return 'this_month'
            else:
                return 'older'
        elif unit in ['months', 'years']:
            return 'older'
        else:
            return 'today'

def test_turkish_time_parser():
    """Test fonksiyonu"""
    parser = TurkishTimeParser()
    
    # Test verileri
    test_cases = [
        "1 saat önce",
        "2 saat önce", 
        "bir saat önce",
        "5 gün önce",
        "bir gün önce",
        "2 hafta önce",
        "bir hafta önce", 
        "3 ay önce",
        "bir ay önce",
        "1 yıl önce",
        "bugün",
        "dün",
        "bilinmeyen format"
    ]
    
    print("🧪 TÜRKÇE ZAMAN PARSER TESTİ")
    print("="*50)
    
    reference_time = datetime(2025, 9, 8, 7, 0, 0)  # 8 Eylül 2025, saat 07:00
    print(f"📅 Referans zaman: {reference_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    for test_text in test_cases:
        print(f"\n🔍 Test: '{test_text}'")
        calculated_time, category = parser.parse_turkish_time(test_text, reference_time)
        
        time_diff = reference_time - calculated_time
        print(f"   📊 Sonuç: {calculated_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   📅 Kategori: {category}")
        print(f"   ⏰ Fark: {time_diff}")

if __name__ == "__main__":
    test_turkish_time_parser()
