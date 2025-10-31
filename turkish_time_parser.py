#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🕒 Turkish Time Expression Parser
Converts "X ago" expressions from Google Maps to real timestamps
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Tuple

class TurkishTimeParser:
    """Parses Turkish time expressions"""
    
    def __init__(self):
        # Time expression regex patterns
        self.time_patterns = [
            # "X saat önce" (X hours ago) pattern
            (r'(\d+)\s*saat\s*önce', 'hours'),
            # "X gün önce" (X days ago) pattern  
            (r'(\d+)\s*gün\s*önce', 'days'),
            # "X hafta önce" (X weeks ago) pattern
            (r'(\d+)\s*hafta\s*önce', 'weeks'),
            # "X ay önce" (X months ago) pattern
            (r'(\d+)\s*ay\s*önce', 'months'),
            # "X yıl önce" (X years ago) pattern
            (r'(\d+)\s*yıl\s*önce', 'years'),
            # Singular versions
            (r'bir\s*saat\s*önce', 'hours'),
            (r'bir\s*gün\s*önce', 'days'), 
            (r'bir\s*hafta\s*önce', 'weeks'),
            (r'bir\s*ay\s*önce', 'months'),
            (r'bir\s*yıl\s*önce', 'years'),
            # Today, yesterday expressions
            (r'bugün', 'today'),
            (r'dün', 'yesterday'),
        ]
        
    def parse_turkish_time(self, time_text: str, reference_time: Optional[datetime] = None) -> Tuple[datetime, str]:
        """
        Parse Turkish time expression
        
        Args:
            time_text: Text like "2 saat önce", "bir gün önce"
            reference_time: Reference time (default: now)
            
        Returns:
            (parsed_datetime, time_category)
        """
        if reference_time is None:
            reference_time = datetime.now()
            
        time_text = time_text.lower().strip()
        
        # Check patterns
        for pattern, unit in self.time_patterns:
            match = re.search(pattern, time_text, re.IGNORECASE)
            if match:
                return self._calculate_timestamp(match, unit, reference_time, time_text)
        
        # If no pattern matches, assume today
        return reference_time, 'today'
    
    def _calculate_timestamp(self, match, unit: str, reference_time: datetime, original_text: str) -> Tuple[datetime, str]:
        """Calculate timestamp"""
        
        # Get numeric value
        if match.groups():
            number = int(match.group(1))
        else:
            # For words like "bir" (one)
            number = 1
        
        # Determine time category
        time_category = self._get_time_category(number, unit)
        
        # Calculate timestamp
        if unit == 'hours':
            calculated_time = reference_time - timedelta(hours=number)
        elif unit == 'days':
            calculated_time = reference_time - timedelta(days=number)
        elif unit == 'weeks':
            calculated_time = reference_time - timedelta(weeks=number)
        elif unit == 'months':
            # Assume average 30 days
            calculated_time = reference_time - timedelta(days=number * 30)
        elif unit == 'years':
            # Assume average 365 days
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
        """Determine time category"""
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
    """Test function"""
    parser = TurkishTimeParser()
    
    # Test data
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
    
    print("🧪 TURKISH TIME PARSER TEST")
    print("="*50)
    
    reference_time = datetime(2025, 9, 8, 7, 0, 0)  # September 8, 2025, 07:00
    print(f"📅 Reference time: {reference_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    for test_text in test_cases:
        print(f"\n🔍 Test: '{test_text}'")
        calculated_time, category = parser.parse_turkish_time(test_text, reference_time)
        
        time_diff = reference_time - calculated_time
        print(f"   📊 Result: {calculated_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   📅 Category: {category}")
        print(f"   ⏰ Difference: {time_diff}")

if __name__ == "__main__":
    test_turkish_time_parser()
