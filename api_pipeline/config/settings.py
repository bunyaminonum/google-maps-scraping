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
