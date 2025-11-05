#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Business CRUD Operations"""

from database_test import ReviewsDatabase

db = ReviewsDatabase('reviews.db')

print("\n" + "="*60)
print("🧪 TESTING BUSINESS CRUD OPERATIONS")
print("="*60)

# 1. List all businesses
print("\n1️⃣ Current businesses:")
businesses = db.get_all_businesses()
for b in businesses:
    status = "✅ Enabled" if b['enabled'] else "❌ Disabled"
    print(f"   - {b['name']} ({status})")
print(f"   Total: {len(businesses)}")

# 2. Add a test business
print("\n2️⃣ Adding 'Test Restaurant'...")
result = db.add_business('Test Restaurant', 'ChIJtestplace123456789', enabled=True)
print(f"   Result: {result}")

# 3. List again
print("\n3️⃣ After adding:")
businesses = db.get_all_businesses()
for b in businesses:
    status = "✅ Enabled" if b['enabled'] else "❌ Disabled"
    print(f"   - {b['name']} ({status}) [ID: {b['id']}]")
print(f"   Total: {len(businesses)}")

# 4. Toggle the test business
test_biz = [b for b in businesses if b['name'] == 'Test Restaurant']
if test_biz:
    test_id = test_biz[0]['id']
    print(f"\n4️⃣ Toggling 'Test Restaurant' (ID: {test_id})...")
    result = db.toggle_business(test_id)
    print(f"   Result: {result}")

# 5. Update the test business
if test_biz:
    print(f"\n5️⃣ Updating 'Test Restaurant'...")
    result = db.update_business(test_id, name='Test Cafe Updated')
    print(f"   Result: {result}")

# 6. Delete the test business
if test_biz:
    print(f"\n6️⃣ Deleting 'Test Cafe Updated'...")
    result = db.delete_business(test_id)
    print(f"   Result: {result}")

# 7. Final list
print("\n7️⃣ Final businesses:")
businesses = db.get_all_businesses()
for b in businesses:
    status = "✅ Enabled" if b['enabled'] else "❌ Disabled"
    print(f"   - {b['name']} ({status})")
print(f"   Total: {len(businesses)}")

print("\n" + "="*60)
print("✅ CRUD TEST COMPLETED!")
print("="*60)
