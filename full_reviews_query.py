#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print('🔍 TAM GENİŞLETİLMİŞ YORUMLARIN TAM HALİ - VERİTABANI SORGUSU')
print('=' * 70)

from database_test import ReviewsDatabase

db = ReviewsDatabase('main_reviews.db')
df = db.get_all_reviews()

if len(df) > 0:
    # 300+ karakter olan yorumları getir (tam genişletilmiş)
    long_reviews = df[df['review_text'].str.len() > 300].copy()
    long_reviews = long_reviews.sort_values('review_text', key=lambda x: x.str.len(), ascending=False)
    
    print(f'📊 300+ karakterli tam genişletilmiş yorum sayısı: {len(long_reviews)}')
    print()
    
    for i, (idx, row) in enumerate(long_reviews.iterrows()):
        reviewer = row['reviewer_name']
        text_length = len(row['review_text'])
        date = row['date_original']
        rating = row['rating']
        business = row['business_name']
        full_text = row['review_text']
        
        print(f'🌟 YORUM #{i+1}:')
        print(f'   👤 Yorumcu: {reviewer}')
        print(f'   ⭐ Puan: {rating} yıldız')
        print(f'   📅 Tarih: {date}')
        print(f'   🏢 İşletme: {business}')
        print(f'   📏 Uzunluk: {text_length} karakter')
        print(f'   📝 TAM METİN:')
        print(f'   "{full_text}"')
        print()
        print('─' * 70)
        print()
        
    # En uzun yorumu özel olarak göster
    if len(long_reviews) > 0:
        longest = long_reviews.iloc[0]
        print(f'🏆 EN UZUN YORUM REKORDEĞERİ:')
        print(f'   👤 {longest["reviewer_name"]}')
        print(f'   📏 {len(longest["review_text"])} karakter')
        print(f'   📊 Bu yorumun kelime sayısı: {len(longest["review_text"].split())} kelime')
        print(f'   📊 Ortalama kelime uzunluğu: {len(longest["review_text"])/len(longest["review_text"].split()):.1f} karakter/kelime')
        
        # Yorumun içindeki özel ifadeleri ara
        text_lower = longest["review_text"].lower()
        interesting_phrases = []
        
        if 'çok' in text_lower:
            interesting_phrases.append('Yoğun duygusal ifade ("çok" kelimesi)')
        if 'ama' in text_lower or 'ancak' in text_lower:
            interesting_phrases.append('Karşıt görüş ifadesi')
        if '!' in longest["review_text"]:
            interesting_phrases.append(f'{longest["review_text"].count("!")} adet ünlem işareti')
        if '?' in longest["review_text"]:
            interesting_phrases.append(f'{longest["review_text"].count("?")} adet soru işareti')
            
        if interesting_phrases:
            print(f'   🔍 İçerik analizi: {", ".join(interesting_phrases)}')
        
        print()
        
else:
    print('❌ Veritabanında veri yok')

print('✅ Tam genişletilmiş yorumların tam hali gösterildi!')
