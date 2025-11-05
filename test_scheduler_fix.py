#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Scheduler with Improved Logging
"""

from background_scheduler import BackgroundScheduler
from api_pipeline.config.settings import BusinessConfig
import json

print("="*60)
print("🧪 Testing Scheduler Fix")
print("="*60)

# Get all businesses
businesses = BusinessConfig.get_all_businesses_from_db()

print(f"\n📋 Found {len(businesses)} businesses:")
for place_id, name in businesses:
    status = "✅" if place_id and place_id.startswith('ChIJ') else "❌"
    print(f"{status} {name}")
    print(f"   Place ID: {place_id}")

# Test collection
print("\n🚀 Testing collection...")
scheduler = BackgroundScheduler()
result = scheduler.collect_reviews()

print("\n📊 Collection Result:")
print(json.dumps(result, indent=2))

# Show logs
print("\n📝 Recent Logs:")
status = scheduler.get_status()
for log in status.get('logs', [])[-10:]:
    level = log.get('level', 'info')
    message = log.get('message', '')
    icon = {'info': 'ℹ️', 'success': '✅', 'error': '❌', 'warning': '⚠️'}.get(level, 'ℹ️')
    print(f"{icon} {message}")

print("\n" + "="*60)
