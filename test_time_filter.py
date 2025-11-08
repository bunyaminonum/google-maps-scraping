"""Test cumulative time filtering logic"""
from datetime import datetime
import pytz
import pandas as pd
from database_test import ReviewsDatabase
from database_dashboard import categorize_timestamp, get_reviews_by_time_filter

# Load data
db = ReviewsDatabase('reviews.db')
df = db.get_all_reviews()
df['timestamp_parsed'] = pd.to_datetime(df['timestamp_parsed'], errors='coerce')

print("=== ORIGINAL TIME CATEGORIES ===")
print(df['time_category'].value_counts())
print(f"\nTotal reviews: {len(df)}")

print("\n=== CUMULATIVE FILTERING TEST ===")
print("(Each filter should include ALL reviews within that timeframe)\n")

time_filters = ['Yesterday', 'This Week', 'This Month', 'Last 3 Months', 'This Year']

for time_filter in time_filters:
    filtered = get_reviews_by_time_filter(df, time_filter)
    print(f"{time_filter:20} → {len(filtered):3} reviews")

print("\n=== DETAILED BREAKDOWN ===")
# Yesterday: should be ONLY yesterday (single day)
yesterday_df = get_reviews_by_time_filter(df, 'Yesterday')
print(f"\nYesterday (Nov 7): {len(yesterday_df)} reviews")
if len(yesterday_df) > 0:
    sample = yesterday_df['timestamp_parsed'].head(3)
    print("Sample dates:", [d.strftime('%Y-%m-%d %H:%M') for d in sample if pd.notna(d)])

# This Week: should include last 7 days
week_df = get_reviews_by_time_filter(df, 'This Week')
print(f"\nThis Week (last 7 days): {len(week_df)} reviews")
if len(week_df) > 0:
    dates = week_df['timestamp_parsed'].dropna()
    if len(dates) > 0:
        print(f"Oldest: {dates.min().strftime('%Y-%m-%d %H:%M')}")
        print(f"Newest: {dates.max().strftime('%Y-%m-%d %H:%M')}")

# This Month: should include last 30 days
month_df = get_reviews_by_time_filter(df, 'This Month')
print(f"\nThis Month (last 30 days): {len(month_df)} reviews")
if len(month_df) > 0:
    dates = month_df['timestamp_parsed'].dropna()
    if len(dates) > 0:
        print(f"Oldest: {dates.min().strftime('%Y-%m-%d %H:%M')}")
        print(f"Newest: {dates.max().strftime('%Y-%m-%d %H:%M')}")

print("\n✅ Test completed!")
