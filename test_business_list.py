#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test business CRUD operations"""

from database_test import ReviewsDatabase

db = ReviewsDatabase('reviews.db')

print("\n" + "="*60)
print("📊 BUSINESSES IN DATABASE")
print("="*60)

businesses = db.get_all_businesses()

for i, b in enumerate(businesses, 1):
    print(f"\n{i}. {b['name']}")
    print(f"   Place ID: {b['place_id']}")
    print(f"   Enabled: {'✅ Yes' if b['enabled'] else '❌ No'}")
    print(f"   ID: {b['id']}")

print("\n" + "="*60)
print(f"Total: {len(businesses)} businesses")
print("="*60)
