# 🚀 Google Maps API Data Pipeline

**Real-time review collection system using Google Maps API + Airflow orchestration**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Apache Airflow](https://img.shields.io/badge/airflow-3.1.1-orange.svg)](https://airflow.apache.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Overview

This project is a complete data engineering pipeline that:
- 🎯 **Collects reviews** from Google Maps API (latest 5 reviews per business)
- 🔄 **Runs automatically** every 5 minutes (configurable)
- 🚫 **Prevents duplicates** using hash-based detection
- 💾 **Stores in SQLite** with full duplicate prevention
- 📊 **Visualizes data** with Streamlit dashboard
- 🤖 **AI Analysis** using Google Gemini API

## 🆚 Web Scraping vs API Approach

| Feature | Web Scraping (Old) | API Pipeline (New) |
|---------|-------------------|-------------------|
| Speed | 🐢 Slow (30-60s) | ⚡ Fast (1-2s) |
| Reliability | ❌ Brittle (HTML changes) | ✅ Stable (Official API) |
| Scalability | 🔴 Limited | 🟢 Excellent |
| Maintenance | 🔧 High (breaks often) | ✨ Low (API stable) |
| Rate Limits | ⚠️ Risk of blocking | ✅ Documented limits |
| Data Quality | 📊 Good | 💎 Excellent |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         Apache Airflow Scheduler            │
│       (Every 5 minutes - cron: */5)         │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  Google Maps API │
         │  (Latest 5 revs) │
         └────────┬─────────┘
                  │
                  ▼
         ┌─────────────────┐
         │ Duplicate Check  │
         │  (MD5 Hash)      │
         └────────┬─────────┘
                  │
            ✅ New  │  ⏭️ Skip
                  ▼
         ┌─────────────────┐
         │   SQLite DB      │
         │ (reviews.db)     │
         └────────┬─────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  Streamlit UI    │
         │ (Real-time view) │
         └──────────────────┘
```

## ✨ Features

### 🔧 Core Pipeline
- ✅ **Google Maps API Integration** - Official API, fast & reliable
- ✅ **Smart Duplicate Detection** - MD5 hash-based (business + reviewer + date + text)
- ✅ **Automatic Scheduling** - Airflow DAG or simple scheduler
- ✅ **Multi-Business Support** - Track multiple businesses simultaneously
- ✅ **Error Recovery** - Retry logic with exponential backoff
- ✅ **Statistics Tracking** - Monitor collections, duplicates, errors

### 📊 Dashboard
- ✅ **Real-time Visualization** - Streamlit web interface
- ✅ **Time-based Analysis** - Filter by date ranges
- ✅ **Rating Distribution** - Visual charts with Plotly
- ✅ **WordCloud** - Visual representation of common terms
- ✅ **AI Analysis** - Google Gemini powered insights

### 🤖 AI Features
- ✅ **Sentiment Analysis** - Positive/Negative/Mixed breakdown
- ✅ **Theme Detection** - Top 5-7 themes mentioned
- ✅ **Strength Analysis** - What customers love most
- ✅ **Improvement Areas** - Common complaints
- ✅ **Customer Insights** - Behavioral patterns & recommendations

## 📁 Project Structure

```
api_pipeline/
├── collectors/
│   ├── __init__.py
│   └── google_maps_api.py      # API collector
├── config/
│   ├── __init__.py
│   └── settings.py              # Configuration management
├── dags/
│   ├── __init__.py
│   └── google_maps_pipeline.py  # Airflow DAG
├── pipeline_manager.py          # Main pipeline orchestrator
└── scheduler.py                 # Simple scheduler (no Airflow)
```

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Python 3.12+
python --version

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create `.env` file:

```env
# Google Maps API Key
GOOGLE_MAPS_API_KEY=your_api_key_here

# Google Gemini API Key (optional - for AI analysis)
GEMINI_API_KEY=your_gemini_key_here

# Database
DATABASE_PATH=reviews.db

# Collection Settings
API_LANGUAGE=tr
COLLECTION_INTERVAL_MINUTES=5
```

### 3. Add Businesses to Track

Edit `api_pipeline/config/settings.py`:

```python
class BusinessConfig:
    BUSINESSES: List[tuple] = [
        ("ChIJqZW8Cvb_n0ARBuUkyCzgDDg", "İstanbul Havalimanı"),
        ("YOUR_PLACE_ID_HERE", "Your Business Name"),
        # Add more businesses...
    ]
```

### 4. Run Options

#### Option A: Simple Scheduler (Recommended for testing)

```bash
# Run once
python api_pipeline/scheduler.py --once

# Run continuously (every 5 minutes)
python api_pipeline/scheduler.py

# Custom interval (every 10 minutes)
python api_pipeline/scheduler.py --interval 10
```

#### Option B: Airflow (Production)

```bash
# Initialize Airflow database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

# Start Airflow webserver
airflow webserver --port 8080

# Start Airflow scheduler (in another terminal)
airflow scheduler

# Access Airflow UI: http://localhost:8080
```

### 5. View Dashboard

```bash
# Start Streamlit dashboard
streamlit run database_dashboard.py

# Access dashboard: http://localhost:8502
```

## 📊 Usage Examples

### Single Collection

```python
from api_pipeline.pipeline_manager import APIPipelineManager

# Initialize pipeline
pipeline = APIPipelineManager()

# Run collection
result = pipeline.run_pipeline()

# Check results
print(f"Fetched: {result['stats']['total_reviews_fetched']}")
print(f"New: {result['stats']['new_reviews_saved']}")
print(f"Duplicates: {result['stats']['duplicates_skipped']}")
```

### API Collector Only

```python
from api_pipeline.collectors.google_maps_api import GoogleMapsAPICollector

# Initialize collector
collector = GoogleMapsAPICollector(api_key="YOUR_API_KEY")

# Collect reviews
result = collector.collect_reviews(
    place_id="ChIJqZW8Cvb_n0ARBuUkyCzgDDg",
    business_name="İstanbul Havalimanı"
)

# Access reviews
for review in result['reviews']:
    print(f"{review.author_name}: {review.rating}⭐")
    print(f"{review.text[:100]}...")
```

## 🔍 How It Works

### 1. **Data Collection**
```
API Request → Google Maps API
  ↓
Returns: Latest 5 reviews (sorted by newest)
  ↓
Parse: Extract author, rating, text, date
```

### 2. **Duplicate Detection**
```
For each review:
  ↓
Generate Hash: MD5(business + reviewer + date + text)
  ↓
Check Database: Does hash exist?
  ↓
  YES → Skip (⏭️)
  NO  → Save (✅)
```

### 3. **Storage**
```
New reviews → SQLite Database
  ↓
Table: reviews
Columns:
  - business_name
  - reviewer_name
  - rating
  - review_text
  - date_original
  - review_hash (UNIQUE)
  - timestamp_parsed
  - scrape_session_id
```

## 📈 Performance

- **API Speed**: ~1-2 seconds per request
- **Duplicate Check**: O(1) using hash index
- **Memory**: Minimal (streams data)
- **Scalability**: Can handle 100+ businesses
- **Rate Limit**: Google Maps API limits apply

## 🎯 Use Cases

1. **Real-time Monitoring**
   - Track new reviews as they come
   - Alert on negative reviews
   - Monitor competitor feedback

2. **Sentiment Analysis**
   - Understand customer sentiment
   - Identify trends over time
   - Generate actionable insights

3. **Business Intelligence**
   - Compare multiple locations
   - Track improvement over time
   - Generate reports

4. **Customer Service**
   - Quick response to negative reviews
   - Thank customers for positive feedback
   - Address common complaints

## 🔐 Security

- ✅ API keys stored in `.env` (not in git)
- ✅ Database uses parameterized queries
- ✅ Hash-based duplicate detection (no PII leakage)
- ✅ Rate limiting respected

## 📝 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_MAPS_API_KEY` | Google Maps API key | Required |
| `GEMINI_API_KEY` | Google Gemini API key | Optional |
| `DATABASE_PATH` | SQLite database file | `reviews.db` |
| `API_LANGUAGE` | API response language | `tr` |
| `COLLECTION_INTERVAL_MINUTES` | Collection frequency | `5` |
| `AIRFLOW_SCHEDULE` | Airflow cron schedule | `*/5 * * * *` |

## 🐛 Troubleshooting

### API Key Issues
```bash
❌ Error: GOOGLE_MAPS_API_KEY not found
✅ Solution: Add to .env file
```

### Duplicate Reviews
```bash
⏭️ All reviews skipped as duplicates
✅ Normal: No new reviews since last collection
```

### Airflow Not Starting
```bash
❌ Error: airflow command not found
✅ Solution: pip install apache-airflow
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Google Maps API for reliable data access
- Apache Airflow for workflow orchestration
- Streamlit for beautiful dashboards
- Google Gemini for AI-powered insights

## 📞 Support

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/google-maps-api-pipeline/issues)
- 📚 Docs: [Wiki](https://github.com/yourusername/google-maps-api-pipeline/wiki)

---

**Made with ❤️ by Data Engineers, for Data Engineers**
