#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print('📺 DATABASE_DASHBOARD.PY - 600 KARAKTER SINIRI TESTİ')
print('=' * 60)

from database_test import ReviewsDatabase

db = ReviewsDatabase('main_reviews.db')
df = db.get_all_reviews()

if len(df) > 0:
    # En uzun yorumları bul
    df_sorted = df.sort_values('review_text', key=lambda x: x.str.len(), ascending=False)
    top_10_long = df_sorted.head(10)
    
    print(f'📊 En uzun 10 yorumun 600 karakter sınırı analizi:')
    print()
    
    for i, (idx, row) in enumerate(top_10_long.iterrows()):
        reviewer = row['reviewer_name'][:20]
        text_len = len(row['review_text'])
        
        if text_len <= 600:
            status = '✅ TAM GÖRÜNÜR'
            display_len = text_len
        else:
            status = f'⚠️ {text_len-600} KARAKTER KESİLİR'
            display_len = 603  # 600 + "..."
        
        print(f'{i+1:2d}. {reviewer:20} | {text_len:3d} kar | {status}')
    
    print()
    
    # maciej kałuski özel kontrol
    maciej_reviews = df[df['reviewer_name'].str.contains('maciej', case=False, na=False)]
    
    if len(maciej_reviews) > 0:
        longest_maciej = maciej_reviews.loc[maciej_reviews['review_text'].str.len().idxmax()]
        
        print(f'🎯 maciej kałuski ÖZEL KONTROL:')
        print(f'   📏 Yorum uzunluğu: {len(longest_maciej["review_text"])} karakter')
        
        if len(longest_maciej["review_text"]) <= 600:
            print(f'   ✅ MÜKEMMEL! Yorumu TAM olarak görünecek!')
            print(f'   🎉 {len(longest_maciej["review_text"])} karakter < 600 sınır')
        else:
            missing_chars = len(longest_maciej["review_text"]) - 600
            print(f'   ⚠️ {missing_chars} karakter kesilecek')
            
        # Görünecek metin preview
        displayed_text = longest_maciej["review_text"][:600] + ('...' if len(longest_maciej["review_text"]) > 600 else '')
        print(f'   📺 Dashboard\'ta görünecek:')
        print(f'   "{displayed_text}"')
        print()
    
    # Genel istatistik
    total_reviews = len(df)
    fully_visible = len(df[df['review_text'].str.len() <= 600])
    partially_cut = total_reviews - fully_visible
    
    print(f'📈 GENEL İSTATİSTİK:')
    print(f'   📊 Toplam yorum: {total_reviews}')
    print(f'   ✅ Tam görünür: {fully_visible} adet ({fully_visible/total_reviews*100:.1f}%)')
    print(f'   ⚠️ Kısaltılır: {partially_cut} adet ({partially_cut/total_reviews*100:.1f}%)')
    
    if fully_visible/total_reviews >= 0.95:
        print(f'   🎯 SONUÇ: MÜKEMMEL! Yorumların %{fully_visible/total_reviews*100:.1f}\'i tam görünüyor!')
    elif fully_visible/total_reviews >= 0.90:
        print(f'   ✅ SONUÇ: İYİ! Yorumların büyük çoğunluğu tam görünüyor.')
    else:
        print(f'   ⚠️ SONUÇ: Daha yüksek sınır gerekebilir.')
        
else:
    print('❌ Veritabanında veri yok')

print()
print('📋 Database Dashboard: http://localhost:8501')
print('✅ 600 karakter sınırı analizi tamamlandı')
