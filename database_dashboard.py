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

def analyze_reviews_with_ai(reviews_text, business_name, time_period):
    """Analyze reviews using Gemini AI"""
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
            model_name = "gemini-2.0-flash-exp"
        except AttributeError:
            # Old API style fallback
            genai.configure(api_key=api_key)
            client = genai
            model_name = "gemini-1.5-flash"
        
        # Create analysis prompt
        prompt = f"""
You are analyzing customer reviews for: {business_name}
Time period: {time_period}
Number of reviews: {len(reviews_text)} reviews

Reviews to analyze:
{chr(10).join(reviews_text[:50])}  # Analyze first 50 reviews

Please provide a comprehensive analysis in the following format:

1. **Overall Sentiment**
   - Positive/Negative/Mixed percentage breakdown
   - General mood of customers

2. **Key Themes** (Top 5-7 themes mentioned)
   - List the most frequently mentioned topics
   - For each theme, indicate if it's positive or negative

3. **Strengths** (Top 3-5)
   - What customers love most
   - Most praised aspects

4. **Areas for Improvement** (Top 3-5)
   - Common complaints
   - Issues that need attention

5. **Customer Insights**
   - Patterns in customer behavior
   - Recommendations based on feedback

6. **Summary**
   - Brief executive summary (2-3 sentences)

Please provide the analysis in clear, structured format with bullet points.
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
    """Categorize timestamp into time periods"""
    try:
        tr_tz = pytz.timezone('Europe/Istanbul')
        now = datetime.now(tr_tz)
        
        # Make timestamp timezone-aware
        if timestamp.tzinfo is None:
            timestamp = tr_tz.localize(timestamp)
        
        diff = now - timestamp
        
        if diff.days == 0:
            return "Today"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days <= 7:
            return "This Week"
        elif diff.days <= 30:
            return "This Month"
        else:
            return "Older"
    except:
        return "Time Unknown"

def run_api_collector():
    """Collect data via Google Maps API"""
    with st.spinner("🚀 Collecting data via Google Maps API..."):
        try:
            # Get Place ID and business name
            place_id = st.session_state.get('place_id', '')
            business_name = st.session_state.get('business_name', '')
            
            if not place_id or not business_name:
                st.error("❌ Business name and Place ID are required!")
                st.info("💡 Place ID example: ChIJqZW8Cvb_n0ARBuUkyCzgDDg")
                return False
            
            # Initialize API collector
            collector = GoogleMapsAPICollector()
            
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
                        # Add new review
                        db.add_review(
                            business_name=business_name,
                            reviewer_name=review.author_name,
                            rating=review.rating,
                            review_text=review.text or "",
                            date_original=review.relative_time,
                            review_hash=review_hash
                        )
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
        
        # Quick add from configured businesses
        if BusinessConfig.BUSINESSES:
            st.markdown("### ⚡ Quick Collect")
            st.caption("Configured businesses:")
            
            for idx, (pid, bname) in enumerate(BusinessConfig.BUSINESSES):
                if st.button(f"📍 {bname}", key=f"quick_{idx}"):
                    st.session_state['place_id'] = pid
                    st.session_state['business_name'] = bname
                    run_api_collector()
        
        st.markdown("---")
        
        # Refresh database
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Main content
    if df is None or df.empty:
        st.warning("📭 No data available yet. Please collect new data from the sidebar.")
        return
    
    # Add time parsing
    df['timestamp_parsed'] = df['date_original'].apply(parse_relative_time_to_timestamp)
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
                time_cats = df['time_category'].value_counts()
                
                fig = px.pie(
                    values=time_cats.values,
                    names=time_cats.index,
                    title="Reviews by Time",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True, key="time_dist_overview")
    
    with tab2:
        st.markdown("## 📈 Time Analysis")
        
        # Time category distribution
        time_cats = df['time_category'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🕒 Time Distribution")
            
            fig = px.bar(
                x=time_cats.index,
                y=time_cats.values,
                labels={'x': 'Time Category', 'y': 'Review Count'},
                color=time_cats.values,
                color_continuous_scale='plasma'
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True, key="time_dist_analysis")
        
        with col2:
            st.markdown("### 📅 Daily Trend")
            
            # Daily review count
            df['date'] = df['timestamp_parsed'].dt.date
            daily_counts = df.groupby('date').size().reset_index(name='count')
            
            fig = px.line(
                daily_counts,
                x='date',
                y='count',
                title='Daily Review Count',
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True, key="daily_trend_analysis")
        
        # Time and rating correlation
        if 'rating' in df.columns:
            st.markdown("### ⏰ Time vs Rating Analysis")
            
            time_rating = df.groupby('time_category')['rating'].agg(['mean', 'count']).reset_index()
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=time_rating['time_category'],
                y=time_rating['mean'],
                name='Average Rating',
                yaxis='y',
                marker_color='lightblue'
            ))
            
            fig.add_trace(go.Scatter(
                x=time_rating['time_category'],
                y=time_rating['count'],
                mode='lines+markers',
                name='Review Count',
                yaxis='y2',
                marker_color='red'
            ))
            
            fig.update_layout(
                title='Rating and Review Count by Time Category',
                xaxis_title='Time Category',
                yaxis=dict(title='Average Rating', side='left'),
                yaxis2=dict(title='Review Count', side='right', overlaying='y'),
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True, key="time_rating_correlation")
    
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
            selected_time = st.selectbox(
                "Time Filter:",
                ["All"] + list(df['time_category'].unique()),
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
                        formatted_date = timestamp_parsed
                    else:
                        formatted_date = timestamp_parsed.strftime('%d.%m.%Y %H:%M')
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
        
        st.info("💡 Use AI to get deep insights from customer reviews")
        
        # Analysis configuration
        col1, col2 = st.columns(2)
        
        with col1:
            # Business selection for AI
            businesses_for_ai = ['All'] + sorted(df['business_name'].unique().tolist())
            selected_business_ai = st.selectbox(
                "Select Business for AI Analysis",
                businesses_for_ai,
                key="ai_business_select"
            )
        
        with col2:
            # Time period selection
            time_filter_ai = st.selectbox(
                "Select Time Period",
                ['All', 'Today', 'Yesterday', 'This Week', 'This Month', 'Older'],
                key="ai_time_select"
            )
        
        # Filter data for AI analysis
        ai_df = df.copy()
        
        if selected_business_ai != 'All':
            ai_df = ai_df[ai_df['business_name'] == selected_business_ai]
        
        if time_filter_ai != 'All':
            ai_df = ai_df[ai_df['time_category'] == time_filter_ai]
        
        # Get text reviews
        text_reviews_ai = ai_df[ai_df['review_text'].notna() & (ai_df['review_text'] != '')]['review_text'].tolist()
        
        st.markdown("---")
        
        # Show selection summary
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Business", selected_business_ai)
        
        with col2:
            st.metric("Time Period", time_filter_ai)
        
        with col3:
            st.metric("Text Reviews", len(text_reviews_ai))
        
        st.markdown("---")
        
        # Analyze button
        if len(text_reviews_ai) > 0:
            if st.button("🚀 Analyze with AI", type="primary", key="analyze_button"):
                with st.spinner("🤖 AI is analyzing reviews... This may take a few seconds..."):
                    # Perform AI analysis
                    result = analyze_reviews_with_ai(
                        text_reviews_ai,
                        selected_business_ai,
                        time_filter_ai
                    )
                    
                    if result["success"]:
                        st.success(f"✅ Analysis completed! Analyzed {result['reviews_count']} reviews")
                        
                        # Display analysis in a nice format
                        st.markdown("### 📊 AI Analysis Results")
                        
                        # Analysis content
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
                            <p style="opacity: 0.9;">📅 Period: {time_filter_ai} | 💬 Reviews: {result['reviews_count']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display the analysis
                        st.markdown(result["analysis"])
                        
                        # Download button for analysis
                        st.download_button(
                            label="📥 Download Analysis",
                            data=result["analysis"],
                            file_name=f"ai_analysis_{selected_business_ai}_{time_filter_ai}.txt",
                            mime="text/plain"
                        )
                        
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
