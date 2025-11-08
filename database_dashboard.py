"""
🎯 Google Maps Reviews - API-Powered Dashboard
Real-time analysis with Google Maps Places API integration
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from datetime import datetime, timedelta
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np
import sqlite3
from database_test import ReviewsDatabase
from api_pipeline.collectors.google_maps_api import GoogleMapsAPICollector
from api_pipeline.config.settings import Config, BusinessConfig
import pytz
import os
import time
from dotenv import load_dotenv

# Gemini AI import (conditional - only if needed)
GEMINI_AVAILABLE = False
try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        import google.generativeai as genai
        GEMINI_AVAILABLE = True
    except ImportError:
        pass

# Page configuration
st.set_page_config(
    page_title="🎯 Google Maps Reviews - API Dashboard",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-left: 4px solid #667eea;
}

.success-box {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 5px;
    padding: 10px;
    margin: 10px 0;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    padding-left: 12px;
    padding-right: 12px;
}

/* Pulse animation for "in progress" indicator */
@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.7;
    }
}

/* Smooth transitions */
.stButton button {
    transition: all 0.3s ease;
}

.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

def load_data_from_database(db_path="reviews.db"):
    """Load all data from database"""
    try:
        db = ReviewsDatabase(db_path)
        
        # Get all reviews
        df = db.get_all_reviews()
        
        if df.empty:
            return None, None
        
        # Get session statistics
        stats = db.get_statistics()
        
        return df, stats
    
    except Exception as e:
        st.error(f"❌ Error loading database: {str(e)}")
        return None, None

def analyze_reviews_with_ai(reviews_text, business_name, time_period, custom_instructions=None, 
                           rating_filter=None, sentiment_filter=None, min_text_length=None):
    """Analyze reviews using Gemini AI with context-aware prompts based on filters"""
    if not GEMINI_AVAILABLE:
        return {
            "error": "Gemini AI is not available. Please install: pip install google-generativeai",
            "success": False
        }
    
    try:
        # Load API key
        load_dotenv()
        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            return {
                "error": "GEMINI_API_KEY not found. Please configure .env file.",
                "success": False
            }
        
        # Initialize Gemini client (support both import styles)
        try:
            # New API style
            client = genai.Client(api_key=api_key)
            model_name = "gemini-2.0-flash"
        except AttributeError:
            # Old API style fallback
            genai.configure(api_key=api_key)
            client = genai
            model_name = "gemini-2.0-flash"
        
        # Build filter context for AI
        filter_context = []
        
        if time_period and time_period != 'All':
            filter_context.append(f"📅 Time Period: {time_period} - Focus on RECENT trends and current customer experience")
        
        if rating_filter and rating_filter != 'All':
            filter_context.append(f"⭐ Rating Filter: {rating_filter} stars - These reviews specifically rated {rating_filter}/5")
        
        if sentiment_filter and sentiment_filter != 'All':
            if 'Positive' in sentiment_filter:
                filter_context.append(f"😊 Sentiment: POSITIVE reviews only (4-5★) - Analyze what makes customers HAPPY and what they PRAISE")
            elif 'Negative' in sentiment_filter:
                filter_context.append(f"😞 Sentiment: NEGATIVE reviews only (1-2★) - Focus on PROBLEMS, COMPLAINTS, and URGENT ISSUES that need attention")
            elif 'Neutral' in sentiment_filter:
                filter_context.append(f"😐 Sentiment: NEUTRAL reviews (3★) - Identify areas that are OKAY but could be IMPROVED")
        
        if min_text_length and min_text_length > 10:
            filter_context.append(f"📝 Text Filter: Minimum {min_text_length} characters - Only detailed reviews included")
        
        filter_section = ""
        if filter_context:
            filter_section = f"""

⚙️ **ANALYSIS CONTEXT - FILTERS APPLIED:**
{chr(10).join([f"   {fc}" for fc in filter_context])}

🎯 **IMPORTANT:** Your analysis should be SPECIFICALLY TAILORED to these filters.
- If analyzing POSITIVE reviews: Focus on strengths, what works well, success patterns
- If analyzing NEGATIVE reviews: Focus on problems, complaints, urgent fixes needed
- If analyzing specific time period: Mention trends for THAT period
- If analyzing specific rating: Explain what makes customers give THAT rating
"""
        
        # Build custom instructions section
        custom_section = ""
        if custom_instructions and custom_instructions.strip():
            custom_section = f"""

✍️ **USER'S CUSTOM INSTRUCTIONS:**
{custom_instructions.strip()}

👉 Please prioritize these specific instructions in your analysis.
"""
        
        # Build smart prompt based on filters
        if sentiment_filter and 'Negative' in sentiment_filter:
            analysis_focus = """
1. **Critical Issues Identified** ⚠️
   - List URGENT problems mentioned by unhappy customers
   - Severity assessment (Critical/High/Medium)
   - Frequency of each complaint

2. **Root Causes Analysis** 🔍
   - Why are customers giving 1-2 stars?
   - Common patterns in complaints
   - Systemic vs isolated issues

3. **Impact on Customer Experience** 💔
   - How these issues affect overall satisfaction
   - Emotional tone of complaints
   - Trust and reputation concerns

4. **Actionable Solutions** ✅
   - Specific recommendations to fix each issue
   - Quick wins vs long-term improvements
   - Priority ranking

5. **Comparison Context** 📊
   - Are issues getting worse or better over time?
   - Most frustrated customer segments

6. **Executive Summary** 📋
   - Top 3 urgent actions needed
   - Risk assessment
"""
        elif sentiment_filter and 'Positive' in sentiment_filter:
            analysis_focus = """
1. **Key Success Factors** 🌟
   - What are customers praising most?
   - Unique selling points mentioned
   - Exceeded expectations

2. **Customer Delight Moments** 😊
   - Standout positive experiences
   - Emotional highlights
   - Word-of-mouth triggers

3. **Competitive Advantages** 💪
   - What sets this business apart?
   - Strengths to double down on
   - Brand differentiators

4. **Best Practices Identified** ✨
   - Patterns in excellent service
   - Successful processes
   - Staff behaviors that work

5. **Growth Opportunities** 🚀
   - How to amplify what works
   - Expansion suggestions
   - Marketing insights

6. **Executive Summary** 📋
   - Top 3 strengths to maintain
   - Success patterns to scale
"""
        else:
            analysis_focus = """
1. **Overall Sentiment Analysis** 📊
   - Positive/Negative/Neutral percentage breakdown
   - Emotional tone and customer mood
   - Satisfaction trends

2. **Key Themes & Topics** 🏷️
   - Top 5-7 most mentioned themes
   - For each theme: Positive ✅ Negative ❌ or Mixed ⚖️
   - Theme importance ranking

3. **Strengths & Wins** 💪
   - Top 3-5 things customers love
   - Competitive advantages
   - Consistent praise patterns

4. **Issues & Pain Points** ⚠️
   - Top 3-5 complaints and problems
   - Urgency level of each issue
   - Impact on customer satisfaction

5. **Customer Behavior Insights** 🧠
   - Usage patterns and preferences
   - Customer segment observations
   - Behavioral trends

6. **Actionable Recommendations** 🎯
   - Specific improvement suggestions
   - Quick wins vs strategic changes
   - Priority actions

7. **Executive Summary** 📋
   - 3-4 sentence overview
   - Key takeaways
   - Strategic direction
"""
        
        # Create intelligent, context-aware prompt
        prompt = f"""
🎯 **CUSTOMER REVIEW ANALYSIS TASK**

📍 **Business:** {business_name}
📅 **Time Period:** {time_period}
📊 **Sample Size:** {len(reviews_text)} reviews
{filter_section}
{custom_section}

---

📝 **REVIEWS TO ANALYZE:**

{chr(10).join([f"{i+1}. {review}" for i, review in enumerate(reviews_text)])}

---

🔍 **YOUR ANALYSIS SHOULD INCLUDE:**
{analysis_focus}

---

⚡ **ANALYSIS GUIDELINES:**
- Be SPECIFIC: Use exact quotes from reviews when relevant
- Be ACTIONABLE: Provide concrete recommendations, not generic advice
- Be CONTEXTUAL: Remember the filters applied (time, rating, sentiment)
- Be BALANCED: Even in filtered data, note any counter-patterns
- Be INSIGHTFUL: Go beyond surface-level observations
- Use EMOJIS and formatting for clarity
- Provide PERCENTAGES and NUMBERS when possible

📌 Start your analysis now:
"""
        
        # Generate analysis (support both API styles)
        try:
            # New API style
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
            analysis_text = response.text
        except AttributeError:
            # Old API style
            model = client.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            analysis_text = response.text
        
        return {
            "success": True,
            "analysis": analysis_text,
            "reviews_count": len(reviews_text)
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

def parse_relative_time_to_timestamp(relative_time_str):
    """Convert Turkish relative time expressions to timestamp"""
    try:
        # Turkey timezone
        tr_tz = pytz.timezone('Europe/Istanbul')
        now = datetime.now(tr_tz)
        
        # Clean text and convert to lowercase
        text = relative_time_str.lower().strip()
        
        # Turkish time patterns
        patterns = [
            (r'(\d+)\s*saat\s*önce', 'hours'),
            (r'(\d+)\s*gün\s*önce', 'days'),
            (r'(\d+)\s*hafta\s*önce', 'weeks'),
            (r'(\d+)\s*ay\s*önce', 'months'),
            (r'(\d+)\s*yıl\s*önce', 'years'),
            (r'bir\s*saat\s*önce', 'hour'),
            (r'bir\s*gün\s*önce', 'day'),
            (r'bir\s*hafta\s*önce', 'week'),
            (r'bir\s*ay\s*önce', 'month'),
            (r'bir\s*yıl\s*önce', 'year'),
        ]
        
        for pattern, unit in patterns:
            match = re.search(pattern, text)
            if match:
                if unit.endswith('s'):  # Çoğul
                    number = int(match.group(1))
                    unit = unit[:-1]  # 's' harfini kaldır
                else:  # Tekil
                    number = 1
                
                if unit == 'hour':
                    delta = timedelta(hours=number)
                elif unit == 'day':
                    delta = timedelta(days=number)
                elif unit == 'week':
                    delta = timedelta(weeks=number)
                elif unit == 'month':
                    delta = timedelta(days=number * 30)
                elif unit == 'year':
                    delta = timedelta(days=number * 365)
                else:
                    continue
                
                result_time = now - delta
                return result_time
        
        # Eğer hiçbir kalıp uymazsa şu anki zamanı döndür
        return now
        
    except Exception as e:
        # Hata durumunda şu anki zamanı döndür
        tr_tz = pytz.timezone('Europe/Istanbul')
        return datetime.now(tr_tz)

def categorize_timestamp(timestamp):
    """Categorize timestamp into time periods with detailed granularity"""
    try:
        tr_tz = pytz.timezone('Europe/Istanbul')
        now = datetime.now(tr_tz)
        
        # Make timestamp timezone-aware if naive
        if timestamp.tzinfo is None:
            timestamp = tr_tz.localize(timestamp)
        
        # Calculate difference
        diff = now - timestamp
        
        # Detailed categorization matching filter options
        if diff.total_seconds() < 3600:  # Less than 1 hour
            return "Last Hour"
        elif diff.days == 0:  # Same day but more than 1 hour ago
            return "Today"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days <= 7:
            return "This Week"
        elif diff.days <= 30:
            return "This Month"
        elif diff.days <= 90:
            return "Last 3 Months"
        elif diff.days <= 180:
            return "Last 6 Months"
        elif diff.days <= 365:
            return "This Year"
        else:
            return "Older"
    except Exception as e:
        return "Time Unknown"

def run_api_collector():
    """Collect data via Google Maps API"""
    with st.spinner("🚀 Collecting data via Google Maps API..."):
        try:
            # Load API key from environment
            load_dotenv()
            api_key = os.getenv('GOOGLE_MAPS_API_KEY')
            
            if not api_key:
                st.error("❌ GOOGLE_MAPS_API_KEY not found in .env file!")
                st.info("💡 Please add your API key to .env file:\nGOOGLE_MAPS_API_KEY=your_key_here")
                return False
            
            # Get Place ID and business name
            place_id = st.session_state.get('place_id', '')
            business_name = st.session_state.get('business_name', '')
            
            if not place_id or not business_name:
                st.error("❌ Business name and Place ID are required!")
                st.info("💡 Place ID example: ChIJqZW8Cvb_n0ARBuUkyCzgDDg")
                return False
            
            # Initialize API collector with API key
            collector = GoogleMapsAPICollector(api_key=api_key)
            
            # Collect reviews
            result = collector.collect_reviews(place_id, business_name)
            
            if result and result.get("success", False):
                reviews = result.get("reviews", [])
                
                # Save to database
                db = ReviewsDatabase("reviews.db")
                
                new_count = 0
                duplicate_count = 0
                
                for review in reviews:
                    # Generate hash for duplicate check
                    review_hash = db.generate_review_hash(
                        business_name,
                        review.author_name,
                        review.relative_time,
                        review.text or ""
                    )
                    
                    # Check if exists
                    if not db.check_review_exists(review_hash):
                        # Convert timestamp to datetime if needed
                        timestamp_obj = review.timestamp if hasattr(review, 'timestamp') else None
                        
                        # Calculate time category
                        time_category = categorize_timestamp(timestamp_obj) if timestamp_obj else "Unknown"
                        
                        # Prepare review data dictionary with correct field names
                        review_data = {
                            'business_name': business_name,
                            'business_url': place_id,  # Store Place ID here for future reference
                            'reviewer_name': review.author_name,
                            'rating': review.rating,
                            'review_date': review.relative_time,  # date_original expects 'review_date' key
                            'review_text': review.text or "",
                            'timestamp_parsed': timestamp_obj.isoformat() if timestamp_obj else None,
                            'time_category': time_category,
                            'session_id': f'dashboard_collection_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                            'review_hash': review_hash
                        }
                        
                        # Add new review with dictionary
                        db.add_review(review_data)
                        new_count += 1
                    else:
                        duplicate_count += 1
                
                st.success(f"✅ API collection completed!")
                st.info(f"📊 Total: {len(reviews)} reviews fetched")
                st.info(f"💾 New: {new_count} saved | ⏭️ Duplicates: {duplicate_count} skipped")
                
                # Refresh page
                st.rerun()
                return True
            else:
                error_msg = result.get("error", "Unknown error") if result else "Operation failed"
                st.error(f"❌ API collection failed: {error_msg}")
                return False
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            return False

def main():
    """Main dashboard function"""
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>� Google Maps Reviews - API Dashboard</h1>
        <p>Real-time analysis powered by Google Maps Places API</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - Data management
    with st.sidebar:
        st.markdown("## 🎯 Data Management")
        
        # Database status
        df, stats = load_data_from_database()
        
        if df is not None and not df.empty:
            st.success(f"✅ Found {len(df)} reviews in database")
            
            # Statistics
            st.markdown("### 📊 General Statistics")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Total Reviews", stats.get('total_reviews', 0))
                st.metric("Average Rating", f"{stats.get('average_rating', 0):.1f}")
            
            with col2:
                st.metric("Text Reviews", stats.get('text_reviews', 0))
                st.metric("Business Count", stats.get('total_businesses', 1))
            
        else:
            st.warning("⚠️ No data in database yet")
        
        st.markdown("---")
        
        # Business Management Section
        st.markdown("### 🏢 Business Management")
        
        db = ReviewsDatabase("reviews.db")
        
        # Quick stats
        all_biz = db.get_all_businesses(enabled_only=False)
        enabled_count = sum(1 for b in all_biz if b['enabled'])
        disabled_count = len(all_biz) - enabled_count
        
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("Total", len(all_biz))
        with col_stat2:
            st.metric("Enabled", enabled_count, delta=f"-{disabled_count} disabled" if disabled_count > 0 else None)
        
        # Tabs for different operations
        business_tab1, business_tab2 = st.tabs(["📋 List", "➕ Add New"])
        
        with business_tab1:
            # List all businesses
            all_businesses_crud = db.get_all_businesses()
            
            if all_businesses_crud:
                st.caption(f"Total: {len(all_businesses_crud)} businesses")
                
                for biz in all_businesses_crud:
                    with st.expander(f"{'✅' if biz['enabled'] else '❌'} {biz['name']}", expanded=False):
                        st.caption(f"**Place ID:** `{biz['place_id']}`")
                        st.caption(f"**Status:** {'Enabled' if biz['enabled'] else 'Disabled'}")
                        st.caption(f"**ID:** {biz['id']}")
                        
                        # Action buttons
                        col_edit1, col_edit2, col_edit3 = st.columns(3)
                        
                        with col_edit1:
                            if st.button("🔄 Toggle", key=f"toggle_{biz['id']}", help="Enable/Disable"):
                                result = db.toggle_business(biz['id'])
                                if result['success']:
                                    st.success(result['message'])
                                    time.sleep(0.5)
                                    st.rerun()
                                else:
                                    st.error(result['error'])
                        
                        with col_edit2:
                            if st.button("✏️ Edit", key=f"edit_{biz['id']}", help="Edit business"):
                                st.session_state[f'editing_{biz["id"]}'] = True
                                st.rerun()
                        
                        with col_edit3:
                            if st.button("🗑️ Delete", key=f"delete_{biz['id']}", help="Delete business"):
                                result = db.delete_business(biz['id'])
                                if result['success']:
                                    st.success(result['message'])
                                    time.sleep(0.5)
                                    st.rerun()
                                else:
                                    st.error(result['error'])
                        
                        # Edit form (if editing)
                        if st.session_state.get(f'editing_{biz["id"]}', False):
                            st.markdown("**Edit Business:**")
                            
                            new_name = st.text_input("Name", value=biz['name'], key=f"edit_name_{biz['id']}")
                            new_place_id = st.text_input("Place ID", value=biz['place_id'], key=f"edit_place_{biz['id']}")
                            
                            col_save, col_cancel = st.columns(2)
                            
                            with col_save:
                                if st.button("💾 Save", key=f"save_{biz['id']}"):
                                    result = db.update_business(
                                        biz['id'],
                                        name=new_name if new_name != biz['name'] else None,
                                        place_id=new_place_id if new_place_id != biz['place_id'] else None
                                    )
                                    if result['success']:
                                        st.success(result['message'])
                                        st.session_state[f'editing_{biz["id"]}'] = False
                                        time.sleep(0.5)
                                        st.rerun()
                                    else:
                                        st.error(result['error'])
                            
                            with col_cancel:
                                if st.button("❌ Cancel", key=f"cancel_{biz['id']}"):
                                    st.session_state[f'editing_{biz["id"]}'] = False
                                    st.rerun()
            else:
                st.info("No businesses yet. Add one in the 'Add New' tab.")
        
        with business_tab2:
            # Add new business form
            st.markdown("**Add New Business:**")
            
            new_biz_name = st.text_input("Business Name", key="new_biz_name", placeholder="e.g., Starbucks")
            new_biz_place_id = st.text_input("Google Place ID", key="new_biz_place_id", placeholder="ChIJ...")
            
            st.caption("💡 Get Place ID from: [Place ID Finder](https://developers.google.com/maps/documentation/places/web-service/place-id)")
            
            if st.button("➕ Add Business", type="primary", key="add_new_business"):
                if new_biz_name and new_biz_place_id:
                    if new_biz_place_id.startswith('ChIJ'):
                        result = db.add_business(new_biz_name, new_biz_place_id, enabled=True)
                        if result['success']:
                            st.success(f"✅ {new_biz_name} added successfully!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {result['error']}")
                    else:
                        st.error("❌ Place ID must start with 'ChIJ'")
                else:
                    st.warning("⚠️ Please fill in both fields")
        
        st.markdown("---")
        
        # API data collection
        st.markdown("### 🚀 Collect Data via API")
        
        st.info("💡 Using Google Maps Places API (fast & reliable)")
        
        business_name = st.text_input(
            "Business Name:",
            value="İstanbul Havalimanı",
            key="business_name",
            help="Enter the business name for identification"
        )
        
        place_id = st.text_input(
            "Google Maps Place ID:",
            value="ChIJqZW8Cvb_n0ARBuUkyCzgDDg",
            key="place_id",
            help="Enter the Place ID from Google Maps"
        )
        
        st.caption("📍 How to find Place ID: [Use Place ID Finder](https://developers.google.com/maps/documentation/places/web-service/place-id)")
        
        if st.button("🚀 Collect Latest Reviews", type="primary"):
            run_api_collector()
        
        st.markdown("---")
        
        # Quick add from configured businesses (from database)
        # Force refresh from database each time to show new additions
        all_businesses_quick = BusinessConfig.get_all_businesses_from_db()
        
        if all_businesses_quick:
            st.markdown("### ⚡ Quick Collect")
            st.caption(f"All businesses ({len(all_businesses_quick)} total):")
            
            # Show last update time
            st.caption(f"🔄 Updated: {datetime.now().strftime('%H:%M:%S')}")
            
            for idx, (pid, bname) in enumerate(all_businesses_quick):
                if st.button(f"📍 {bname}", key=f"quick_{idx}"):
                    # Trigger collection
                    with st.spinner(f"Collecting reviews from {bname}..."):
                        try:
                            load_dotenv()
                            api_key = os.getenv('GOOGLE_MAPS_API_KEY')
                            if api_key:
                                collector = GoogleMapsAPICollector(api_key=api_key)
                                result = collector.collect_reviews(pid, bname)
                                
                                if result and result.get('success'):
                                    # Save to database
                                    db = ReviewsDatabase("reviews.db")
                                    reviews = result.get('reviews', [])
                                    
                                    new_count = 0
                                    dup_count = 0
                                    
                                    for review in reviews:
                                        review_hash = db.generate_review_hash(
                                            bname, review.author_name, review.relative_time, review.text or ""
                                        )
                                        
                                        if not db.check_review_exists(review_hash):
                                            timestamp_obj = review.timestamp if hasattr(review, 'timestamp') else None
                                            time_category = categorize_timestamp(timestamp_obj) if timestamp_obj else "Unknown"
                                            
                                            review_data = {
                                                'business_name': bname,
                                                'business_url': pid,  # Store Place ID
                                                'reviewer_name': review.author_name,
                                                'rating': review.rating,
                                                'review_date': review.relative_time,
                                                'review_text': review.text or "",
                                                'timestamp_parsed': timestamp_obj.isoformat() if timestamp_obj else None,
                                                'time_category': time_category,
                                                'session_id': f'quick_collect_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                                                'review_hash': review_hash
                                            }
                                            db.add_review(review_data)
                                            new_count += 1
                                        else:
                                            dup_count += 1
                                    
                                    st.success(f"✅ Collected! New: {new_count}, Duplicates: {dup_count}")
                                else:
                                    error = result.get('error', 'Unknown error') if result else 'No response'
                                    st.error(f"❌ Collection failed: {error}")
                            else:
                                st.error("❌ API key not found")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                    
                    # Refresh to show updated data
                    time.sleep(1)
                    st.rerun()
        
        st.markdown("---")
        
        # Auto-Scheduler Section (Background Service)
        st.markdown("### ⏰ Background Auto Scheduler")
        
        # Import background scheduler
        from background_scheduler import BackgroundScheduler
        import json
        
        # Load scheduler status from file
        scheduler_status = {}
        if os.path.exists('scheduler_status.json'):
            try:
                with open('scheduler_status.json', 'r') as f:
                    scheduler_status = json.load(f)
            except:
                scheduler_status = {'active': False}
        
        # Initialize scheduler
        scheduler = BackgroundScheduler()
        current_config = scheduler.get_config()
        
        # ⚙️ Configuration Section
        with st.expander("⚙️ Scheduler Settings", expanded=not scheduler_status.get('active', False)):
            st.markdown("**Configure Collection Behavior:**")
            
            # Interval selection
            col_int1, col_int2 = st.columns([2, 1])
            with col_int1:
                interval_options = {
                    15: "⚡ Fast - Every 15 minutes",
                    30: "⚖️ Balanced - Every 30 minutes",
                    60: "🕐 Hourly - Every hour",
                    120: "🕑 Slow - Every 2 hours",
                    180: "🕒 Very Slow - Every 3 hours"
                }
                selected_interval = st.selectbox(
                    "Collection Interval",
                    options=list(interval_options.keys()),
                    format_func=lambda x: interval_options[x],
                    index=list(interval_options.keys()).index(current_config.get('interval_minutes', 30)),
                    key="scheduler_interval"
                )
            
            with col_int2:
                st.metric("Interval", f"{selected_interval} min")
            
            # Business selection
            st.markdown("**Select Businesses to Monitor:**")
            
            # Get all available businesses from database (includes manual additions)
            # Force refresh from database to show newly added businesses
            all_businesses = BusinessConfig.get_all_businesses_from_db()
            business_names = [name for _, name in all_businesses]
            
            # Show business count and last update
            st.caption(f"📊 {len(business_names)} businesses available • Updated: {datetime.now().strftime('%H:%M:%S')}")
            
            if business_names:
                # Current enabled businesses from config
                current_enabled = current_config.get('enabled_businesses', [])
                
                # Filter to only include businesses that exist in current business_names
                # (in case some were disabled or deleted)
                valid_current_enabled = [b for b in current_enabled if b in business_names]
                
                # Select all / none buttons
                col_sel1, col_sel2, col_sel3 = st.columns(3)
                with col_sel1:
                    select_all = st.button("✅ Select All", key="select_all_biz")
                with col_sel2:
                    select_none = st.button("❌ Clear All", key="select_none_biz")
                with col_sel3:
                    st.caption(f"{len(valid_current_enabled) if valid_current_enabled else len(business_names)} selected")
                
                # Handle select all/none
                if select_all:
                    valid_current_enabled = business_names.copy()
                elif select_none:
                    valid_current_enabled = []
                
                # Multi-select for businesses
                # Use valid_current_enabled as default (only businesses that exist)
                selected_businesses = st.multiselect(
                    "Businesses",
                    options=business_names,
                    default=valid_current_enabled if valid_current_enabled else business_names,
                    key="scheduler_businesses",
                    help="Select businesses to monitor (only enabled businesses shown)"
                )
            else:
                st.warning("⚠️ No businesses configured in settings")
                selected_businesses = []
            
            # Save button
            st.markdown("---")
            col_save1, col_save2 = st.columns([1, 2])
            with col_save1:
                save_config = st.button("💾 Save Settings", type="primary", key="save_scheduler_config")
            
            with col_save2:
                if scheduler_status.get('active', False):
                    st.caption("⚠️ Settings will apply on next run")
                else:
                    st.caption("✅ Ready to save")
            
            # Save configuration
            if save_config:
                new_config = {
                    'interval_minutes': selected_interval,
                    'enabled_businesses': selected_businesses
                }
                
                if scheduler.save_config(new_config):
                    st.success(f"✅ Saved! Interval: {selected_interval} min, Businesses: {len(selected_businesses) if selected_businesses else 'All'}")
                    st.rerun()
                else:
                    st.error("❌ Failed to save configuration")
            
            # Show current config summary
            st.info(f"""
**Current Settings:**
- 📊 Interval: {current_config.get('interval_minutes', 30)} minutes
- 🏢 Businesses: {len(current_config.get('enabled_businesses', [])) if current_config.get('enabled_businesses') else 'All'}
            """)
        
        # Scheduler controls
        st.markdown("---")
        
        # Real-time status indicator
        is_running = scheduler_status.get('active', False)
        
        # Control buttons layout
        col_sch1, col_sch2, col_sch3 = st.columns([2, 1, 1])
        
        with col_sch1:
            if not is_running:
                if st.button("▶️ Start Background Scheduler", type="primary", key="start_scheduler", use_container_width=True):
                    if scheduler.start():
                        st.success("✅ Background scheduler started!")
                        time.sleep(1)  # Give it a moment to start
                        st.rerun()
                    else:
                        st.error("❌ Failed to start scheduler")
            else:
                if st.button("⏹️ Stop Background Scheduler", type="secondary", key="stop_scheduler", use_container_width=True):
                    if scheduler.stop():
                        st.info("✅ Background scheduler stopped successfully")
                        time.sleep(1)  # Give it a moment to stop
                        st.rerun()
                    else:
                        st.warning("⚠️ Scheduler may already be stopped")
        
        with col_sch2:
            if is_running:
                st.markdown("### ✅")
                st.markdown("<p style='color: #28a745; font-weight: bold; text-align: center;'>RUNNING</p>", unsafe_allow_html=True)
            else:
                st.markdown("### ⏸️")
                st.markdown("<p style='color: #6c757d; font-weight: bold; text-align: center;'>STOPPED</p>", unsafe_allow_html=True)
        
        with col_sch3:
            # Manual refresh button moved here
            if st.button("🔄 Refresh", key="manual_refresh_btn", use_container_width=True, help="Manually refresh scheduler status"):
                st.rerun()
        
        # Independent Scheduler Runner Option
        st.markdown("---")
        st.markdown("### 🚀 Run Scheduler Independently")
        
        with st.expander("ℹ️ About Independent Mode", expanded=False):
            st.info("""
**🎯 What is Independent Mode?**

Run the scheduler as a standalone process that continues even when you close the dashboard.

**✅ Advantages:**
- Scheduler runs continuously in background
- No need to keep dashboard open
- More reliable for long-term operation
- Dashboard shows live data from database

**📝 How to use:**
1. Click "Open Instructions" below
2. Follow the simple steps to launch standalone scheduler
3. Scheduler will run independently and save to database
4. Dashboard will show latest data when you open it

**⚠️ Note:** Only one scheduler instance should run at a time.
            """)
        
        col_ind1, col_ind2 = st.columns(2)
        
        with col_ind1:
            if st.button("📖 Open Instructions", key="show_independent_instructions", use_container_width=True):
                st.session_state['show_independent_guide'] = True
        
        with col_ind2:
            # Check if standalone script exists
            standalone_script = os.path.join(os.getcwd(), 'run_scheduler_standalone.py')
            if os.path.exists(standalone_script):
                st.success("✅ Script ready")
            else:
                st.warning("⚠️ Script not found")
        
        # Show instructions if requested
        if st.session_state.get('show_independent_guide', False):
            st.markdown("---")
            st.markdown("### 📖 Independent Scheduler Setup Guide")
            
            st.markdown("""
**Option 1: Using Windows Batch File (Easiest)**

1. **Close this dashboard** (optional but recommended)
2. **Double-click** `run_scheduler.bat` in project folder
3. A command window will open showing scheduler status
4. **Leave it running** - minimize the window if needed
5. **To stop**: Go to the command window and press `Ctrl+C`

---

**Option 2: Using Python Directly**

Open PowerShell in project folder and run:
```powershell
python run_scheduler_standalone.py
```

---

**Option 3: Background Process (Advanced)**

To run completely hidden in background:
```powershell
Start-Process -WindowStyle Hidden python -ArgumentList "run_scheduler_standalone.py"
```

To stop:
```powershell
Get-Process python | Where-Object {$_.CommandLine -like "*run_scheduler_standalone*"} | Stop-Process
```

---

**📊 Monitoring:**
- Check `scheduler_status.json` for real-time status
- Open dashboard anytime to view collected data
- Scheduler logs are saved in status file

**⚠️ Important:**
- Only run ONE scheduler instance at a time
- If dashboard scheduler is running, stop it before starting independent mode
            """)
            
            if st.button("✅ Got it, close instructions", key="close_independent_guide"):
                st.session_state['show_independent_guide'] = False
                st.rerun()
        
        # Show scheduler status from file
        st.markdown("---")
        if scheduler_status.get('active', False):
            st.markdown("**📊 Scheduler Status:**")
            
            # Status metrics in columns
            col_s1, col_s2, col_s3 = st.columns(3)
            
            with col_s1:
                total_runs = scheduler_status.get('total_collections', 0)
                st.metric("Total Runs", total_runs)
            
            with col_s2:
                last_result = scheduler_status.get('last_result', {})
                if last_result:
                    new_reviews = last_result.get('new_reviews', 0)
                    st.metric("Last Collection", f"{new_reviews} new")
            
            with col_s3:
                if last_result:
                    duplicates = last_result.get('duplicates', 0)
                    st.metric("Duplicates", duplicates)
            
            # Last run time
            last_run = scheduler_status.get('last_run')
            if last_run:
                try:
                    last_dt = datetime.fromisoformat(last_run)
                    st.caption(f"🕒 Last run: {last_dt.strftime('%d %b %H:%M:%S')}")
                except:
                    st.caption(f"🕒 Last run: {last_run}")
            
            # Next run countdown (server-side with intelligent handling)
            next_run = scheduler_status.get('next_run')
            last_run = scheduler_status.get('last_run')
            
            if next_run:
                try:
                    next_time = datetime.fromisoformat(next_run)
                    now = datetime.now()
                    time_left = (next_time - now).total_seconds()
                    
                    # Calculate expected next run based on last run and interval
                    interval_minutes = current_config.get('interval_minutes', 30)
                    
                    # Check if last_run exists and calculate time since last run
                    time_since_last_run = None
                    if last_run:
                        try:
                            last_run_time = datetime.fromisoformat(last_run)
                            time_since_last_run = (now - last_run_time).total_seconds()
                        except:
                            pass
                    
                    # If scheduled time has passed (time_left < 0)
                    if time_left < 0:
                        # Calculate next expected run from last run
                        if last_run and time_since_last_run is not None:
                            try:
                                last_run_time = datetime.fromisoformat(last_run)
                                
                                # Calculate how many intervals have passed since last run
                                intervals_passed = int(time_since_last_run // (interval_minutes * 60))
                                
                                # Calculate next expected run (add enough intervals to get to future)
                                estimated_next = last_run_time + timedelta(minutes=interval_minutes * (intervals_passed + 1))
                                est_time_left = (estimated_next - now).total_seconds()
                                
                                # If estimation looks reasonable (within next 2 intervals)
                                if est_time_left > 0 and est_time_left < (interval_minutes * 60 * 2):
                                    # Show estimated countdown
                                    est_minutes = int(est_time_left // 60)
                                    est_seconds = int(est_time_left % 60)
                                    
                                    # Color coding
                                    if est_minutes == 0 and est_seconds < 60:
                                        color = "#ff6b6b"
                                        emoji = "�"
                                    elif est_minutes < 5:
                                        color = "#ffd93d"
                                        emoji = "🟡"
                                    else:
                                        color = "#51cf66"
                                        emoji = "�"
                                    
                                    st.markdown(f"""
                                    <div style="background: {color}; padding: 10px; border-radius: 8px; text-align: center;">
                                        <p style="color: white; font-weight: bold; margin: 0; font-size: 16px;">
                                            {emoji} Next in ~{est_minutes}m {est_seconds}s
                                        </p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    interval_seconds = interval_minutes * 60
                                    progress = 1 - (est_time_left / interval_seconds)
                                    st.progress(max(0, min(1, progress)))
                                    st.caption(f"📅 Estimated: {estimated_next.strftime('%H:%M:%S')}")
                                    st.caption(f"ℹ️ Based on {interval_minutes} min interval")
                                else:
                                    # Estimation doesn't look right, just show active
                                    st.markdown("""
                                    <div style="background: #51cf66; padding: 10px; border-radius: 8px; text-align: center;">
                                        <p style="color: white; font-weight: bold; margin: 0; font-size: 16px;">
                                            ✅ Scheduler is active
                                        </p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    st.caption(f"⏰ Last run: {last_run_time.strftime('%H:%M:%S')}")
                            except Exception as e:
                                # Fallback to generic message
                                st.markdown("""
                                <div style="background: #51cf66; padding: 10px; border-radius: 8px; text-align: center;">
                                    <p style="color: white; font-weight: bold; margin: 0; font-size: 16px;">
                                        ✅ Scheduler is running
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            # No last_run info, just show active
                            st.markdown("""
                            <div style="background: #51cf66; padding: 10px; border-radius: 8px; text-align: center;">
                                <p style="color: white; font-weight: bold; margin: 0; font-size: 16px;">
                                    ✅ Scheduler is active
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.caption("💡 Press 🔄 Refresh to see updated countdown")
                    
                    # Normal countdown (time_left > 0)
                    else:
                        minutes_left = int(time_left // 60)
                        seconds_left = int(time_left % 60)
                        
                        # Colorful countdown display
                        if minutes_left == 0 and seconds_left < 60:
                            color = "#ff6b6b"  # Red - almost time
                            emoji = "🔴"
                        elif minutes_left < 2:
                            color = "#ffd93d"  # Yellow - soon
                            emoji = "🟡"
                        else:
                            color = "#51cf66"  # Green - plenty of time
                            emoji = "🟢"
                        
                        st.markdown(f"""
                        <div style="background: {color}; padding: 10px; border-radius: 8px; text-align: center;">
                            <p style="color: white; font-weight: bold; margin: 0; font-size: 16px;">
                                {emoji} Next in: {minutes_left}m {seconds_left}s
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Progress bar
                        interval_seconds = interval_minutes * 60
                        progress = 1 - (time_left / interval_seconds)
                        st.progress(max(0, min(1, progress)))
                        
                        st.caption(f"📅 Next run at: {next_time.strftime('%H:%M:%S')}")
                        st.caption("💡 Press 🔄 Refresh to update countdown")
                
                except Exception as e:
                    st.caption(f"⚠️ Error calculating countdown: {str(e)}")
            
            # Show recent logs with color coding
            st.markdown("**📝 Recent Activity:**")
            logs = scheduler_status.get('logs', [])
            
            if logs:
                # Count errors
                error_count = sum(1 for log in logs if log.get('level') == 'error')
                
                # Show error warning if any
                if error_count > 0:
                    st.warning(f"⚠️ {error_count} error(s) detected in logs")
                
                # Show last 15 logs in expander (increased from 10)
                with st.expander("View Activity Log", expanded=(error_count > 0)):
                    # Reverse to show newest first
                    for log in reversed(logs[-15:]):
                        timestamp = log.get('timestamp', '')
                        level = log.get('level', 'info')
                        message = log.get('message', '')
                        
                        # Format timestamp
                        try:
                            dt = datetime.fromisoformat(timestamp)
                            time_str = dt.strftime('%H:%M:%S')
                        except:
                            time_str = timestamp
                        
                        # Color and icon based on level
                        if level == 'error':
                            color = "#ff6b6b"
                            icon = "❌"
                            st.markdown(f"""
                            <div style="background: {color}; padding: 8px; border-radius: 5px; margin: 3px 0;">
                                <span style="color: white; font-weight: bold;">{icon} {time_str}</span>
                                <span style="color: white;"> {message}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        elif level == 'warning':
                            color = "#ffd93d"
                            icon = "⚠️"
                            st.markdown(f"""
                            <div style="background: {color}; padding: 8px; border-radius: 5px; margin: 3px 0;">
                                <span style="font-weight: bold;">{icon} {time_str}</span>
                                <span> {message}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        elif level == 'success':
                            icon = "✅"
                            st.caption(f"{icon} `{time_str}` {message}")
                        else:
                            icon = "ℹ️"
                            st.caption(f"{icon} `{time_str}` {message}")
            else:
                st.caption("No activity yet")
            
            # Info box with improved information
            st.info("""
**💡 Background Scheduler:**
- ✓ Runs independently in background
- ✓ Auto-collects reviews at set intervals
- ✓ Saves to database automatically
- ✓ Live countdown updates without page refresh
- ✓ View logs to monitor activity
            """)
        else:
            st.info("� Start the scheduler to enable automatic review collection")
        
        st.markdown("---")
        
        # Refresh database button
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    # Main content
    if df is None or df.empty:
        st.warning("📭 No data available yet. Please collect new data from the sidebar.")
        return
    
    # Convert timestamp_parsed from string to datetime if needed
    if 'timestamp_parsed' in df.columns and df['timestamp_parsed'].dtype == 'object':
        df['timestamp_parsed'] = pd.to_datetime(df['timestamp_parsed'], errors='coerce')
    
    # ALWAYS recalculate time_category to ensure accuracy with current time
    # This fixes issues where old categories become stale
    if 'timestamp_parsed' in df.columns:
        df['time_category'] = df['timestamp_parsed'].apply(categorize_timestamp)
    
    # 🎯 BUSINESS FILTERING SYSTEM
    st.markdown("## 🏢 Business Selection")
    
    # Business list and statistics
    business_stats = df.groupby('business_name').agg({
        'reviewer_name': 'count',
        'rating': 'mean',
        'review_text': lambda x: sum(1 for text in x if text and len(str(text).strip()) > 10)
    }).round(2)
    business_stats.columns = ['Total Reviews', 'Average Rating', 'Text Reviews']
    
    # Business selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        businesses = ["All Businesses"] + list(df['business_name'].unique())
        selected_business = st.selectbox(
            "🎯 Select Business:",
            businesses,
            index=0,
            help="Select the business you want to analyze"
        )
    
    with col2:
        if selected_business != "All Businesses":
            business_data = business_stats.loc[selected_business]
            st.info(f"""
            **{selected_business}**
            - 📊 {int(business_data['Total Reviews'])} reviews
            - ⭐ {business_data['Average Rating']:.1f} rating
            - 💬 {int(business_data['Text Reviews'])} text reviews
            """)
    
    # Business statistics table (for all businesses)
    if selected_business == "All Businesses":
        st.markdown("### 📋 Business Comparison")
        
        # Styled DataFrame
        styled_df = business_stats.style.format({
            'Average Rating': '{:.1f}',
            'Total Reviews': '{:.0f}',
            'Text Reviews': '{:.0f}'
        }).background_gradient(subset=['Average Rating'], cmap='RdYlGn')
        
        st.dataframe(styled_df, use_container_width=True)
    
    # Filter data
    if selected_business != "All Businesses":
        df = df[df['business_name'] == selected_business]
        st.success(f"✅ Showing {len(df)} reviews for {selected_business}")
    else:
        st.info(f"📊 Showing {len(df)} reviews for all businesses")
    
    st.markdown("---")
    
    # Tab structure
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Overview", "📈 Time Analysis", "💬 Review Details", "☁️ WordCloud", "🤖 AI Analysis"])
    
    with tab1:
        st.markdown("## 📊 Overview")
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Reviews",
                len(df),
                delta=None
            )
        
        with col2:
            avg_rating = df['rating'].mean() if 'rating' in df.columns else 0
            st.metric(
                "Average Rating",
                f"{avg_rating:.1f}/5",
                delta=None
            )
        
        with col3:
            text_reviews = len(df[df['review_text'].notna() & (df['review_text'] != '')])
            st.metric(
                "Text Reviews",
                text_reviews,
                delta=f"{(text_reviews/len(df)*100):.1f}%"
            )
        
        with col4:
            recent_count = len(df[df['time_category'].isin(['Today', 'Yesterday'])])
            st.metric(
                "Recent Reviews",
                recent_count,
                delta=f"{(recent_count/len(df)*100):.1f}%"
            )
        
        # Rating distribution
        if 'rating' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### ⭐ Rating Distribution")
                rating_counts = df['rating'].value_counts().sort_index()
                
                fig = px.bar(
                    x=rating_counts.index,
                    y=rating_counts.values,
                    labels={'x': 'Rating', 'y': 'Review Count'},
                    color=rating_counts.values,
                    color_continuous_scale='viridis'
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True, key="rating_dist_overview")
            
            with col2:
                st.markdown("### 📊 Time Category Distribution")
                st.caption("Reviews by time period (based on actual review timestamp)")
                
                # Filter and order time categories
                df_time_overview = df[df['timestamp_parsed'].notna()].copy()
                time_cats = df_time_overview['time_category'].value_counts()
                
                fig = px.pie(
                    values=time_cats.values,
                    names=time_cats.index,
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    hole=0.3
                )
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
                )
                fig.update_layout(height=400, showlegend=True)
                st.plotly_chart(fig, use_container_width=True, key="time_dist_overview")
    
    with tab2:
        st.markdown("## 📈 Time Analysis")
        
        # Filter out rows with null timestamp_parsed
        df_with_time = df[df['timestamp_parsed'].notna()].copy()
        
        if len(df_with_time) == 0:
            st.warning("⚠️ No timestamp data available for time analysis.")
        else:
            # Time category distribution with proper ordering
            time_category_order = [
                'Last Hour', 'Today', 'Yesterday', 'This Week', 
                'This Month', 'Last 3 Months', 'Last 6 Months', 
                'This Year', 'Older', 'Unknown'
            ]
            
            time_cats = df_with_time['time_category'].value_counts()
            # Reindex with proper order (only existing categories)
            existing_cats = [cat for cat in time_category_order if cat in time_cats.index]
            time_cats = time_cats.reindex(existing_cats, fill_value=0)
            
            # Show both timeline and category views
            st.markdown("### 📊 Time Distribution Views")
            
            view_type = st.radio(
                "Select View:",
                ["📈 Timeline (Actual Timestamps)", "📁 Categories (Grouped)"],
                horizontal=True,
                key="time_view_selector"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if view_type == "📈 Timeline (Actual Timestamps)":
                    st.markdown("#### 🕒 Reviews Timeline Distribution")
                    st.caption("Reviews distributed across actual timestamps")
                    
                    # Create histogram based on actual timestamps
                    fig = px.histogram(
                        df_with_time,
                        x='timestamp_parsed',
                        nbins=20,
                        labels={'timestamp_parsed': 'Review Timestamp', 'count': 'Number of Reviews'},
                        color_discrete_sequence=['#667eea']
                    )
                    fig.update_traces(
                        hovertemplate='<b>Period:</b> %{x|%d %b %Y}<br><b>Reviews:</b> %{y}<extra></extra>'
                    )
                    fig.update_layout(
                        height=400, 
                        showlegend=False,
                        xaxis_title='Review Timestamp',
                        yaxis_title='Number of Reviews',
                        bargap=0.1,
                        xaxis=dict(tickangle=-45)
                    )
                    st.plotly_chart(fig, use_container_width=True, key="time_dist_analysis")
                else:
                    st.markdown("#### 📁 Time Category Distribution")
                    st.caption("Reviews grouped by time periods")
                    
                    # Reindex with proper order (only existing categories)
                    existing_cats = [cat for cat in time_category_order if cat in time_cats.index]
                    time_cats_ordered = time_cats.reindex(existing_cats, fill_value=0)
                    
                    fig = px.bar(
                        x=time_cats_ordered.index,
                        y=time_cats_ordered.values,
                        labels={'x': 'Time Category', 'y': 'Review Count'},
                        color=time_cats_ordered.values,
                        color_continuous_scale='plasma',
                        text=time_cats_ordered.values
                    )
                    fig.update_traces(textposition='outside')
                    fig.update_layout(
                        height=400, 
                        showlegend=False,
                        xaxis_title='Time Period',
                        yaxis_title='Number of Reviews',
                        xaxis_tickangle=-45
                    )
                    st.plotly_chart(fig, use_container_width=True, key="time_cat_analysis")
            
            with col2:
                st.markdown("### 📅 Daily Review Trend")
                st.caption("Number of reviews per day (based on actual review timestamp)")
                
                # Daily review count based on timestamp_parsed
                df_with_time['date'] = df_with_time['timestamp_parsed'].dt.date
                daily_counts = df_with_time.groupby('date').size().reset_index(name='count')
                daily_counts = daily_counts.sort_values('date')
                
                # Format dates properly for display
                daily_counts['date_formatted'] = pd.to_datetime(daily_counts['date']).dt.strftime('%d %b %Y')
                
                fig = px.line(
                    daily_counts,
                    x='date',
                    y='count',
                    markers=True,
                    text='count',
                    hover_data={'date': False, 'count': True}
                )
                fig.update_traces(
                    textposition='top center',
                    line=dict(width=3, color='#667eea'),
                    marker=dict(size=10),
                    hovertemplate='<b>Date:</b> %{x|%d %b %Y}<br><b>Reviews:</b> %{y}<extra></extra>'
                )
                fig.update_layout(
                    height=400,
                    xaxis_title='Date',
                    yaxis_title='Number of Reviews',
                    hovermode='x unified',
                    xaxis=dict(
                        tickformat='%d %b',
                        tickangle=-45
                    )
                )
                st.plotly_chart(fig, use_container_width=True, key="daily_trend_analysis")
        
            # Rating over time (scatter plot)
            if 'rating' in df_with_time.columns:
                st.markdown("### ⭐ Rating Trend Over Time")
                st.caption("How ratings changed over time (each point is a review)")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    # Scatter plot of ratings over time
                    fig = px.scatter(
                        df_with_time.sort_values('timestamp_parsed'),
                        x='timestamp_parsed',
                        y='rating',
                        color='rating',
                        color_continuous_scale='RdYlGn',
                        hover_data={'timestamp_parsed': '|%d %b %Y %H:%M', 'rating': True},
                        labels={'timestamp_parsed': 'Review Time', 'rating': 'Rating'}
                    )
                    fig.update_traces(
                        marker=dict(size=10, line=dict(width=1, color='white')),
                        hovertemplate='<b>Time:</b> %{x|%d %b %Y %H:%M}<br><b>Rating:</b> %{y} ⭐<extra></extra>'
                    )
                    fig.update_layout(
                        height=400,
                        yaxis=dict(tickmode='linear', tick0=1, dtick=1, range=[0, 6]),
                        xaxis=dict(tickangle=-45)
                    )
                    st.plotly_chart(fig, use_container_width=True, key="rating_scatter_time")
                
                with col_b:
                    # Moving average of ratings
                    df_sorted = df_with_time.sort_values('timestamp_parsed').copy()
                    df_sorted['rating_ma'] = df_sorted['rating'].rolling(window=min(5, len(df_sorted)), center=True).mean()
                    
                    fig = go.Figure()
                    
                    # Individual ratings
                    fig.add_trace(go.Scatter(
                        x=df_sorted['timestamp_parsed'],
                        y=df_sorted['rating'],
                        mode='markers',
                        name='Individual Ratings',
                        marker=dict(size=8, color='lightgray', opacity=0.5),
                        hovertemplate='<b>Time:</b> %{x|%d %b %Y %H:%M}<br><b>Rating:</b> %{y} ⭐<extra></extra>'
                    ))
                    
                    # Moving average
                    fig.add_trace(go.Scatter(
                        x=df_sorted['timestamp_parsed'],
                        y=df_sorted['rating_ma'],
                        mode='lines',
                        name='Trend (Moving Avg)',
                        line=dict(width=3, color='#667eea'),
                        hovertemplate='<b>Time:</b> %{x|%d %b %Y %H:%M}<br><b>Avg Rating:</b> %{y:.2f} ⭐<extra></extra>'
                    ))
                    
                    fig.update_layout(
                        height=400,
                        yaxis=dict(title='Rating ⭐', tickmode='linear', tick0=1, dtick=1, range=[0, 6]),
                        xaxis=dict(title='Review Time', tickangle=-45),
                        hovermode='x unified',
                        legend=dict(x=0.01, y=0.99)
                    )
                    st.plotly_chart(fig, use_container_width=True, key="rating_trend_time")
            
            # Hourly distribution
            st.markdown("### 🕐 Hourly Review Distribution")
            st.caption("Reviews by hour of day (based on actual review timestamp)")
            
            df_with_time['hour'] = df_with_time['timestamp_parsed'].dt.hour
            hourly_counts = df_with_time.groupby('hour').size().reset_index(name='count')
            
            # Fill missing hours with 0
            all_hours = pd.DataFrame({'hour': range(24)})
            hourly_counts = all_hours.merge(hourly_counts, on='hour', how='left').fillna(0)
            hourly_counts['count'] = hourly_counts['count'].astype(int)
            hourly_counts['hour_label'] = hourly_counts['hour'].apply(lambda x: f'{x:02d}:00')
            
            fig = px.bar(
                hourly_counts,
                x='hour',
                y='count',
                labels={'hour': 'Hour of Day', 'count': 'Review Count'},
                color='count',
                color_continuous_scale='viridis',
                text='count',
                hover_data={'hour': False, 'count': True}
            )
            fig.update_traces(
                textposition='outside',
                hovertemplate='<b>Hour:</b> %{x}:00<br><b>Reviews:</b> %{y}<extra></extra>'
            )
            fig.update_layout(
                height=400,
                xaxis=dict(
                    tickmode='linear', 
                    tick0=0, 
                    dtick=2,
                    tickformat='%02d:00'
                ),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True, key="hourly_distribution")
            
            # Weekly pattern (day of week)
            st.markdown("### 📆 Weekly Pattern Analysis")
            st.caption("Reviews by day of week (based on actual review timestamp)")
            
            df_with_time['day_of_week'] = df_with_time['timestamp_parsed'].dt.day_name()
            df_with_time['day_of_week_num'] = df_with_time['timestamp_parsed'].dt.dayofweek
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            weekly_counts = df_with_time.groupby('day_of_week').size().reset_index(name='count')
            weekly_counts['day_of_week'] = pd.Categorical(weekly_counts['day_of_week'], categories=day_order, ordered=True)
            weekly_counts = weekly_counts.sort_values('day_of_week')
            weekly_counts['day_short'] = weekly_counts['day_of_week'].apply(lambda x: x[:3])
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    weekly_counts,
                    x='day_of_week',
                    y='count',
                    labels={'day_of_week': 'Day of Week', 'count': 'Review Count'},
                    color='count',
                    color_continuous_scale='blues',
                    text='count'
                )
                fig.update_traces(
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>Reviews: %{y}<extra></extra>'
                )
                fig.update_layout(
                    height=400, 
                    showlegend=False, 
                    xaxis_tickangle=-45,
                    xaxis_title='Day of Week',
                    yaxis_title='Number of Reviews'
                )
                st.plotly_chart(fig, use_container_width=True, key="weekly_pattern")
            
            with col2:
                # Average rating by day of week
                if 'rating' in df_with_time.columns:
                    weekly_rating = df_with_time.groupby('day_of_week')['rating'].agg(['mean', 'count']).reset_index()
                    weekly_rating['day_of_week'] = pd.Categorical(weekly_rating['day_of_week'], categories=day_order, ordered=True)
                    weekly_rating = weekly_rating.sort_values('day_of_week')
                    
                    fig = px.line(
                        weekly_rating,
                        x='day_of_week',
                        y='mean',
                        markers=True,
                        labels={'day_of_week': 'Day of Week', 'mean': 'Average Rating'}
                    )
                    fig.update_traces(
                        line=dict(width=3, color='#764ba2'),
                        marker=dict(size=12),
                        text=weekly_rating['mean'].round(2),
                        textposition='top center',
                        hovertemplate='<b>%{x}</b><br>Avg Rating: %{y:.2f} ⭐<br>Reviews: ' + 
                                     weekly_rating['count'].astype(str) + '<extra></extra>'
                    )
                    fig.update_layout(
                        height=400,
                        yaxis=dict(range=[0, 5.5], title='Average Rating ⭐'),
                        xaxis=dict(tickangle=-45, title='Day of Week')
                    )
                    st.plotly_chart(fig, use_container_width=True, key="weekly_rating")
    
    with tab3:
        st.markdown("## 💬 Review Details")
        
        # Filters (Business filter removed as it's in main system)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_rating = st.selectbox(
                "Rating Filter:",
                ["All"] + sorted(df['rating'].unique()) if 'rating' in df.columns else ["All"],
                key="rating_filter_details"
            )
        
        with col2:
            # Get time categories in proper chronological order
            time_category_order = ['Last Hour', 'Today', 'Yesterday', 'This Week', 
                                  'This Month', 'Last 3 Months', 'Last 6 Months', 
                                  'This Year', 'Older']
            available_categories = [cat for cat in time_category_order if cat in df['time_category'].unique()]
            selected_time = st.selectbox(
                "Time Filter:",
                ["All"] + available_categories,
                key="time_filter_details"
            )
        
        with col3:
            show_only_text = st.checkbox(
                "Only text reviews",
                value=False,
                key="text_only_filter"
            )
        
        # Filtering
        filtered_df = df.copy()
        
        if selected_rating != "All":
            filtered_df = filtered_df[filtered_df['rating'] == selected_rating]
        
        if selected_time != "All":
            filtered_df = filtered_df[filtered_df['time_category'] == selected_time]
        
        if show_only_text:
            filtered_df = filtered_df[filtered_df['review_text'].notna() & (filtered_df['review_text'] != '')]
        
        st.markdown(f"### 📝 Filtered Reviews ({len(filtered_df)} items)")
        
        # Display reviews
        for idx, review in filtered_df.head(10).iterrows():
            reviewer_name = review.get('reviewer_name', 'Anonymous')
            rating = review.get('rating', 'N/A')
            date_original = review.get('date_original', 'Date unknown')
            review_text = review.get('review_text', '')
            time_category = review.get('time_category', 'Unknown')
            timestamp_parsed = review.get('timestamp_parsed', '')
            
            # Safe text creation
            reviewer_name_safe = str(reviewer_name).replace('<', '&lt;').replace('>', '&gt;')
            review_text_safe = str(review_text).replace('<', '&lt;').replace('>', '&gt;')
            
            formatted_date = ""
            if timestamp_parsed:
                try:
                    if isinstance(timestamp_parsed, str):
                        # Parse ISO format string to datetime
                        dt = pd.to_datetime(timestamp_parsed)
                        formatted_date = dt.strftime('%d.%m.%Y %H:%M')
                    elif hasattr(timestamp_parsed, 'strftime'):
                        formatted_date = timestamp_parsed.strftime('%d.%m.%Y %H:%M')
                    else:
                        formatted_date = str(timestamp_parsed)
                except:
                    formatted_date = str(timestamp_parsed)
            
            # Create review card
            with st.container():
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 15px;
                    border-radius: 10px;
                    margin: 10px 0;
                    color: white;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                ">
                    <h4 style="margin: 0 0 10px 0; color: #FFE066;">
                        👤 {reviewer_name_safe} • ⭐ {rating} stars
                    </h4>
                    <p style="margin: 5px 0; opacity: 0.8; font-size: 14px;">
                        📅 {date_original} • 🕒 {formatted_date} • 📊 {time_category}
                    </p>
                    <p style="margin: 10px 0 0 0; line-height: 1.5;">
                        💬 {review_text_safe[:600]}{'...' if len(review_text_safe) > 600 else ''}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # Show total review count
        if len(filtered_df) > 10:
            st.info(f"📊 Total {len(filtered_df)} reviews available. Showing first 10 above.")
    
    with tab4:
        st.markdown("## ☁️ WordCloud Analysis")
        
        # Get text reviews
        text_reviews = df[df['review_text'].notna() & (df['review_text'] != '')]
        
        if len(text_reviews) > 0:
            # Combine all reviews
            all_text = ' '.join(text_reviews['review_text'].astype(str))
            
            # Turkish stop words
            turkish_stopwords = {
                've', 'bir', 'bu', 'da', 'de', 'ki', 'ile', 'için', 'olan', 'olan',
                'var', 'yok', 'çok', 'daha', 'en', 'ama', 'fakat', 'lakin', 'ancak',
                'şu', 'o', 'bunlar', 'şunlar', 'onlar', 've', 'veya', 'ya', 'yahut'
            }
            
            try:
                # Create WordCloud
                wordcloud = WordCloud(
                    width=800,
                    height=400,
                    background_color='white',
                    stopwords=turkish_stopwords,
                    max_words=100,
                    colormap='viridis'
                ).generate(all_text)
                
                # Display with Matplotlib
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                ax.set_title('Most Frequently Used Words', fontsize=16, pad=20)
                
                st.pyplot(fig, clear_figure=True)
                
                # Most frequently used words
                words = all_text.lower().split()
                word_freq = Counter([word for word in words if len(word) > 2 and word not in turkish_stopwords])
                
                if word_freq:
                    st.markdown("### 🔤 Most Frequently Used Words")
                    
                    top_words = word_freq.most_common(20)
                    words_df = pd.DataFrame(top_words, columns=['Word', 'Frequency'])
                    
                    fig = px.bar(
                        words_df,
                        x='Frequency',
                        y='Word',
                        orientation='h',
                        title='Top 20 Words'
                    )
                    fig.update_layout(height=600)
                    st.plotly_chart(fig, use_container_width=True, key="word_frequency")
                
            except Exception as e:
                st.error(f"Error creating WordCloud: {str(e)}")
        
        else:
            st.warning("⚠️ Not enough text reviews for WordCloud.")
    
    with tab5:
        st.markdown("## 🤖 AI Analysis with Gemini")
        
        st.info("💡 Use AI to get deep insights from customer reviews with advanced filters")
        
        # 🎯 ADVANCED FILTERS SECTION
        st.markdown("### 🔍 Advanced Filters")
        
        # Quick presets
        with st.expander("⚡ Quick Filter Presets", expanded=False):
            col_preset1, col_preset2, col_preset3 = st.columns(3)
            
            with col_preset1:
                if st.button("🌟 Recent Positive", use_container_width=True, help="Last week, 4-5 stars"):
                    st.session_state.ai_time_select = 'This Week'
                    st.session_state.ai_sentiment_select = 'Positive (4-5★)'
                    st.rerun()
            
            with col_preset2:
                if st.button("⚠️ Recent Issues", use_container_width=True, help="Last week, 1-2 stars"):
                    st.session_state.ai_time_select = 'This Week'
                    st.session_state.ai_sentiment_select = 'Negative (1-2★)'
                    st.rerun()
            
            with col_preset3:
                if st.button("📊 All Time Overview", use_container_width=True, help="All reviews, all ratings"):
                    st.session_state.ai_time_select = 'All'
                    st.session_state.ai_sentiment_select = 'All'
                    st.session_state.ai_rating_select = 'All'
                    st.rerun()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Business selection for AI
            businesses_for_ai = ['All'] + sorted(df['business_name'].unique().tolist())
            selected_business_ai = st.selectbox(
                "📍 Business",
                businesses_for_ai,
                key="ai_business_select"
            )
        
        with col2:
            # Time period selection - use all available categories
            available_time_categories = ['All', 'Last Hour', 'Today', 'Yesterday', 'This Week', 
                                        'This Month', 'Last 3 Months', 'Last 6 Months', 
                                        'This Year', 'Older']
            time_filter_ai = st.selectbox(
                "📅 Time Period",
                available_time_categories,
                key="ai_time_select"
            )
        
        with col3:
            # Rating filter
            available_ratings = ['All'] + sorted([int(r) for r in df['rating'].unique() if pd.notna(r)], reverse=True)
            rating_filter_ai = st.selectbox(
                "⭐ Rating",
                available_ratings,
                key="ai_rating_select"
            )
        
        # Second row of filters
        col4, col5, col6 = st.columns(3)
        
        with col4:
            # Sentiment filter (based on rating)
            sentiment_filter = st.selectbox(
                "😊 Sentiment",
                ['All', 'Positive (4-5★)', 'Neutral (3★)', 'Negative (1-2★)'],
                key="ai_sentiment_select"
            )
        
        with col5:
            # Review count limit
            max_reviews = st.number_input(
                "📊 Max Reviews",
                min_value=10,
                max_value=500,
                value=50,
                step=10,
                help="Maximum number of reviews to analyze (affects API cost)",
                key="ai_max_reviews"
            )
        
        with col6:
            # Text length filter
            min_text_length = st.slider(
                "📝 Min Text Length",
                min_value=0,
                max_value=100,
                value=10,
                step=5,
                help="Minimum characters in review text",
                key="ai_min_length"
            )
        
        # Filter data for AI analysis
        ai_df = df.copy()
        
        if selected_business_ai != 'All':
            ai_df = ai_df[ai_df['business_name'] == selected_business_ai]
        
        if time_filter_ai != 'All':
            ai_df = ai_df[ai_df['time_category'] == time_filter_ai]
        
        if rating_filter_ai != 'All':
            ai_df = ai_df[ai_df['rating'] == rating_filter_ai]
        
        # Apply sentiment filter
        if sentiment_filter == 'Positive (4-5★)':
            ai_df = ai_df[ai_df['rating'] >= 4]
        elif sentiment_filter == 'Neutral (3★)':
            ai_df = ai_df[ai_df['rating'] == 3]
        elif sentiment_filter == 'Negative (1-2★)':
            ai_df = ai_df[ai_df['rating'] <= 2]
        
        # Get text reviews with minimum length filter
        text_reviews_ai = ai_df[
            (ai_df['review_text'].notna()) & 
            (ai_df['review_text'] != '') & 
            (ai_df['review_text'].str.len() >= min_text_length)
        ]['review_text'].tolist()
        
        # Limit to max_reviews
        text_reviews_ai = text_reviews_ai[:max_reviews]
        
        st.markdown("---")
        
        # Show selection summary with more metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Business", selected_business_ai if selected_business_ai != 'All' else 'All')
        
        with col2:
            st.metric("Time Period", time_filter_ai)
        
        with col3:
            st.metric("Rating", f"{rating_filter_ai}★" if rating_filter_ai != 'All' else 'All')
        
        with col4:
            st.metric("Sentiment", sentiment_filter.split(' ')[0])
        
        with col5:
            st.metric("Text Reviews", len(text_reviews_ai))
        
        st.markdown("---")
        
        # 🎨 CUSTOM PROMPT SECTION
        st.markdown("### 🎨 Customize AI Analysis (Optional)")
        
        with st.expander("✍️ Add Custom Instructions", expanded=False):
            st.caption("Add your own instructions to customize the AI analysis. Leave empty for default analysis.")
            
            custom_prompt = st.text_area(
                "Custom AI Instructions:",
                placeholder="Example: Focus on customer service quality and wait times. Compare morning vs evening experiences.",
                max_chars=1000,
                height=100,
                help="Maximum 1000 characters. This will be added to the default analysis prompt.",
                key="ai_custom_prompt"
            )
            
            char_count = len(custom_prompt) if custom_prompt else 0
            col_char1, col_char2 = st.columns([3, 1])
            
            with col_char1:
                if char_count > 0:
                    progress = char_count / 1000
                    st.progress(progress)
            
            with col_char2:
                color = "#ff6b6b" if char_count > 900 else "#51cf66" if char_count > 0 else "#adb5bd"
                st.markdown(f"<p style='color: {color}; text-align: right; margin: 0;'>{char_count}/1000</p>", unsafe_allow_html=True)
            
            if custom_prompt:
                st.info(f"✅ Custom instructions added ({char_count} characters)")
        
        st.markdown("---")
        
        # Analyze button
        if len(text_reviews_ai) > 0:
            col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
            
            with col_btn1:
                analyze_button = st.button("🚀 Analyze with AI", type="primary", key="analyze_button", use_container_width=True)
            
            with col_btn2:
                if len(text_reviews_ai) < 5:
                    st.warning("⚠️ Low sample")
                elif len(text_reviews_ai) >= 50:
                    st.success("✅ Good sample")
                else:
                    st.info("ℹ️ Fair sample")
            
            with col_btn3:
                estimated_time = max(5, len(text_reviews_ai) // 10)
                st.caption(f"⏱️ ~{estimated_time}s")
            
            if analyze_button:
                with st.spinner("🤖 AI is analyzing reviews... This may take a few seconds..."):
                    # Perform AI analysis with ALL filter context
                    result = analyze_reviews_with_ai(
                        text_reviews_ai,
                        selected_business_ai,
                        time_filter_ai,
                        custom_instructions=custom_prompt if custom_prompt else None,
                        rating_filter=rating_filter_ai,
                        sentiment_filter=sentiment_filter,
                        min_text_length=min_text_length
                    )
                    
                    if result["success"]:
                        st.success(f"✅ Analysis completed! Analyzed {result['reviews_count']} reviews")
                        
                        # Display analysis in a nice format
                        st.markdown("### 📊 AI Analysis Results")
                        
                        # Build filter summary
                        filter_summary = f"📅 {time_filter_ai}"
                        if rating_filter_ai != 'All':
                            filter_summary += f" | ⭐ {rating_filter_ai}★"
                        if sentiment_filter != 'All':
                            filter_summary += f" | 😊 {sentiment_filter.split(' ')[0]}"
                        filter_summary += f" | 💬 {result['reviews_count']} reviews"
                        
                        # Analysis header with filters
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            padding: 20px;
                            border-radius: 10px;
                            color: white;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                            margin: 20px 0;
                        ">
                            <h3 style="color: #FFE066; margin-top: 0;">
                                🎯 Analysis for: {selected_business_ai}
                            </h3>
                            <p style="opacity: 0.9; margin: 5px 0;">{filter_summary}</p>
                            {'<p style="opacity: 0.85; margin: 5px 0; font-size: 14px;">✍️ Custom instructions applied</p>' if custom_prompt else ''}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display the analysis
                        st.markdown(result["analysis"])
                        
                        # Download button for analysis with metadata
                        analysis_metadata = f"""
AI Analysis Report
==================
Business: {selected_business_ai}
Time Period: {time_filter_ai}
Rating Filter: {rating_filter_ai}
Sentiment: {sentiment_filter}
Reviews Analyzed: {result['reviews_count']}
Date Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Custom Instructions: {'Yes' if custom_prompt else 'No'}

{'='*50}

{result['analysis']}
"""
                        
                        col_dl1, col_dl2 = st.columns([3, 1])
                        
                        with col_dl1:
                            st.download_button(
                                label="📥 Download Analysis Report",
                                data=analysis_metadata,
                                file_name=f"ai_analysis_{selected_business_ai}_{time_filter_ai}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        
                        with col_dl2:
                            # Show token estimate
                            token_estimate = len(result['analysis'].split()) * 1.3
                            st.caption(f"📊 ~{int(token_estimate)} tokens")
                        
                    else:
                        st.error(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
                        
                        if "GEMINI_API_KEY" in result.get('error', ''):
                            st.warning("""
                            ⚠️ **Gemini API Key not configured**
                            
                            To use AI analysis:
                            1. Get your free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
                            2. Create a `.env` file in the project root
                            3. Add: `GEMINI_API_KEY=your_api_key_here`
                            4. Restart the dashboard
                            """)
        else:
            st.warning("⚠️ No text reviews available for the selected filters. Please adjust your selection.")
            st.info("💡 Try selecting 'All' for business and time period to see all available reviews.")

if __name__ == "__main__":
    main()
