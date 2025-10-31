# Field Mapping Reference - All Systems

## Database Schema (reviews table)
```sql
- id (INTEGER PRIMARY KEY)
- business_name (TEXT)
- business_url (TEXT)
- reviewer_name (TEXT)
- rating (INTEGER)
- date_original (TEXT)
- review_text (TEXT)
- timestamp_parsed (DATETIME)
- time_category (TEXT)
- scrape_session_id (TEXT)
- review_hash (TEXT UNIQUE)
```

## ReviewsDatabase.add_review() Expected Dictionary Keys
```python
review_data = {
    'business_name': str,       # ✅ Maps to: business_name
    'business_url': str,        # ✅ Maps to: business_url
    'reviewer_name': str,       # ✅ Maps to: reviewer_name
    'rating': int,              # ✅ Maps to: rating
    'review_date': str,         # ✅ Maps to: date_original (NOTE: Key is 'review_date', column is 'date_original')
    'review_text': str,         # ✅ Maps to: review_text
    'timestamp_parsed': str,    # ✅ Maps to: timestamp_parsed (ISO format string)
    'time_category': str,       # ✅ Maps to: time_category
    'session_id': str,          # ✅ Maps to: scrape_session_id (NOTE: Key is 'session_id', column is 'scrape_session_id')
    'review_hash': str          # ✅ Maps to: review_hash
}
```

## Google Maps API Review Object (from api_pipeline/collectors/google_maps_api.py)
```python
@dataclass
class Review:
    author_name: str           # ✅ Use for: reviewer_name
    author_url: str            # ✅ Use for: business_url
    rating: int                # ✅ Use for: rating
    text: str                  # ✅ Use for: review_text
    time: int                  # ✅ UNIX timestamp - convert via .timestamp property
    timestamp: datetime        # ✅ Property that converts time to datetime
    relative_time: str         # ✅ Use for: review_date (e.g., "2 saat önce")
    language: str              # ℹ️ Not stored in DB
    profile_photo_url: str     # ℹ️ Not stored in DB
```

## Correct Mapping Flow

### From API Pipeline Manager (api_pipeline/pipeline_manager.py)
```python
review_data = {
    'business_name': review['business_name'],        # ✅
    'business_url': review['business_url'],          # ✅
    'reviewer_name': review['reviewer_name'],        # ✅
    'rating': review['rating'],                      # ✅
    'review_date': review['date_original'],          # ✅ KEY NAME IMPORTANT!
    'review_text': review['review_text'],            # ✅
    'timestamp_parsed': review['timestamp_parsed'].isoformat(),  # ✅ Convert to ISO string
    'time_category': time_category,                  # ✅ Calculated value
    'session_id': session_id,                        # ✅ KEY NAME IMPORTANT!
    'review_hash': review['review_hash']             # ✅
}
self.db.add_review(review_data)
```

### From Streamlit Dashboard (database_dashboard.py)
```python
review_data = {
    'business_name': business_name,                  # ✅
    'business_url': review.author_url,               # ✅
    'reviewer_name': review.author_name,             # ✅
    'rating': review.rating,                         # ✅
    'review_date': review.relative_time,             # ✅ KEY NAME: 'review_date' not 'date_original'
    'review_text': review.text or "",                # ✅
    'timestamp_parsed': timestamp_obj.isoformat(),   # ✅ Convert datetime to ISO string
    'time_category': time_category,                  # ✅ Calculated via categorize_timestamp()
    'session_id': f'dashboard_{datetime.now()}',     # ✅ KEY NAME: 'session_id' not 'scrape_session_id'
    'review_hash': review_hash                       # ✅
}
db.add_review(review_data)
```

## Common Mistakes to Avoid

❌ **WRONG**: Using keyword arguments
```python
db.add_review(
    business_name=business_name,
    reviewer_name=reviewer_name,
    # ... etc
)
```

✅ **CORRECT**: Using dictionary
```python
review_data = {'business_name': business_name, ...}
db.add_review(review_data)
```

❌ **WRONG**: Using 'date_original' as key
```python
'date_original': review.relative_time  # WRONG KEY NAME
```

✅ **CORRECT**: Using 'review_date' as key
```python
'review_date': review.relative_time  # Correct - maps to date_original column
```

❌ **WRONG**: Using 'scrape_session_id' as key
```python
'scrape_session_id': session_id  # WRONG KEY NAME
```

✅ **CORRECT**: Using 'session_id' as key
```python
'session_id': session_id  # Correct - maps to scrape_session_id column
```

❌ **WRONG**: Passing datetime object
```python
'timestamp_parsed': review.timestamp  # datetime object
```

✅ **CORRECT**: Converting to ISO string
```python
'timestamp_parsed': review.timestamp.isoformat()  # ISO format string
```

## Testing Checklist

- [✅] API Pipeline Manager uses correct field names
- [✅] Dashboard uses correct field names
- [✅] Dictionary structure used (not keyword args)
- [✅] 'review_date' key maps to 'date_original' column
- [✅] 'session_id' key maps to 'scrape_session_id' column
- [✅] timestamp_parsed converted to ISO string format
- [✅] time_category calculated before saving
- [✅] review_hash generated for duplicate detection

## Last Updated
2025-10-31 - All field mappings verified and corrected
