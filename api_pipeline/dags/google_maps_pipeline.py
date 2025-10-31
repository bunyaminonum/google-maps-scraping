"""
Google Maps API Data Pipeline DAG
Automated review collection with Airflow
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_pipeline.pipeline_manager import APIPipelineManager

# Default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 10, 31),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=2),
}

# DAG definition
dag = DAG(
    'google_maps_api_pipeline',
    default_args=default_args,
    description='Collect Google Maps reviews via API every 5 minutes',
    schedule_interval=timedelta(minutes=5),  # Every 5 minutes
    catchup=False,
    tags=['google-maps', 'api', 'data-pipeline'],
)


def run_collection_pipeline():
    """Execute the API collection pipeline"""
    try:
        # Initialize and run pipeline
        pipeline = APIPipelineManager()
        result = pipeline.run_pipeline()
        
        if result['success']:
            print(f"✅ Pipeline completed successfully!")
            print(f"📊 Stats: {result['stats']}")
            return result['stats']
        else:
            print(f"❌ Pipeline failed!")
            raise Exception("Pipeline execution failed")
            
    except Exception as e:
        print(f"❌ Pipeline error: {e}")
        raise


# Task definition
collect_reviews_task = PythonOperator(
    task_id='collect_google_maps_reviews',
    python_callable=run_collection_pipeline,
    dag=dag,
)

# Task dependencies (single task in this case)
collect_reviews_task
