"""
🎯 Google Maps Yorumları - Veritabanı Entegrasyonlu Dashboard
SQLite veritabanından veri çekme ile geliştirilmiş analiz arayüzü
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
from database_scraper import DatabaseGoogleMapsScraper
import pytz

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="🎯 Google Maps Yorumları - DB Dashboard",
    page_icon="💾",
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

def load_data_from_database(db_path="main_reviews.db"):
    """Veritabanından tüm verileri yükle"""
    try:
        db = ReviewsDatabase(db_path)
        
        # Tüm yorumları getir
        df = db.get_all_reviews()
        
        if df.empty:
            return None, None
        
        # Session istatistiklerini getir
        stats = db.get_statistics()
        
        return df, stats
    
    except Exception as e:
        st.error(f"❌ Veritabanı yüklenirken hata: {str(e)}")
        return None, None

def parse_relative_time_to_timestamp(relative_time_str):
    """Türkçe göreceli zaman ifadelerini timestamp'e çevirir"""
    try:
        # Türkiye saat dilimi
        tr_tz = pytz.timezone('Europe/Istanbul')
        now = datetime.now(tr_tz)
        
        # Metni temizle ve küçük harfe çevir
        text = relative_time_str.lower().strip()
        
        # Türkçe zaman kalıpları
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
    """Timestamp'i zaman kategorisine ayır"""
    try:
        tr_tz = pytz.timezone('Europe/Istanbul')
        now = datetime.now(tr_tz)
        
        # Timestamp'i timezone-aware yap
        if timestamp.tzinfo is None:
            timestamp = tr_tz.localize(timestamp)
        
        diff = now - timestamp
        
        if diff.days == 0:
            return "Bugün"
        elif diff.days == 1:
            return "Dün"
        elif diff.days <= 7:
            return "Bu Hafta"
        elif diff.days <= 30:
            return "Bu Ay"
        else:
            return "Eski"
    except:
        return "Zaman bilgisi belirsiz"

def run_new_scraper():
    """Yeni veri toplama işlemi"""
    with st.spinner("🦊 Yeni veriler toplanıyor..."):
        try:
            # URL ve parametreleri al
            business_url = st.session_state.get('business_url', '')
            business_name = st.session_state.get('business_name', '')
            text_reviews = st.session_state.get('text_reviews', 5)
            total_reviews = st.session_state.get('total_reviews', 10)
            
            if not business_url or not business_name:
                st.error("❌ İşletme adı ve URL'si gerekli!")
                return False
            
            # Scraper'ı başlat
            scraper = DatabaseGoogleMapsScraper(headless=True, db_path="main_reviews.db")
            
            # Veri topla
            result = scraper.scrape_business_reviews(
                business_name=business_name,
                business_url=business_url,
                text_reviews_target=text_reviews,
                total_ratings_target=total_reviews
            )
            
            if result:
                st.success("✅ Veriler başarıyla veritabanına kaydedildi!")
                # Sayfayı yenile
                st.rerun()
                return True
            else:
                st.error("❌ Veri toplama işlemi başarısız!")
                return False
                
        except Exception as e:
            st.error(f"❌ Hata: {str(e)}")
            return False

def main():
    """Ana dashboard fonksiyonu"""
    
    # Ana başlık
    st.markdown("""
    <div class="main-header">
        <h1>💾 Google Maps Yorumları - Veritabanı Dashboard</h1>
        <p>SQLite veritabanından gerçek zamanlı analiz</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - Veri yönetimi
    with st.sidebar:
        st.markdown("## 🎯 Veri Yönetimi")
        
        # Veritabanı durumu
        df, stats = load_data_from_database()
        
        if df is not None and not df.empty:
            st.success(f"✅ Veritabanında {len(df)} yorum bulundu")
            
            # İstatistikler
            st.markdown("### 📊 Genel İstatistikler")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Toplam Yorum", stats.get('total_reviews', 0))
                st.metric("Ortalama Puan", f"{stats.get('average_rating', 0):.1f}")
            
            with col2:
                st.metric("Metin Yorumu", stats.get('text_reviews', 0))
                st.metric("İşletme Sayısı", stats.get('total_businesses', 1))
            
        else:
            st.warning("⚠️ Veritabanında henüz veri yok")
        
        st.markdown("---")
        
        # Yeni veri toplama
        st.markdown("### 🚀 Yeni Veri Topla")
        
        business_name = st.text_input(
            "İşletme Adı:",
            value="İstanbul Sabiha Gökçen Uluslararası Havalimanı",
            key="business_name"
        )
        
        business_url = st.text_area(
            "Google Maps URL:",
            value="https://www.google.com/maps/place/%C4%B0stanbul+Sabiha+G%C3%B6k%C3%A7en+Uluslararas%C4%B1+Havaliman%C4%B1/@40.9066374,29.3133253,17z/data=!4m8!3m7!1s0x14cadbcbf424a153:0xacefca4d8098da74!8m2!3d40.8944747!4d29.3130928!9m1!1b1!16zL20vMDJnbmhx?entry=ttu&g_ep=EgoyMDI1MDkwMy4wIKXMDSoASAFQAw%3D%3D",
            height=100,
            key="business_url"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            text_reviews = st.number_input("Metin Yorumu:", min_value=1, max_value=50, value=5, key="text_reviews")
        with col2:
            total_reviews = st.number_input("Toplam Hedef:", min_value=1, max_value=100, value=10, key="total_reviews")
        
        if st.button("🦊 Veri Topla", type="primary"):
            run_new_scraper()
        
        st.markdown("---")
        
        # Veritabanı yenile
        if st.button("🔄 Verileri Yenile"):
            st.rerun()
    
    # Ana içerik
    if df is None or df.empty:
        st.warning("📭 Henüz veri bulunmuyor. Lütfen sidebar'dan yeni veri toplayın.")
        return
    
    # Zaman parsing'i ekle
    df['timestamp_parsed'] = df['date_original'].apply(parse_relative_time_to_timestamp)
    df['time_category'] = df['timestamp_parsed'].apply(categorize_timestamp)
    
    # Sekme yapısı
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Genel Bakış", "📈 Zaman Analizi", "💬 Yorum Detayları", "☁️ WordCloud"])
    
    with tab1:
        st.markdown("## 📊 Genel Bakış")
        
        # Ana metrikler
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Toplam Yorum",
                len(df),
                delta=None
            )
        
        with col2:
            avg_rating = df['rating'].mean() if 'rating' in df.columns else 0
            st.metric(
                "Ortalama Puan",
                f"{avg_rating:.1f}/5",
                delta=None
            )
        
        with col3:
            text_reviews = len(df[df['review_text'].notna() & (df['review_text'] != '')])
            st.metric(
                "Metin Yorumu",
                text_reviews,
                delta=f"{(text_reviews/len(df)*100):.1f}%"
            )
        
        with col4:
            recent_count = len(df[df['time_category'].isin(['Bugün', 'Dün'])])
            st.metric(
                "Son Yorumlar",
                recent_count,
                delta=f"{(recent_count/len(df)*100):.1f}%"
            )
        
        # Puan dağılımı
        if 'rating' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### ⭐ Puan Dağılımı")
                rating_counts = df['rating'].value_counts().sort_index()
                
                fig = px.bar(
                    x=rating_counts.index,
                    y=rating_counts.values,
                    labels={'x': 'Puan', 'y': 'Yorum Sayısı'},
                    color=rating_counts.values,
                    color_continuous_scale='viridis'
                )
                fig.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig, use_container_width=True, key="rating_dist_overview")
            
            with col2:
                st.markdown("### 📊 İşletme Dağılımı")
                business_counts = df['business_name'].value_counts()
                
                fig = px.pie(
                    values=business_counts.values,
                    names=business_counts.index,
                    title="Yorumlar İşletme Bazında"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True, key="business_dist_overview")
    
    with tab2:
        st.markdown("## 📈 Zaman Analizi")
        
        # Zaman kategorisi dağılımı
        time_cats = df['time_category'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🕒 Zaman Dağılımı")
            
            fig = px.bar(
                x=time_cats.index,
                y=time_cats.values,
                labels={'x': 'Zaman Kategorisi', 'y': 'Yorum Sayısı'},
                color=time_cats.values,
                color_continuous_scale='plasma'
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True, key="time_dist_analysis")
        
        with col2:
            st.markdown("### 📅 Günlük Trend")
            
            # Günlük yorum sayısı
            df['date'] = df['timestamp_parsed'].dt.date
            daily_counts = df.groupby('date').size().reset_index(name='count')
            
            fig = px.line(
                daily_counts,
                x='date',
                y='count',
                title='Günlük Yorum Sayısı',
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True, key="daily_trend_analysis")
        
        # Zaman ve puan korelasyonu
        if 'rating' in df.columns:
            st.markdown("### ⏰ Zaman vs Puan Analizi")
            
            time_rating = df.groupby('time_category')['rating'].agg(['mean', 'count']).reset_index()
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=time_rating['time_category'],
                y=time_rating['mean'],
                name='Ortalama Puan',
                yaxis='y',
                marker_color='lightblue'
            ))
            
            fig.add_trace(go.Scatter(
                x=time_rating['time_category'],
                y=time_rating['count'],
                mode='lines+markers',
                name='Yorum Sayısı',
                yaxis='y2',
                marker_color='red'
            ))
            
            fig.update_layout(
                title='Zaman Kategorilerine Göre Puan ve Yorum Sayısı',
                xaxis_title='Zaman Kategorisi',
                yaxis=dict(title='Ortalama Puan', side='left'),
                yaxis2=dict(title='Yorum Sayısı', side='right', overlaying='y'),
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True, key="time_rating_correlation")
    
    with tab3:
        st.markdown("## 💬 Yorum Detayları")
        
        # Filtreler
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_business = st.selectbox(
                "İşletme Seç:",
                ["Tümü"] + list(df['business_name'].unique()),
                key="business_filter_details"
            )
        
        with col2:
            selected_rating = st.selectbox(
                "Puan Filtresi:",
                ["Tümü"] + sorted(df['rating'].unique()) if 'rating' in df.columns else ["Tümü"],
                key="rating_filter_details"
            )
        
        with col3:
            selected_time = st.selectbox(
                "Zaman Filtresi:",
                ["Tümü"] + list(df['time_category'].unique()),
                key="time_filter_details"
            )
        
        # Filtreleme
        filtered_df = df.copy()
        
        if selected_business != "Tümü":
            filtered_df = filtered_df[filtered_df['business_name'] == selected_business]
        
        if selected_rating != "Tümü":
            filtered_df = filtered_df[filtered_df['rating'] == selected_rating]
        
        if selected_time != "Tümü":
            filtered_df = filtered_df[filtered_df['time_category'] == selected_time]
        
        st.markdown(f"### 📝 Filtrelenmiş Yorumlar ({len(filtered_df)} adet)")
        
        # Yorumları göster
        for idx, review in filtered_df.head(10).iterrows():
            reviewer_name = review.get('reviewer_name', 'Anonim')
            rating = review.get('rating', 'N/A')
            date_original = review.get('date_original', 'Tarih bilinmiyor')
            review_text = review.get('review_text', '')
            time_category = review.get('time_category', 'Bilinmiyor')
            timestamp_parsed = review.get('timestamp_parsed', '')
            
            # Güvenli metin oluşturma
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
            
            # Yorum kartı oluştur
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
                        👤 {reviewer_name_safe} • ⭐ {rating} yıldız
                    </h4>
                    <p style="margin: 5px 0; opacity: 0.8; font-size: 14px;">
                        📅 {date_original} • 🕒 {formatted_date} • 📊 {time_category}
                    </p>
                    <p style="margin: 10px 0 0 0; line-height: 1.5;">
                        💬 {review_text_safe[:600]}{'...' if len(review_text_safe) > 600 else ''}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # Toplam yorum sayısını göster
        if len(filtered_df) > 10:
            st.info(f"📊 Toplam {len(filtered_df)} yorum var. Yukarıda ilk 10 tanesi gösteriliyor.")
    
    with tab4:
        st.markdown("## ☁️ WordCloud Analizi")
        
        # Metin yorumlarını al
        text_reviews = df[df['review_text'].notna() & (df['review_text'] != '')]
        
        if len(text_reviews) > 0:
            # Tüm yorumları birleştir
            all_text = ' '.join(text_reviews['review_text'].astype(str))
            
            # Türkçe stop words
            turkish_stopwords = {
                've', 'bir', 'bu', 'da', 'de', 'ki', 'ile', 'için', 'olan', 'olan',
                'var', 'yok', 'çok', 'daha', 'en', 'ama', 'fakat', 'lakin', 'ancak',
                'şu', 'o', 'bunlar', 'şunlar', 'onlar', 've', 'veya', 'ya', 'yahut'
            }
            
            try:
                # WordCloud oluştur
                wordcloud = WordCloud(
                    width=800,
                    height=400,
                    background_color='white',
                    stopwords=turkish_stopwords,
                    max_words=100,
                    colormap='viridis'
                ).generate(all_text)
                
                # Matplotlib ile göster
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                ax.set_title('En Sık Kullanılan Kelimeler', fontsize=16, pad=20)
                
                st.pyplot(fig, key="wordcloud_main")
                
                # En sık kullanılan kelimeler
                words = all_text.lower().split()
                word_freq = Counter([word for word in words if len(word) > 2 and word not in turkish_stopwords])
                
                if word_freq:
                    st.markdown("### 🔤 En Sık Kullanılan Kelimeler")
                    
                    top_words = word_freq.most_common(20)
                    words_df = pd.DataFrame(top_words, columns=['Kelime', 'Sıklık'])
                    
                    fig = px.bar(
                        words_df,
                        x='Sıklık',
                        y='Kelime',
                        orientation='h',
                        title='Top 20 Kelime'
                    )
                    fig.update_layout(height=600)
                    st.plotly_chart(fig, use_container_width=True, key="word_frequency")
                
            except Exception as e:
                st.error(f"WordCloud oluşturulurken hata: {str(e)}")
        
        else:
            st.warning("⚠️ WordCloud için yeterli metin yorumu bulunmuyor.")

if __name__ == "__main__":
    main()
