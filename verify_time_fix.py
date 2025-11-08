"""
Quick verification script for time filter changes
"""
from datetime import datetime
import pytz
from database_test import ReviewsDatabase
from database_dashboard import get_reviews_by_time_filter
import pandas as pd

print("=" * 60)
print("TIME FILTER VERIFICATION")
print("=" * 60)

# Current time
tr_tz = pytz.timezone('Europe/Istanbul')
now = datetime.now(tr_tz)
print(f"\nCurrent time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Current date: {now.date()}")

# Load data
db = ReviewsDatabase('reviews.db')
df = db.get_all_reviews()
df['timestamp_parsed'] = pd.to_datetime(df['timestamp_parsed'], errors='coerce')

print(f"\nTotal reviews in database: {len(df)}")

print("\n" + "=" * 60)
print("CUMULATIVE FILTER RESULTS")
print("=" * 60)

filters = [
    ('Yesterday', 'Only Nov 7'),
    ('This Week', 'Last 7 days (Nov 2-8)'),
    ('This Month', 'Last 30 days'),
]

for filter_name, description in filters:
    filtered = get_reviews_by_time_filter(df, filter_name)
    print(f"\n{filter_name:15} ({description})")
    print(f"  → {len(filtered):3} reviews")
    
    if len(filtered) > 0:
        dates = filtered['timestamp_parsed'].dropna()
        if len(dates) > 0:
            oldest = dates.min()
            newest = dates.max()
            print(f"  → Date range: {oldest.strftime('%b %d')} to {newest.strftime('%b %d')}")

print("\n" + "=" * 60)
print("✅ VERIFICATION COMPLETE")
print("=" * 60)
print("\nExpected behavior:")
print("  • Yesterday: Only Nov 7 reviews (single day)")
print("  • This Week: All reviews from Nov 2-8 (7 days)")
print("  • This Month: All reviews from Oct 9 - Nov 8 (30 days)")
print("\nIf numbers match expectations, cumulative filtering is working! ✅")
