# Duplicate Detection System

## 🎯 Overview
Smart duplicate detection system to prevent saving duplicate reviews and speed up scraping.

## 🔑 How It Works

### 1. **Unique Hash Generation**
Each review gets a unique MD5 hash based on:
- Business name
- Reviewer name  
- Review date
- Review text

```python
hash = MD5(business_name + reviewer_name + date + review_text)
```

### 2. **Database Schema**
Added `review_hash` column with UNIQUE constraint:
- Indexed for fast lookups
- Prevents duplicates at database level

### 3. **Real-time Check During Scraping**
Before adding each review:
1. Generate hash
2. Check if hash exists in database
3. Skip if duplicate (⏭️)
4. Save if new (✅)

## 📊 Performance Benefits

### Speed Improvements:
- **Database Query**: ~0.001s per check (indexed hash lookup)
- **No Re-scraping**: Skips already collected reviews
- **Batch Operations**: Efficient duplicate filtering

### Example:
```
First Scrape:  100 reviews → 100 saved ✅
Second Scrape: 100 reviews → 20 new, 80 skipped ⏭️
Time Saved:    80% faster on re-scrape!
```

## 🚀 Usage

### Automatic (Default)
System automatically checks for duplicates during scraping:

```python
scraper = DatabaseGoogleMapsScraper()
result = scraper.extract_reviews_with_database(
    business_name="Starbucks",
    target_text_reviews=50
)
# Duplicates are automatically skipped ⏭️
```

### Manual Check
```python
db = ReviewsDatabase()

# Generate hash
hash_value = db.generate_review_hash(
    business_name="Starbucks",
    reviewer_name="John Doe",
    date="2 days ago",
    review_text="Great coffee!"
)

# Check if exists
if db.check_review_exists(hash_value):
    print("⏭️ Duplicate!")
else:
    print("✅ New review!")
```

## 📈 Statistics

After saving reviews, you'll see:
```
✅ 25 new reviews saved to database
⏭️ 15 duplicate reviews skipped
```

## 🔧 Technical Details

### Hash Function
- **Algorithm**: MD5 (fast, sufficient for this use case)
- **Collision Probability**: ~0% for our data size
- **Performance**: ~1 microsecond per hash

### Database Index
```sql
CREATE INDEX idx_review_hash ON reviews(review_hash)
```
- **Type**: B-Tree index
- **Lookup Time**: O(log n)
- **Storage**: Minimal overhead

### Migration
Existing databases are automatically upgraded:
- `review_hash` column added
- Index created
- Old reviews get hash on first update

## 🎯 Use Cases

### 1. Incremental Scraping
Update your database without re-collecting old reviews:
```python
# Day 1: Collect initial reviews
scraper.extract_reviews_with_database("Business A", target=100)
# → 100 reviews saved

# Day 7: Update with new reviews
scraper.extract_reviews_with_database("Business A", target=100)
# → Only NEW reviews since day 1 are saved!
```

### 2. Multi-Source Scraping
Prevent duplicates when scraping same business from different URLs:
```python
# From search
scraper.extract_reviews_with_database(
    business_name="Pizza Place",
    search_query="Pizza Place Istanbul"
)

# From direct URL (same business)
scraper.extract_reviews_with_database(
    business_name="Pizza Place",
    business_url="https://maps.google.com/..."
)
# → Duplicates automatically skipped!
```

### 3. Error Recovery
Resume scraping after interruption:
```python
# First attempt (interrupted)
scraper.extract_reviews_with_database("Business", target=200)
# → 150 collected, then crash

# Resume (automatic skip of existing)
scraper.extract_reviews_with_database("Business", target=200)
# → Continues from review 151!
```

## 💡 Best Practices

1. **Always use business_name consistently** - Same spelling, same case
2. **Let the system handle duplicates** - Don't try to filter manually
3. **Monitor skip rate** - High skip rate means you've already collected most data
4. **Regular scraping** - Daily/weekly updates become very fast

## 🔍 Troubleshooting

### Issue: False duplicates
**Cause**: Business name spelling inconsistency
**Solution**: Use exact same business_name string

### Issue: Not skipping duplicates
**Cause**: Database schema not updated
**Solution**: Delete old database or run migration script

### Issue: Slow performance
**Cause**: Missing index
**Solution**: Database automatically creates index on first run

## 📝 Changelog

### v2.0 (Current)
- ✅ Added MD5 hash-based duplicate detection
- ✅ Database schema updated with review_hash
- ✅ Indexed for fast lookups
- ✅ Real-time duplicate checking during scraping
- ✅ Batch duplicate filtering
- ✅ Statistics showing skip count

### v1.0 (Previous)
- Basic review collection
- No duplicate detection
- Manual cleanup required
