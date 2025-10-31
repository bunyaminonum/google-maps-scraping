# Google Maps Review Scraper 🗺️

Firefox-based Google Maps business review extraction system.

## 🎯 Features

- ✅ **Firefox WebDriver** - Optimized against bot protection
- ✅ **Real-time review extraction** - Latest business reviews
- ✅ **CSV export** - Data export for easy analysis
- ✅ **Turkish support** - Both Turkish and English reviews
- ✅ **Flexible search** - Search by business name and location
- ✅ **Rate limiting** - Safe and controlled scraping

## 📋 Requirements

### Python Packages
```bash
pip install -r requirements.txt
```

### Dependencies
- Python 3.8+
- Firefox browser installed
- selenium
- webdriver-manager
- pandas
- beautifulsoup4

## 🚀 Usage

### Quick Start

```python
from firefox_optimized_scraper import FirefoxGoogleMapsReviewScraper

# Initialize scraper
scraper = FirefoxGoogleMapsReviewScraper(headless=False)

# Extract reviews
reviews = scraper.scrape_reviews(
    business_name="Starbucks Zorlu Center",
    location="Istanbul",
    max_reviews=10
)

# Display results
for review in reviews:
    print(f"{review.reviewer_name}: {review.review_text[:100]}...")
```

### Command Line Usage

```bash
# Run optimized scraper for testing
python firefox_optimized_scraper.py

# Istanbul Airport special test
python test_istanbul_airport.py

# Multiple business test
python test_multiple_businesses.py
```

## 📊 Output Format

### Review Object
```python
@dataclass
class Review:
    reviewer_name: str      # Reviewer name
    review_text: str        # Review text
    rating: str            # Rating (1-5)
    date: str              # Date (e.g., "3 months ago")
    is_new: bool           # Is new?
    platform: str          # Platform name
```

### CSV Output
```csv
Reviewer_Name,Review_Text,Rating,Date,Platform
"John Doe","Great place, definitely recommend",5,"2 days ago","Google Maps (Firefox)"
```

## 🔧 Configuration

### Firefox Settings
```python
# Visible mode (recommended)
scraper = FirefoxGoogleMapsReviewScraper(headless=False)

# Headless mode (background)
scraper = FirefoxGoogleMapsReviewScraper(headless=True)
```

### Customizable Parameters
- `business_name`: Business name (required)
- `location`: Location (optional)
- `max_reviews`: Maximum number of reviews (default: 10)

## 📁 Project Structure

```
google-maps-scraping/
├── firefox_optimized_scraper.py    # Main scraper (OPTIMIZED BASED ON TEST RESULTS)
├── firefox_test_enhanced.py        # Enhanced test script
├── test_istanbul_airport.py        # Istanbul Airport test
├── test_multiple_businesses.py     # Multiple business test
├── google_maps_scraper_firefox.py  # First version scraper
├── requirements.txt                 # Python dependencies
├── README.md                       # This file
└── *.csv                          # Output files
```

## 🧪 Tested Businesses

✅ **Starbucks Zorlu Center** - Istanbul
✅ **Istanbul Airport** - Istanbul
✅ **Maxx Royal Kemer Resort** - Antalya
✅ **Galata Tower** - Istanbul

## 🔍 Technical Details

### Used CSS Selectors (Test Results)
- `[data-review-id]`: 98 elements found ✅
- `.jftiEf.fontBodyMedium`: 10 elements found ✅
- `.wiI7pd`: Review text (10 elements) ✅
- `.d4r55.fontTitleMedium`: Reviewer name (10 elements) ✅

### Firefox Optimizations
- Enhanced JavaScript element detection
- Aria-label based navigation
- Wait times for rate limiting
- Dynamic loading with scroll operations

## ⚠️ Important Notes

1. **Rate Limiting**: Slow scraping to respect Google's bot protection
2. **Firefox Recommendation**: Less bot detection than Chrome
3. **Visible Mode**: Use headless=False for initial tests
4. **Internet Connection**: Stable connection required

## 🐛 Troubleshooting

### Common Errors

**1. Reviews not found**
```python
# Solution: Add more waiting time
time.sleep(5)
```

**2. WebDriver error**
```bash
# Solution: Update WebDriver
pip install --upgrade webdriver-manager
```

**3. CSS selector not working**
```python
# Solution: Check selectors using test script
python firefox_test_enhanced.py
```

## 📈 Performance

- **Average Processing Time**: 30-60 seconds (for 10 reviews)
- **Success Rate**: 95%+ (on tested businesses)
- **Supported Review Count**: 1-100 reviews/business

## 🤝 Contributing

1. Fork this repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For questions:
- Open GitHub Issues
- Run test scripts
- Use debug mode

---

**Last updated**: Firefox CSS selectors optimized based on test results ✅
