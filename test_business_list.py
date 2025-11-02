#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test business list from database
"""

from api_pipeline.config.settings import BusinessConfig

print("🔍 Testing get_all_businesses_from_db()")
print("=" * 70)

businesses = BusinessConfig.get_all_businesses_from_db()

print(f"\n📊 Total unique businesses: {len(businesses)}")
print("\n📍 Business List:")
print("-" * 70)

for i, (place_id, name) in enumerate(businesses, 1):
    place_id_short = place_id[:20] + "..." if len(place_id) > 20 else place_id
    print(f"{i}. {name}")
    print(f"   Place ID: {place_id_short}")

print("\n" + "=" * 70)
