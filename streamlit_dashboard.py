"""
🎯 Google Maps Yorumları - Modern Analiz Dashboard
StreamLit ile geliştirilmiş interaktif analiz arayüzü
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
from firefox_optimized_scraper import FirefoxGoogleMapsReviewScraper
import pytz

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="🎯 Google Maps Yorumları Analiz Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
                                    <p style="margin: 5px 0; opacity: 0.8; font-size: 14px;">
                        📅 {date_original}   {formatted_date}   {time_category}
                    </p>               <p style="margin: 5px 0; opacity: 0.8; font-size: 14px;">
                        📅 {date_original}   {formatted_date}   {time_category}
                    </p>             👤 {reviewer_name} • ⭐ {rating} yıldız
                    </h4>
                    <p style="margin: 5px 0; opacity: 0.8; font-size: 14px;">
                        📅 Orijinal: {date_original}<br/>
                        🕒 Gerçek: {formatted_date}<br/>
                        📊 Kategori: {time_category}
                    </p>          <p style="margin: 5px 0; opacity: 0.8; font-size: 14px;">
                        📅 Orijinal: {date_original}<br/>
                        🕒 Gerçek: {formatted_date}<br/>
                        📊 Kategori: {time_category}
                    </p>.main > div {
        padding: 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .custom-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .insight-box {
        background-color: #e8f4fd;
        border-left: 5px solid #1f77b4;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="custom-header">
        <h1>🎯 Google Maps Yorumları Analiz Dashboard</h1>
        <p>Gerçek zamanlı veri toplama ve akıllı analiz platformu</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - Kontrol Paneli
    with st.sidebar:
        st.header("🎛️ Kontrol Paneli")
        
        # Veri toplama seçenekleri
        st.subheader("📊 Veri Toplama")
        data_source = st.radio(
            "Veri kaynağı seçin:",
            ["🔴 Canlı Veri Toplama", "📁 CSV Dosyasından Yükle"]
        )
        
        if data_source == "🔴 Canlı Veri Toplama":
            st.markdown("### 🎯 Scraping Parametreleri")
            
            url_input = st.text_input(
                "Google Maps URL:",
                placeholder="https://www.google.com/maps/place/...",
                help="İşletmenin Google Maps linkini buraya yapıştırın"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                text_reviews = st.number_input(
                    "Metin Yorumu",
                    min_value=5,
                    max_value=50,
                    value=15,
                    help="Sadece metin içeren yorumlar"
                )
            
            with col2:
                rating_reviews = st.number_input(
                    "Toplam Puanlama", 
                    min_value=10,
                    max_value=100,
                    value=30,
                    help="Tüm değerlendirmeler (istatistik için)"
                )
            
            if st.button("🚀 Veri Toplamaya Başla", type="primary"):
                if url_input:
                    collect_live_data(url_input, text_reviews, rating_reviews)
                else:
                    st.error("🚨 Lütfen Google Maps URL'si girin!")
        
        else:
            uploaded_file = st.file_uploader(
                "CSV dosyası yükleyin:",
                type=['csv'],
                help="Önceden toplanan veri dosyasını seçin"
            )
            
            if uploaded_file:
                load_csv_data(uploaded_file)
        
        # Analiz ayarları
        st.markdown("---")
        st.subheader("⚙️ Analiz Ayarları")
        
        analysis_type = st.multiselect(
            "Analiz türleri:",
            ["📈 Temel İstatistikler", "📊 Puan Dağılımı", "☁️ Kelime Bulutu", 
             "📅 Zaman Analizi", "🔍 Sentiment Analizi", "💡 Akıllı Öneriler"],
            default=["📈 Temel İstatistikler", "📊 Puan Dağılımı"]
        )
        
        st.markdown("---")
        st.info("💡 **İpucu:** Canlı veri toplamak için Firefox kurulu olmalıdır.")

def collect_live_data(url, text_count, rating_count):
    """Canlı veri toplama fonksiyonu"""
    with st.spinner("🔄 Veriler toplanıyor... Bu işlem 1-2 dakika sürebilir."):
        try:
            # Business name'i URL'den çıkar
            business_name = extract_business_name_from_url(url)
            
            # Scraper'ı başlat
            scraper = FirefoxGoogleMapsReviewScraper(headless=True)
            
            # Veri topla
            results = scraper.scrape_reviews(
                business_name=business_name,
                text_reviews_count=text_count,
                rating_reviews_count=rating_count,
                google_maps_url=url
            )
            
            if results and results['text_reviews']:
                # Session state'e kaydet
                st.session_state['live_data'] = results
                st.session_state['business_name'] = business_name
                st.success(f"✅ {len(results['text_reviews'])} metin yorumu ve {len(results['all_ratings'])} puanlama toplandı!")
                
                # Analize yönlendir
                st.rerun()
            else:
                st.error("❌ Veri toplama başarısız! URL'yi kontrol edin.")
                
        except Exception as e:
            st.error(f"❌ Hata: {str(e)}")

def load_csv_data(uploaded_file):
    """CSV dosyasından veri yükleme"""
    try:
        df = pd.read_csv(uploaded_file)
        
        # CSV formatını kontrol et
        required_columns = ['reviewer_name', 'review_text', 'rating', 'date']
        if all(col in df.columns for col in required_columns):
            
            # Fake results formatına çevir
            fake_results = {
                'text_reviews': [],
                'all_ratings': [],
                'statistics': {}
            }
            
            for _, row in df.iterrows():
                if pd.notna(row['review_text']) and len(str(row['review_text'])) > 10:
                    fake_results['text_reviews'].append({
                        'reviewer_name': row['reviewer_name'],
                        'review_text': row['review_text'],
                        'rating': str(row['rating']),
                        'date': row['date']
                    })
                
                if pd.notna(row['rating']):
                    fake_results['all_ratings'].append({
                        'rating': int(row['rating']) if str(row['rating']).isdigit() else None,
                        'date': row['date'],
                        'reviewer_name': row['reviewer_name']
                    })
            
            # İstatistikleri hesapla
            fake_results['statistics'] = calculate_statistics(fake_results['all_ratings'])
            
            st.session_state['live_data'] = fake_results
            st.session_state['business_name'] = uploaded_file.name.split('.')[0]
            st.success(f"✅ CSV yüklendi: {len(fake_results['text_reviews'])} yorum")
            st.rerun()
            
        else:
            st.error(f"❌ CSV formatı hatalı! Gerekli sütunlar: {required_columns}")
            
    except Exception as e:
        st.error(f"❌ CSV yükleme hatası: {str(e)}")

def extract_business_name_from_url(url):
    """URL'den işletme adını çıkarır"""
    try:
        import urllib.parse
        decoded = urllib.parse.unquote(url)
        if '/place/' in decoded:
            name_part = decoded.split('/place/')[1].split('/')[0]
            return name_part.replace('+', ' ')
        return "Bilinmeyen İşletme"
    except:
        return "Bilinmeyen İşletme"

def calculate_statistics(ratings_data):
    """İstatistikleri hesaplar"""
    try:
        valid_ratings = [r['rating'] for r in ratings_data if r['rating'] is not None]
        if not valid_ratings:
            return {}
        
        return {
            'rating_average': sum(valid_ratings) / len(valid_ratings),
            'rating_count': len(valid_ratings),
            'rating_distribution': {
                str(i): valid_ratings.count(i) for i in range(1, 6)
            }
        }
    except:
        return {}

def show_analytics():
    """Ana analitik dashboard'unu gösterir"""
    
    if 'live_data' not in st.session_state:
        st.info("👆 Lütfen önce veri toplayın veya CSV dosyası yükleyin.")
        return
    
    data = st.session_state['live_data']
    business_name = st.session_state.get('business_name', 'İşletme')
    
    # Ana başlık
    st.header(f"📊 {business_name} - Analiz Raporu")
    
    # Temel metrikler
    show_key_metrics(data)
    
    # Ana analiz sekmeleri
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Genel Bakış", "📊 Detaylı Analizler", "☁️ Kelime Analizi", "💡 Öneriler", "🧪 Test"])
    
    with tab1:
        show_overview_analysis(data)
    
    with tab2:
        show_detailed_analysis(data)
    
    with tab3:
        show_word_analysis(data)
    
    with tab4:
        show_recommendations(data)
    
    with tab5:
        test_time_parsing()

def show_key_metrics(data):
    """Temel metrikleri gösterir"""
    
    stats = data.get('statistics', {})
    text_reviews = data.get('text_reviews', [])
    all_ratings = data.get('all_ratings', [])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg_rating = stats.get('rating_average', 0)
        st.metric(
            label="⭐ Ortalama Puan",
            value=f"{avg_rating:.1f}/5",
            delta=f"{avg_rating-3:.1f}" if avg_rating > 0 else None
        )
    
    with col2:
        st.metric(
            label="📝 Metin Yorumu",
            value=len(text_reviews),
            delta=f"%{len(text_reviews)/len(all_ratings)*100:.0f}" if all_ratings else None
        )
    
    with col3:
        st.metric(
            label="📊 Toplam Puanlama",
            value=len(all_ratings)
        )
    
    with col4:
        # Son 24 saat yorumları
        recent_count = count_recent_reviews(text_reviews, hours=24)
        st.metric(
            label="🕐 Son 24 Saat",
            value=recent_count,
            delta=f"%{recent_count/len(text_reviews)*100:.0f}" if text_reviews else None
        )
    
    with col5:
        # En pozitif/negatif oranı
        positive_count = len([r for r in all_ratings if r.get('rating', 0) >= 4])
        st.metric(
            label="👍 Pozitif Oran",
            value=f"%{positive_count/len(all_ratings)*100:.0f}" if all_ratings else "0%"
        )

def show_overview_analysis(data):
    """Genel bakış analizleri"""
    
    text_reviews = data.get('text_reviews', [])
    all_ratings = data.get('all_ratings', [])
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Puan dağılımı
        st.subheader("📊 Puan Dağılımı")
        if all_ratings:
            ratings_df = pd.DataFrame(all_ratings)
            ratings_df = ratings_df[ratings_df['rating'].notna()]
            
            # Rating dağılımını hesapla
            rating_counts = ratings_df['rating'].value_counts().sort_index()
            
            fig = px.bar(
                x=rating_counts.index,
                y=rating_counts.values,
                title=f"Kullanıcı Puanları Dağılımı (Toplam: {len(all_ratings)})",
                color=rating_counts.values,
                color_continuous_scale='RdYlGn',
                text=rating_counts.values
            )
            fig.update_traces(texttemplate='%{text}', textposition='outside')
            fig.update_layout(
                xaxis_title="⭐ Puan",
                yaxis_title="Yorum Sayısı",
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(tickmode='linear', tick0=1, dtick=1)
            )
            st.plotly_chart(fig, use_container_width=True, key="rating_distribution")
            
            # Rating istatistikleri
            avg_rating = ratings_df['rating'].mean()
            st.markdown("**📈 Puan İstatistikleri:**")
            col1_1, col1_2, col1_3 = st.columns(3)
            with col1_1:
                st.metric("Ortalama Puan", f"{avg_rating:.1f}⭐", delta=f"{avg_rating-3:.1f}")
            with col1_2:
                positive_count = len(ratings_df[ratings_df['rating'] >= 4])
                positive_rate = (positive_count/len(ratings_df)*100) if len(ratings_df) > 0 else 0
                st.metric("Pozitif (4-5⭐)", f"{positive_count}", delta=f"%{positive_rate:.1f}")
            with col1_3:
                negative_count = len(ratings_df[ratings_df['rating'] <= 2])
                negative_rate = (negative_count/len(ratings_df)*100) if len(ratings_df) > 0 else 0
                st.metric("Negatif (1-2⭐)", f"{negative_count}", delta=f"%{negative_rate:.1f}")
        else:
            st.warning("⚠️ Puan dağılımı için veri bulunamadı")
    
    with col2:
        # Zaman dağılımı
        st.subheader("📅 Akıllı Zaman Dağılımı")
        if text_reviews:
            time_data = analyze_time_distribution_advanced(text_reviews)
            
            if time_data['labels'] and time_data['values'] and any(v > 0 for v in time_data['values']):
                time_df = pd.DataFrame({
                    'Zaman Aralığı': time_data['labels'],
                    'Yorum Sayısı': time_data['values']
                })
                
                fig = px.bar(
                    time_df,
                    x='Zaman Aralığı',
                    y='Yorum Sayısı',
                    title=f"📊 Gerçek Zamanlı Analiz (Toplam: {sum(time_data['values'])})",
                    color='Yorum Sayısı',
                    color_continuous_scale='Turbo',
                    text='Yorum Sayısı'
                )
                fig.update_traces(texttemplate='%{text}', textposition='outside')
                fig.update_layout(
                    xaxis_title="⏰ Zaman Aralığı",
                    yaxis_title="📊 Yorum Sayısı",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig, use_container_width=True, key="time_distribution_advanced")
                
                # Zaman parsing örnekleri göster
                with st.expander("🔍 Zaman Parsing Örnekleri"):
                    sample_times = time_data.get('processed_times', [])[:5]
                    for i, item in enumerate(sample_times, 1):
                        original = item['original']
                        timestamp = item['timestamp']
                        category = item['category']
                        formatted_time = timestamp.strftime('%d.%m.%Y %H:%M')
                        st.write(f"**{i}.** `{original}` → **{formatted_time}** → `{category}`")
                
                # Gelişmiş zaman istatistikleri
                st.markdown("**⏰ Detaylı Zaman İstatistikleri:**")
                col2_1, col2_2, col2_3, col2_4 = st.columns(4)
                
                with col2_1:
                    recent_count = sum(v for k, v in zip(time_data['labels'], time_data['values']) 
                                     if 'Son' in k and ('saat' in k or '24' in k))
                    recent_rate = (recent_count/len(text_reviews)*100) if len(text_reviews) > 0 else 0
                    st.metric("🔥 Güncel Yorumlar", f"{recent_count}", delta=f"%{recent_rate:.1f}")
                
                with col2_2:
                    if time_data['values']:
                        max_index = time_data['values'].index(max(time_data['values']))
                        max_period = time_data['labels'][max_index]
                        st.metric("📈 En Aktif Dönem", max_period, delta=f"{max(time_data['values'])} yorum")
                    else:
                        st.metric("📈 En Aktif Dönem", "Veri yok", delta="0 yorum")
                
                with col2_3:
                    total_periods = len([v for v in time_data['values'] if v > 0])
                    st.metric("📊 Aktif Dönem", f"{total_periods}", delta="farklı zaman")
                
                with col2_4:
                    # En eski yorumun ne zaman olduğunu bul
                    processed_times = time_data.get('processed_times', [])
                    if processed_times:
                        oldest_time = min(processed_times, key=lambda x: x['timestamp'])
                        oldest_category = oldest_time['category']
                        st.metric("⏳ En Eski Yorum", oldest_category, delta=oldest_time['original'][:15])
                    else:
                        st.metric("⏳ En Eski Yorum", "Belirsiz", delta="")
                        
            else:
                st.warning("⚠️ Zaman dağılımı için yeterli veri yok")
        else:
            st.warning("⚠️ Analiz için yorum bulunamadı")
    
    # Yorum örnekleri
    st.subheader("💬 Son Yorumlar")
    show_recent_reviews(text_reviews[:5])

def show_detailed_analysis(data):
    """Detaylı analizler"""
    
    text_reviews = data.get('text_reviews', [])
    all_ratings = data.get('all_ratings', [])
    
    # Puan vs Metin uzunluğu analizi
    st.subheader("📏 Puan vs Yorum Uzunluğu Analizi")
    
    if text_reviews:
        review_analysis = []
        for review in text_reviews:
            if isinstance(review, dict):
                rating = int(review.get('rating', 0)) if str(review.get('rating', '')).isdigit() else 0
                text_length = len(review.get('review_text', ''))
                review_analysis.append({
                    'rating': rating,
                    'text_length': text_length,
                    'reviewer': review.get('reviewer_name', 'Unknown')
                })
        
        if review_analysis:
            analysis_df = pd.DataFrame(review_analysis)
            
            fig = px.scatter(
                analysis_df,
                x='rating',
                y='text_length',
                hover_data=['reviewer'],
                title="Puan vs Yorum Uzunluğu İlişkisi",
                color='rating',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(
                xaxis_title="Verilen Puan",
                yaxis_title="Yorum Uzunluğu (karakter)",
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True, key="sentiment_analysis")
    
    # İki sütunlu detaylı analiz
    col1, col2 = st.columns(2)
    
    with col1:
        # Yorum uzunluğu dağılımı
        st.subheader("📝 Yorum Uzunluğu Dağılımı")
        if text_reviews:
            lengths = [len(r.get('review_text', '')) for r in text_reviews if isinstance(r, dict)]
            
            fig = px.histogram(
                x=lengths,
                nbins=10,
                title="Yorum Uzunluklarının Dağılımı",
                color_discrete_sequence=['#4ECDC4']
            )
            fig.update_layout(
                xaxis_title="Karakter Sayısı",
                yaxis_title="Yorum Sayısı",
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True, key="comment_length")
    
    with col2:
        # Aktif kullanıcılar
        st.subheader("👥 En Aktif Yorumcular")
        if text_reviews:
            reviewers = [r.get('reviewer_name', 'Unknown') for r in text_reviews if isinstance(r, dict)]
            reviewer_counts = Counter(reviewers)
            
            top_reviewers = dict(reviewer_counts.most_common(5))
            
            if top_reviewers:
                reviewer_df = pd.DataFrame({
                    'Kullanıcı': list(top_reviewers.keys()),
                    'Yorum Sayısı': list(top_reviewers.values())
                })
                
                fig = px.bar(
                    reviewer_df,
                    x='Yorum Sayısı',
                    y='Kullanıcı',
                    orientation='h',
                    title="En Çok Yorum Yapan Kullanıcılar",
                    color='Yorum Sayısı',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    xaxis_title="Yorum Sayısı",
                    yaxis_title="Kullanıcı",
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)'
                )
            st.plotly_chart(fig, use_container_width=True, key="active_reviewers")

def show_word_analysis(data):
    """Kelime analizi"""
    
    text_reviews = data.get('text_reviews', [])
    
    if not text_reviews:
        st.warning("📝 Kelime analizi için yeterli metin verisi yok.")
        return
    
    # Tüm yorumları birleştir
    all_text = " ".join([
        r.get('review_text', '') for r in text_reviews 
        if isinstance(r, dict) and r.get('review_text')
    ])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("☁️ Kelime Bulutu")
        
        if all_text:
            try:
                # Türkçe stopwords
                turkish_stopwords = {
                    'bir', 'bu', 've', 'ile', 'için', 'çok', 'daha', 'olan', 'olan',
                    'var', 'yok', 'gibi', 'kadar', 'ancak', 'ama', 'fakat', 'veya',
                    'hiç', 'her', 'şey', 'de', 'da', 'ki', 'mi', 'mu', 'mı', 'mü'
                }
                
                wordcloud = WordCloud(
                    width=400,
                    height=300,
                    background_color='white',
                    stopwords=turkish_stopwords,
                    max_words=50,
                    colormap='viridis'
                ).generate(all_text)
                
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
                
            except Exception as e:
                st.error(f"Kelime bulutu oluşturulamadı: {str(e)}")
    
    with col2:
        st.subheader("🔤 En Sık Kullanılan Kelimeler")
        
        # Kelime frekansı analizi
        words = re.findall(r'\b\w+\b', all_text.lower())
        turkish_stopwords = {
            'bir', 'bu', 've', 'ile', 'için', 'çok', 'daha', 'olan', 'var', 'yok',
            'gibi', 'kadar', 'ancak', 'ama', 'fakat', 'veya', 'hiç', 'her', 'şey',
            'de', 'da', 'ki', 'mi', 'mu', 'mı', 'mü', 'the', 'and', 'is', 'in', 'it'
        }
        
        filtered_words = [w for w in words if len(w) > 3 and w not in turkish_stopwords]
        word_freq = Counter(filtered_words).most_common(10)
        
        if word_freq:
            words_df = pd.DataFrame(word_freq, columns=['Kelime', 'Frekans'])
            
            fig = px.bar(
                words_df,
                x='Frekans',
                y='Kelime',
                orientation='h',
                title="En Sık Kullanılan Kelimeler",
                color='Frekans',
                color_continuous_scale='Sunset'
            )
            fig.update_layout(
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True, key="word_frequency")

def show_recommendations(data):
    """Akıllı öneriler"""
    
    text_reviews = data.get('text_reviews', [])
    stats = data.get('statistics', {})
    
    st.subheader("💡 Akıllı Öneriler ve İçgörüler")
    
    avg_rating = stats.get('rating_average', 0)
    total_reviews = len(text_reviews)
    
    insights = []
    
    # Puan bazlı öneriler
    if avg_rating < 3:
        insights.append({
            'type': '🚨 Kritik',
            'title': 'Düşük Puan Uyarısı',
            'content': f'Ortalama puan {avg_rating:.1f}/5 oldukça düşük. Acil iyileştirme gerekiyor.'
        })
    elif avg_rating < 4:
        insights.append({
            'type': '⚠️ Dikkat',
            'title': 'Orta Seviye Performans',
            'content': f'Ortalama puan {avg_rating:.1f}/5. İyileştirme alanları mevcut.'
        })
    else:
        insights.append({
            'type': '✅ Pozitif',
            'title': 'Yüksek Müşteri Memnuniyeti',
            'content': f'Ortalama puan {avg_rating:.1f}/5 mükemmel seviyede!'
        })
    
    # Yorum sayısı analizi
    if total_reviews < 10:
        insights.append({
            'type': '💡 Öneri',
            'title': 'Daha Fazla Yorum Gerekli',
            'content': 'Güvenilir analiz için daha fazla yorum toplayın.'
        })
    
    # Negatif yorum analizi
    if text_reviews:
        negative_reviews = [
            r for r in text_reviews 
            if isinstance(r, dict) and str(r.get('rating', '')).isdigit() and int(r.get('rating', 0)) <= 2
        ]
        
        if len(negative_reviews) > total_reviews * 0.3:
            insights.append({
                'type': '🔍 Analiz',
                'title': 'Yüksek Negatif Yorum Oranı',
                'content': f'Yorumların %{len(negative_reviews)/total_reviews*100:.0f}\'si negatif. Temel sorunları tespit edin.'
            })
    
    # Önerileri göster
    for insight in insights:
        if insight['type'] == '🚨 Kritik':
            st.error(f"**{insight['title']}:** {insight['content']}")
        elif insight['type'] == '⚠️ Dikkat':
            st.warning(f"**{insight['title']}:** {insight['content']}")
        elif insight['type'] == '✅ Pozitif':
            st.success(f"**{insight['title']}:** {insight['content']}")
        else:
            st.info(f"**{insight['title']}:** {insight['content']}")
    
    # Aksiyon önerileri
    st.subheader("🎯 Önerilen Aksiyonlar")
    
    action_items = []
    
    if avg_rating < 3.5:
        action_items.extend([
            "🔧 Müşteri şikayetlerini analiz edin",
            "📞 Negatif yorumlara yanıt verin",
            "⚡ Hızlı iyileştirmeler yapın"
        ])
    
    if total_reviews < 20:
        action_items.append("📢 Daha fazla müşteriden yorum isteyin")
    
    action_items.extend([
        "📊 Düzenli olarak yorumları takip edin",
        "💬 Pozitif yorumlara teşekkür edin",
        "🎯 Müşteri deneyimini sürekli iyileştirin"
    ])
    
    for action in action_items:
        st.write(f"• {action}")

def show_recent_reviews(reviews):
    """Son yorumları gösterir - iyileştirilmiş"""
    
    if not reviews:
        st.warning("⚠️ Görüntülenecek yorum bulunamadı!")
        return
    
    # En fazla 5 yorum göster
    display_reviews = reviews[:5]
    
    for i, review in enumerate(display_reviews, 1):
        if isinstance(review, dict):
            reviewer_name = review.get('reviewer_name', 'Bilinmeyen Kullanıcı')
            rating = review.get('rating', 'N/A')
            date_original = review.get('date', 'Tarih bilinmiyor')
            review_text = review.get('review_text', 'Metin yorumu yok')
            
            # Gerçek timestamp hesapla
            timestamp = parse_relative_time_to_timestamp(date_original)
            formatted_date = timestamp.strftime('%d.%m.%Y %H:%M')
            time_category = categorize_timestamp(timestamp)
            
            # Yorum kartı oluştur - iyileştirilmiş
            reviewer_name_safe = reviewer_name.replace('<', '&lt;').replace('>', '&gt;')
            review_text_safe = review_text.replace('<', '&lt;').replace('>', '&gt;')
            
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
                        👤 {reviewer_name} • ⭐ {rating} yıldız
                    </h4>
                    <p style="margin: 5px 0; opacity: 0.8; font-size: 14px;">
                        � {date_original}   {formatted_date}   {time_category}
                    </p>
                    <p style="margin: 10px 0 0 0; line-height: 1.5;">
                        💬 {review_text_safe[:600]}{'...' if len(review_text_safe) > 600 else ''}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    # Toplam yorum sayısını göster
    st.info(f"📊 Toplam {len(reviews)} metin yorumu var. Yukarıda ilk {len(display_reviews)} tanesi gösteriliyor.")

def count_recent_reviews(reviews, hours=24):
    """Son X saatteki yorum sayısını hesaplar"""
    
    recent_keywords = ['saat önce', 'dakika önce', 'hour ago', 'minute ago']
    count = 0
    
    for review in reviews:
        if isinstance(review, dict):
            date_str = review.get('date', '').lower()
            if any(keyword in date_str for keyword in recent_keywords):
                count += 1
    
    return count

def parse_relative_time_to_timestamp(date_str):
    """
    Türkçe/İngilizce relatif zaman ifadelerini gerçek timestamp'e çevirir
    
    Örnekler:
    - "bir saat önce" → datetime object
    - "2 gün önce" → datetime object
    - "bir yıl önce" → datetime object
    """
    
    # Türkiye saati için timezone
    turkey_tz = pytz.timezone('Europe/Istanbul')
    current_time = datetime.now(turkey_tz)
    
    if not date_str or not isinstance(date_str, str):
        return current_time
    
    date_str = date_str.lower().strip()
    
    # Düzenlendi kısımlarını temizle
    date_str = re.sub(r'düzenlendi.*$', '', date_str).strip()
    date_str = re.sub(r'edited.*$', '', date_str).strip()
    
    # Sayıları çıkar
    numbers = re.findall(r'\d+', date_str)
    number = int(numbers[0]) if numbers else 1
    
    # "bir", "bir kaç" gibi text sayıları
    if 'bir ' in date_str or date_str.startswith('bir'):
        number = 1
    elif 'birkaç' in date_str or 'few' in date_str:
        number = 3
    elif 'çeyrek' in date_str:
        number = 15  # dakika için
    elif 'yarım' in date_str or 'half' in date_str:
        number = 30  # dakika için
    
    # Zaman birimini belirle ve çıkar
    if any(x in date_str for x in ['saniye', 'second']):
        delta = timedelta(seconds=number)
    elif any(x in date_str for x in ['dakika', 'minute']):
        delta = timedelta(minutes=number)
    elif any(x in date_str for x in ['saat', 'hour']):
        delta = timedelta(hours=number)
    elif any(x in date_str for x in ['gün', 'day']):
        delta = timedelta(days=number)
    elif any(x in date_str for x in ['hafta', 'week']):
        delta = timedelta(weeks=number)
    elif any(x in date_str for x in ['ay', 'month']):
        # Ay hesaplaması (ortalama 30.44 gün)
        delta = timedelta(days=number * 30.44)
    elif any(x in date_str for x in ['yıl', 'year']):
        # Yıl hesaplaması (365.25 gün - artık yıl dahil)
        delta = timedelta(days=number * 365.25)
    else:
        # Tanımlanamayan durumlar için varsayılan
        delta = timedelta(hours=1)
    
    # Geçmişe git
    calculated_time = current_time - delta
    return calculated_time

def categorize_timestamp(timestamp):
    """
    Timestamp'i zaman kategorilerine ayırır
    """
    
    turkey_tz = pytz.timezone('Europe/Istanbul')
    current_time = datetime.now(turkey_tz)
    
    # Timestamp'in timezone'unu kontrol et
    if timestamp.tzinfo is None:
        timestamp = turkey_tz.localize(timestamp)
    
    time_diff = current_time - timestamp
    
    if time_diff.total_seconds() < 3600:  # 1 saat
        return "Son 1 saat"
    elif time_diff.total_seconds() < 86400:  # 1 gün
        return "Son 24 saat"
    elif time_diff.days < 7:  # 1 hafta
        return "Son hafta"
    elif time_diff.days < 30:  # 1 ay
        return "Son ay"
    elif time_diff.days < 365:  # 1 yıl
        return "Son yıl"
    else:
        return "1+ yıl önce"

def test_time_parsing():
    """Zaman parsing'i test et"""
    
    st.subheader("🧪 Zaman Parsing Test")
    
    # Test verileri - gerçek CSV'den
    test_dates = [
        "2 saat önce",
        "4 saat önce", 
        "11 saat önce",
        "22 saat önce",
        "bir gün önce",
        "bir gün önce düzenlendi",
        "bir hafta önce",
        "2 ay önce",
        "bir yıl önce"
    ]
    
    st.write("**Test Sonuçları:**")
    
    results = []
    for date_str in test_dates:
        try:
            timestamp = parse_relative_time_to_timestamp(date_str)
            category = categorize_timestamp(timestamp)
            formatted = timestamp.strftime('%d.%m.%Y %H:%M')
            
            results.append({
                'Orijinal': date_str,
                'Timestamp': formatted,
                'Kategori': category,
                'Durum': '✅ Başarılı'
            })
        except Exception as e:
            results.append({
                'Orijinal': date_str,
                'Timestamp': 'HATA',
                'Kategori': 'HATA', 
                'Durum': f'❌ {str(e)}'
            })
    
    # Sonuçları tablo olarak göster
    df_results = pd.DataFrame(results)
    st.dataframe(df_results, use_container_width=True)
    
    return results

def analyze_time_distribution_advanced(reviews):
    """
    Gelişmiş zaman dağılımı analizi - gerçek timestamp hesaplaması
    """
    
    time_categories = {
        'Son 1 saat': 0,
        'Son 24 saat': 0,
        'Son hafta': 0,
        'Son ay': 0,
        'Son yıl': 0,
        '1+ yıl önce': 0
    }
    
    processed_times = []
    
    for review in reviews:
        if isinstance(review, dict):
            date_str = review.get('date', '')
            
            # Text'i timestamp'e çevir
            timestamp = parse_relative_time_to_timestamp(date_str)
            
            # Kategoriyi belirle
            category = categorize_timestamp(timestamp)
            time_categories[category] += 1
            
            # Debug için sakla
            processed_times.append({
                'original': date_str,
                'timestamp': timestamp,
                'category': category
            })
    
    # Debug info (ilk 3 örnek)
    # st.write("🔍 **Zaman Parsing Örnekleri:**")
    # for i, item in enumerate(processed_times[:3]):
    #     st.write(f"{i+1}. '{item['original']}' → {item['timestamp'].strftime('%Y-%m-%d %H:%M')} → {item['category']}")
    
    # Sadece 0'dan büyük değerleri döndür
    filtered_categories = {k: v for k, v in time_categories.items() if v > 0}
    
    if not filtered_categories:
        return {
            'labels': ['Zaman bilgisi belirsiz'],
            'values': [len(reviews)],
            'processed_times': processed_times
        }
    
    return {
        'labels': list(filtered_categories.keys()),
        'values': list(filtered_categories.values()),
        'processed_times': processed_times
    }

# Ana uygulama akışı
if __name__ == "__main__":
    main()
    
    # Veri varsa analitikleri göster
    if 'live_data' in st.session_state:
        show_analytics()
