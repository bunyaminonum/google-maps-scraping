# Google Maps Reviews Dashboard 🗺️# Google Maps Reviews - API Data Pipeline �



Modern Google Maps review collection and analysis platform with Streamlit dashboard, automated scheduling, and AI-powered insights.Modern data engineering project powered by Google Maps Places API with automated collection and AI analysis.



## 🎯 Features## 🎯 Features



- ✅ **Google Maps Places API** - Fast & reliable official API (1-2 seconds per business)- ✅ **Google Maps Places API** - Fast & reliable official API (1-2 seconds vs 30-60 seconds scraping)

- ✅ **Automated Scheduler** - Background collection with auto-recovery (15/30/60/120/180 min intervals)- ✅ **Automated Pipeline** - Scheduled data collection every 5 minutes

- ✅ **Real-time Dashboard** - Interactive Streamlit interface with 5 analysis tabs- ✅ **Duplicate Detection** - Hash-based system prevents duplicate reviews

- ✅ **AI Analysis** - Google Gemini AI-powered sentiment analysis and insights- ✅ **Real-time Dashboard** - Streamlit interface with 5 analysis tabs

- ✅ **Time-based Filtering** - Calendar-based filters (Today, Yesterday, This Week, This Month, etc.)- ✅ **AI Analysis** - Google Gemini AI-powered review insights

- ✅ **Business Management** - Enable/disable businesses, manual collection control- ✅ **Apache Airflow Ready** - Production-ready DAG for Linux/Docker

- ✅ **Docker Deployment** - Production-ready containerization with health checks- ✅ **SQLite Database** - Efficient storage with automatic migrations

- ✅ **SQLite Database** - Efficient storage with automatic schema management

## 📋 Requirements

## 🐳 Docker Deployment (Recommended)

### System Requirements

### Quick Start- **Python 3.12+** (Recommended for best compatibility)

- **Windows/Linux/MacOS** (Airflow requires Linux for production)

1. **Clone repository:**

```bash### Python Packages

git clone <repository-url>```bash

cd google-maps-scraping-1pip install -r requirements.txt

git checkout feature/docker-deployment```

```

### Core Dependencies

2. **Create `.env` file:**- `google-maps-services` - Google Maps Places API client

```bash- `google-generativeai` - Gemini AI for review analysis

GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here- `streamlit` - Interactive dashboard

GEMINI_API_KEY=your_gemini_api_key_here- `pandas` - Data processing

DATABASE_PATH=reviews.db- `plotly` - Interactive visualizations

API_LANGUAGE=tr- `python-dotenv` - Environment configuration

```- `apache-airflow` - Workflow orchestration (Linux/Docker)



3. **Start with Docker Compose:**### 🔑 API Keys Setup (Required)

```bash

docker-compose up -d1. **Google Maps API Key**

```   - Get from [Google Cloud Console](https://console.cloud.google.com/)

   - Enable "Places API"

4. **Access dashboard:**

```2. **Google Gemini API Key** 

http://localhost:8501   - Get from [Google AI Studio](https://aistudio.google.com/app/apikey)

```

3. **Create `.env` file:**

### Docker Features```bash

GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

- **Multi-stage Build** - Optimized image size with builder patternGEMINI_API_KEY=your_gemini_api_key_here

- **Health Checks** - Automatic container health monitoringDATABASE_PATH=reviews.db

- **Volume Persistence** - Database persists across container restartsAPI_LANGUAGE=tr

- **Non-root User** - Security best practices with dedicated appuserCOLLECTION_INTERVAL_MINUTES=5

- **Auto-recovery** - Scheduler automatically restarts after container restart```



### Docker Commands## 🚀 Quick Start



```bash### 1️⃣ Start Automated Pipeline (Windows)

# Start containers

docker-compose up -d```bash

# Single run (test)

# View logspython api_pipeline/scheduler.py --once

docker-compose logs -f dashboard

# Continuous collection (every 5 minutes)

# Stop containerspython api_pipeline/scheduler.py --interval 5

docker-compose down

# Or use batch file

# Rebuild after code changesstart_pipeline.bat

docker-compose up -d --build```



# Check container status### 2️⃣ Start Dashboard

docker ps

```bash

# Execute commands in containerpython -m streamlit run database_dashboard.py

docker exec -it google-maps-dashboard /bin/bash```

```

### 3️⃣ View Results

### Verifying Scheduler Status

Open browser: `http://localhost:8501`

```powershell

# Check scheduler status (Windows PowerShell)## 🎯 Usage Examples

docker exec google-maps-dashboard cat /app/scheduler_status.json | ConvertFrom-Json | Select-Object active, last_run, next_run, total_collections | Format-List

```### Collect Reviews via API



Expected output:```python

```from api_pipeline.collectors.google_maps_api import GoogleMapsAPICollector

active: True

last_run: 2025-11-09T18:25:55.545225# Initialize collector

next_run: 2025-11-09T20:25:55.545225collector = GoogleMapsAPICollector()

total_collections: 77

```# Collect reviews

result = collector.collect_reviews(

## 📋 Requirements (Local Installation)    place_id="ChIJqZW8Cvb_n0ARBuUkyCzgDDg",  # Istanbul Airport

    business_name="İstanbul Havalimanı"

### System Requirements)

- **Python 3.11+** (or Docker for containerized deployment)

- **Windows/Linux/MacOS**# Display results

print(f"Success: {result['success']}")

### Python Packagesprint(f"Reviews: {result['total_count']}")

```bash```

pip install -r requirements.txt

```### Add New Business



### Core DependenciesEdit `api_pipeline/config/settings.py`:

- `google-maps-services` - Google Maps Places API client

- `google-generativeai` - Gemini AI for review analysis```python

- `streamlit` - Interactive dashboardBUSINESSES = [

- `pandas` - Data processing    ("ChIJqZW8Cvb_n0ARBuUkyCzgDDg", "İstanbul Havalimanı"),

- `plotly` - Interactive visualizations    ("YOUR_PLACE_ID", "Your Business Name"),

- `python-dotenv` - Environment configuration]

```

### 🔑 API Keys Setup (Required)

Find Place ID: [Place ID Finder](https://developers.google.com/maps/documentation/places/web-service/place-id)

1. **Google Maps API Key**

   - Get from [Google Cloud Console](https://console.cloud.google.com/)## 📊 Output Format

   - Enable "Places API"

### Review Object

2. **Google Gemini API Key** ```python

   - Get from [Google AI Studio](https://aistudio.google.com/app/apikey)@dataclass

class Review:

3. **Create `.env` file:**    reviewer_name: str      # Reviewer name

```bash    review_text: str        # Review text

GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here    rating: str            # Rating (1-5)

GEMINI_API_KEY=your_gemini_api_key_here    date: str              # Date (e.g., "3 months ago")

DATABASE_PATH=reviews.db    is_new: bool           # Is new?

API_LANGUAGE=tr    platform: str          # Platform name

``````



## 🚀 Quick Start (Local)### CSV Output

```csv

### 1️⃣ Start Dashboard with Built-in SchedulerReviewer_Name,Review_Text,Rating,Date,Platform

"John Doe","Great place, definitely recommend",5,"2 days ago","Google Maps (Firefox)"

```bash```

python -m streamlit run database_dashboard.py

```## 🔧 Configuration



The dashboard includes an integrated scheduler that can be configured and controlled from the UI.### Firefox Settings

```python

### 2️⃣ Start Independent Scheduler (Optional)# Visible mode (recommended)

scraper = FirefoxGoogleMapsReviewScraper(headless=False)

For running scheduler separately from dashboard:

# Headless mode (background)

```bashscraper = FirefoxGoogleMapsReviewScraper(headless=True)

# Windows```

run_scheduler.bat

### Customizable Parameters

# Linux/Mac- `business_name`: Business name (required)

python run_scheduler_standalone.py- `location`: Location (optional)

```- `max_reviews`: Maximum number of reviews (default: 10)



### 3️⃣ View Results## 📁 Project Structure



Open browser: `http://localhost:8501````

google-maps-scraping/

## 📊 Dashboard Features├── api_pipeline/                    # 🚀 API Data Pipeline

│   ├── collectors/

### 📈 Overview Tab│   │   └── google_maps_api.py      # Google Maps API collector

- **Total Reviews** - Count and distribution across time periods│   ├── config/

- **Rating Distribution** - 5-star rating breakdown with percentages│   │   └── settings.py             # Configuration management

- **Business Performance** - Individual business metrics and review counts│   ├── dags/

- **Review Trends** - Time-series visualization of review collection│   │   └── google_maps_pipeline.py # Airflow DAG

│   ├── pipeline_manager.py         # Main orchestration

### ⏰ Time Analysis Tab│   └── scheduler.py                # Simple scheduler (no Airflow)

- **Calendar-based Filtering** - Today, Yesterday, This Week, This Month, Last 3 Months, This Year, All Time│

- **Cumulative Filtering** - "This Week" includes ALL reviews from last 7 days (not just categorized as "This Week")├── database_dashboard.py            # 📊 Streamlit dashboard (API-powered)

- **Review Timeline** - Historical review collection patterns├── database_test.py                 # 💾 Database management

- **Time Distribution** - Review activity by time period├── API_PIPELINE_README.md          # 📖 Detailed documentation

├── start_pipeline.bat              # ⚡ Windows quick start

### 🔍 Review Details Tab├── requirements.txt                 # 📦 Dependencies

- **Full Review List** - All reviews with ratings, dates, and business info├── .env                            # 🔑 API keys (create this)

- **Search & Filter** - Find specific reviews by text, rating, or business└── reviews.db                      # 💾 SQLite database

- **Export Options** - Download filtered reviews as CSV```

- **Pagination** - Navigate through large review sets

## 🏗️ Architecture

### ☁️ WordCloud Tab

- **Visual Keywords** - Most frequent words in review texts```

- **Turkish Language Support** - Proper handling of Turkish characters┌─────────────────────────────────────────────────────────────┐

- **Time-filtered WordClouds** - Generate wordclouds for specific time periods│                    AUTOMATED DATA PIPELINE                   │

└─────────────────────────────────────────────────────────────┘

### 🤖 AI Analysis Tab                              │

- **Gemini AI Integration** - Automated sentiment analysis                    ┌─────────▼─────────┐

- **Key Insights** - Common themes and patterns in reviews                    │   Scheduler       │

- **Sentiment Scores** - Positive, negative, and neutral review classification                    │  (Every 5 min)    │

- **Recommendations** - AI-generated improvement suggestions                    └─────────┬─────────┘

                              │

## ⚙️ Scheduler Configuration              ┌───────────────┼───────────────┐

              ▼               ▼               ▼

### Built-in Scheduler (Dashboard)    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐

    │ Business 1  │  │ Business 2  │  │ Business 3  │

The dashboard includes a scheduler control panel in the sidebar:    │  API Call   │  │  API Call   │  │  API Call   │

    └──────┬──────┘  └──────┬──────┘  └──────┬──────┘

1. **Configure Collection Interval:**           │                 │                 │

   - 15 minutes (frequent updates)           └────────┬────────┴────────┬────────┘

   - 30 minutes (balanced)                    ▼                 ▼

   - 60 minutes (hourly)              ┌──────────┐      ┌──────────┐

   - 120 minutes (every 2 hours)              │   Hash   │      │   New    │

   - 180 minutes (every 3 hours)              │  Check   │──Y──▶│ Review?  │

              └──────────┘      └─────┬────┘

2. **Business Management:**                    │                 │

   - Enable/disable individual businesses                    N                 Y

   - Manual collection trigger                    │                 │

   - View last collection time                    ▼                 ▼

              ┌──────────┐      ┌──────────┐

3. **Auto-Recovery:**              │   Skip   │      │   Save   │

   - Automatically detects if scheduler crashed (container restart, etc.)              │Duplicate │      │    to    │

   - Restarts scheduler if `last_run > 2 × interval`              └──────────┘      │Database  │

   - Ensures continuous data collection                                └─────┬────┘

                                      │

### Scheduler Status File                    ┌─────────────────┴─────────────────┐

                    ▼                                   ▼

Location: `scheduler_status.json`            ┌──────────────┐                   ┌──────────────┐

            │  Streamlit   │                   │   Gemini AI  │

```json            │  Dashboard   │                   │   Analysis   │

{            └──────────────┘                   └──────────────┘

  "active": true,```

  "last_run": "2025-11-09T18:25:55.545225",

  "next_run": "2025-11-09T20:25:55.545225",## 🔍 Technical Details

  "interval_minutes": 120,

  "total_collections": 77### API vs Web Scraping Comparison

}

```| Feature | API Approach | Web Scraping |

|---------|--------------|--------------|

## 🏗️ Project Structure| **Speed** | 1-2 seconds | 30-60 seconds |

| **Reliability** | 99%+ | 85-90% |

```| **Maintenance** | Zero | High |

google-maps-scraping-1/| **Bot Detection** | None | Risk present |

├── api_pipeline/                    # 🚀 API Data Pipeline| **Data Quality** | Official | Depends |

│   ├── collectors/

│   │   └── google_maps_api.py      # Google Maps API collector### Duplicate Detection

│   ├── config/- **Method**: MD5 hash of (business + reviewer + date + text)

│   │   └── settings.py             # Configuration (businesses, API keys)- **Storage**: Database constraint + application check

│   ├── pipeline_manager.py         # Collection orchestration- **Performance**: O(1) lookup with index

│   └── scheduler.py                # Background scheduler- **Accuracy**: 100% tested

│

├── database_dashboard.py            # 📊 Streamlit dashboard (main app)## ⚠️ Important Notes

├── database_test.py                 # 💾 Database management & schema

├── background_scheduler.py          # ⏰ Scheduler control logic1. **API Keys Required**: Must configure both Google Maps and Gemini API keys

├── run_scheduler_standalone.py     # 🔧 Independent scheduler runner2. **Python 3.12+**: Recommended for best compatibility

├── run_scheduler.bat               # 🪟 Windows batch file for scheduler3. **Airflow on Linux**: For production Airflow deployment, use Linux/Docker

│4. **Place ID**: Each business needs a unique Place ID from Google Maps

├── docker-compose.yml              # 🐳 Docker Compose configuration5. **Rate Limits**: API has generous limits, no need for delays

├── Dockerfile                      # 🐳 Multi-stage Docker build

├── .dockerignore                   # 🐳 Docker build exclusions## 🐛 Troubleshooting

│

├── requirements.txt                 # 📦 Python dependencies### Common Issues

├── .env                            # 🔑 API keys (create this!)

├── .env.example                    # 📄 Environment template**1. API Key Error**

├── scheduler_config.json           # ⚙️ Scheduler configuration```bash

├── scheduler_status.json           # 📊 Scheduler runtime statusError: GOOGLE_MAPS_API_KEY not found

├── reviews.db                      # 💾 SQLite databaseSolution: Check .env file exists and contains valid API key

└── README.md                       # 📖 This file```

```

**2. No Reviews Collected**

## 🔧 Configuration Files```bash

Check: 

### `scheduler_config.json`- Place ID is correct

- Business has reviews on Google Maps

Controls scheduler behavior:- API key has Places API enabled

```

```json

{**3. Airflow Import Error (Windows)**

  "businesses": [```bash

    {Error: ImportError: cannot import name 'Styles' from 'structlog.dev'

      "place_id": "ChIJqZW8Cvb_n0ARBuUkyCzgDDg",Solution: Use simple scheduler instead: python api_pipeline/scheduler.py

      "name": "İstanbul Havalimanı",```

      "enabled": true

    },**4. Database Migration**

    {```bash

      "place_id": "ChIJ1YCMEbbJyhQRl_WtWEBrUSM",# Database automatically migrates on first run

      "name": "Sabiha Gökçen Havalimanı",# If issues occur, backup and recreate:

      "enabled": truemv reviews.db reviews.db.backup

    }python database_test.py

  ],```

  "interval_minutes": 120,

  "api_language": "tr"## 📈 Performance

}

```- **API Response Time**: 1-2 seconds per business

- **Success Rate**: 99%+ (official API)

### Adding New Businesses- **Reviews per Call**: 5 latest reviews

- **Pipeline Interval**: Configurable (default: 5 minutes)

1. **Find Place ID:**- **Duplicate Detection**: O(1) hash lookup

   - Use [Place ID Finder](https://developers.google.com/maps/documentation/places/web-service/place-id)- **Dashboard Load Time**: <1 second

   - Or search on Google Maps and extract from URL

## 🤝 Contributing

2. **Add to config:**

   Edit `scheduler_config.json` or use dashboard UI1. Fork this repository

2. Create feature branch (`git checkout -b feature/amazing-feature`)

3. **Restart scheduler:**3. Commit changes (`git commit -m 'Add amazing feature'`)

   Changes take effect on next collection cycle4. Push to branch (`git push origin feature/amazing-feature`)

5. Open Pull Request

## 🎯 Time Filter Logic

## 📄 License

### Calendar-based Categorization

This project is licensed under the MIT License.

Reviews are categorized using **calendar dates**, not 24-hour periods:

## 🆘 Support

- **Today** - Reviews from current calendar date (00:00 to 23:59 today)

- **Yesterday** - Reviews from previous calendar date (00:00 to 23:59 yesterday)For questions:

- **This Week** - Reviews from current week (Monday to Sunday)- Open GitHub Issues

- **This Month** - Reviews from current month (1st to last day)- Run test scripts

- **This Year** - Reviews from current year (January 1st to December 31st)- Use debug mode



### Cumulative Filtering## 📚 Additional Resources



When selecting a time filter, you see **ALL reviews** within that timeframe:- **Detailed API Pipeline Docs**: See `API_PIPELINE_README.md`

- **Google Maps API**: [Places API Documentation](https://developers.google.com/maps/documentation/places/web-service/overview)

- **"This Week" filter** → Shows all reviews from last 7 days (includes Today + Yesterday + This Week categories)- **Gemini API**: [Gemini API Guide](https://ai.google.dev/docs)

- **"This Month" filter** → Shows all reviews from last 30 days (includes Today + Yesterday + This Week + This Month)- **Airflow**: [Apache Airflow Documentation](https://airflow.apache.org/docs/)

- **"Yesterday" filter** → Shows ONLY reviews from yesterday (not cumulative)

## 🎉 Migration from Web Scraping

Implementation: `get_reviews_by_time_filter()` function in `database_dashboard.py`

This project evolved from web scraping to API-based pipeline:

## 🐛 Troubleshooting- **Before**: Selenium + Firefox (30-60s, maintenance heavy)

- **After**: Google Maps API (1-2s, zero maintenance)

### Docker Issues

Old scraping files archived in: `archived_scripts/` (if needed for reference)

**1. Container won't start**

```bash---

# Check logs

docker-compose logs dashboard**Project Status**: ✅ Production-ready API pipeline with automated collection

**Last Updated**: October 2025 - API Data Pipeline v2.0

# Common issue: Port already in use
# Solution: Stop other services on port 8501 or change port in docker-compose.yml
```

**2. Scheduler not running**
```bash
# Verify scheduler status
docker exec google-maps-dashboard cat /app/scheduler_status.json

# If active=false or last_run is old:
# - Restart container: docker-compose restart dashboard
# - Dashboard will auto-recover scheduler on next load
```

**3. Database not persisting**
```bash
# Check volume
docker volume ls | grep google-maps

# Recreate volume
docker-compose down -v
docker-compose up -d
```

### Local Installation Issues

**1. API Key Error**
```bash
Error: GOOGLE_MAPS_API_KEY not found
Solution: Check .env file exists and contains valid API key
```

**2. No Reviews Collected**
```bash
Check: 
- Place ID is correct
- Business has reviews on Google Maps
- API key has Places API enabled
- Check api_pipeline/config/settings.py for business list
```

**3. Module Import Error**
```bash
Error: ModuleNotFoundError: No module named 'api_pipeline'
Solution: Ensure you're running from project root directory
```

**4. Scheduler Shows "Active" But Not Collecting**
```bash
# Check last_run timestamp
# If older than 2x interval, auto-recovery will trigger

# Manual restart:
1. Stop scheduler (dashboard sidebar)
2. Wait 5 seconds
3. Start scheduler again
```

## 📈 Performance

- **API Response Time**: 1-2 seconds per business
- **Success Rate**: 99%+ (official Google API)
- **Reviews per Call**: Up to 5 most recent reviews per business
- **Scheduler Intervals**: 15, 30, 60, 120, 180 minutes (configurable)
- **Dashboard Load Time**: <1 second (cached data)
- **Database Size**: ~100KB per 1000 reviews

## 🔍 Technical Details

### API vs Web Scraping Comparison

| Feature | API Approach | Web Scraping |
|---------|--------------|--------------|
| **Speed** | 1-2 seconds | 30-60 seconds |
| **Reliability** | 99%+ | 85-90% |
| **Maintenance** | Zero | High |
| **Bot Detection** | None | Risk present |
| **Data Quality** | Official | Depends |
| **Rate Limits** | Generous | Restrictive |

### Scheduler Auto-Recovery

How it works:

1. Dashboard checks `scheduler_status.json` on load
2. If `active: true` but `(now - last_run) > (interval × 2)`:
   - Scheduler thread crashed (container restart, exception, etc.)
   - Auto-recovery triggers: `scheduler.start()`
3. New collection cycle begins immediately
4. Status updates with new `last_run` and `next_run`

This ensures zero downtime even after container restarts or crashes.

### Database Schema

**reviews table:**
```sql
CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    business_name TEXT NOT NULL,
    place_id TEXT NOT NULL,
    reviewer_name TEXT,
    review_text TEXT,
    rating INTEGER,
    review_date TEXT,
    relative_time TEXT,
    timestamp TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**businesses table:**
```sql
CREATE TABLE businesses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    place_id TEXT NOT NULL UNIQUE,
    enabled INTEGER DEFAULT 1,
    last_collection TEXT,
    total_reviews INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## ⚠️ Important Notes

1. **API Keys Required**: Must configure both Google Maps and Gemini API keys in `.env`
2. **Docker Recommended**: For production deployment, use Docker to ensure consistency
3. **Place ID Required**: Each business needs a unique Place ID from Google Maps
4. **Rate Limits**: Google Maps API has generous free tier (check Google Cloud Console for quotas)
5. **Time Zones**: Dashboard uses `Europe/Istanbul` timezone (configurable in code)
6. **Auto-recovery**: Scheduler automatically restarts after container restart (detects stale status)

## 🤝 Contributing

1. Fork this repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues or questions:
- Open GitHub Issues
- Check troubleshooting section
- Review scheduler status logs

## 📚 Additional Resources

- [Google Maps Places API Documentation](https://developers.google.com/maps/documentation/places/web-service/overview)
- [Google Gemini API Guide](https://ai.google.dev/docs)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

---

**Project Status**: ✅ Production-ready with Docker deployment and auto-recovery
**Last Updated**: November 2025
**Current Version**: v2.0 - Docker Deployment with Auto-Recovery
