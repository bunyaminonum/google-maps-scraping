"""
Configuration Management
Centralized settings for API data pipeline
"""

import os
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Main configuration class"""
    
    # API Keys
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'reviews.db')
    
    # API Settings
    API_LANGUAGE = os.getenv('API_LANGUAGE', 'tr')
    API_MAX_RETRIES = int(os.getenv('API_MAX_RETRIES', '3'))
    API_RETRY_DELAY = int(os.getenv('API_RETRY_DELAY', '2'))
    
    # Collection Schedule
    COLLECTION_INTERVAL_MINUTES = int(os.getenv('COLLECTION_INTERVAL_MINUTES', '5'))
    
    # Airflow
    AIRFLOW_SCHEDULE = os.getenv('AIRFLOW_SCHEDULE', '*/5 * * * *')  # Every 5 minutes
    AIRFLOW_START_DATE = os.getenv('AIRFLOW_START_DATE', '2025-10-31')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        if not cls.GOOGLE_MAPS_API_KEY:
            print("❌ GOOGLE_MAPS_API_KEY not configured")
            return False
        return True
    
    @classmethod
    def summary(cls) -> Dict:
        """Get configuration summary"""
        return {
            'api_key_configured': bool(cls.GOOGLE_MAPS_API_KEY),
            'gemini_key_configured': bool(cls.GEMINI_API_KEY),
            'database': cls.DATABASE_PATH,
            'language': cls.API_LANGUAGE,
            'interval_minutes': cls.COLLECTION_INTERVAL_MINUTES,
            'airflow_schedule': cls.AIRFLOW_SCHEDULE
        }


class BusinessConfig:
    """Business places configuration"""
    
    # List of businesses to track
    # Format: (place_id, business_name)
    BUSINESSES: List[tuple] = [
        ("ChIJqZW8Cvb_n0ARBuUkyCzgDDg", "İstanbul Havalimanı"),
        # Add more businesses here
    ]
    
    @classmethod
    def add_business(cls, place_id: str, business_name: str):
        """Add a new business to track"""
        cls.BUSINESSES.append((place_id, business_name))
    
    @classmethod
    def get_business_list(cls) -> List[Dict]:
        """Get formatted business list"""
        return [
            {'place_id': pid, 'name': name}
            for pid, name in cls.BUSINESSES
        ]
    
    @classmethod
    def get_all_businesses_from_db(cls, db_path: str = None) -> List[tuple]:
        """Get all unique businesses from database"""
        import sqlite3
        
        if db_path is None:
            db_path = Config.DATABASE_PATH
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get unique businesses with their place_ids
            # Use GROUP BY to get only one entry per business_name
            # Prefer place_ids that start with 'ChIJ' (real Google place IDs)
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN business_url LIKE 'ChIJ%' THEN business_url
                        ELSE (SELECT business_url FROM reviews r2 
                              WHERE r2.business_name = reviews.business_name 
                              AND r2.business_url LIKE 'ChIJ%' LIMIT 1)
                    END as place_id,
                    business_name
                FROM reviews 
                WHERE business_name IS NOT NULL 
                AND business_name != ''
                GROUP BY business_name
                ORDER BY business_name
            """)
            
            businesses = cursor.fetchall()
            conn.close()
            
            # Merge with static list
            all_businesses = list(cls.BUSINESSES)
            
            # Add database businesses that aren't in static list
            existing_names = {name for _, name in all_businesses}
            for place_id, name in businesses:
                if name not in existing_names:
                    all_businesses.append((place_id or '', name))
            
            return all_businesses
            
        except Exception as e:
            print(f"Error loading businesses from DB: {e}")
            return cls.BUSINESSES
    
    @classmethod
    def get_place_ids(cls) -> List[str]:
        """Get list of place IDs"""
        return [pid for pid, _ in cls.BUSINESSES]


# Example .env file template
ENV_TEMPLATE = """
# Google Maps API Data Pipeline Configuration

# API Keys
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Database
DATABASE_PATH=reviews.db

# API Settings
API_LANGUAGE=tr
API_MAX_RETRIES=3
API_RETRY_DELAY=2

# Collection Schedule (minutes)
COLLECTION_INTERVAL_MINUTES=5

# Airflow Schedule (cron format)
AIRFLOW_SCHEDULE=*/5 * * * *
AIRFLOW_START_DATE=2025-10-31

# Logging
LOG_LEVEL=INFO
"""


def create_env_template(filepath: str = '.env.pipeline'):
    """Create .env template file"""
    with open(filepath, 'w') as f:
        f.write(ENV_TEMPLATE.strip())
    print(f"✅ Created template: {filepath}")


if __name__ == "__main__":
    print("📋 Current Configuration:")
    print("=" * 50)
    
    for key, value in Config.summary().items():
        print(f"{key:30s}: {value}")
    
    print("\n📍 Tracked Businesses:")
    print("=" * 50)
    
    for i, business in enumerate(BusinessConfig.get_business_list(), 1):
        print(f"{i}. {business['name']}")
        print(f"   Place ID: {business['place_id']}")
