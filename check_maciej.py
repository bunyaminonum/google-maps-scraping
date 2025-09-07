#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database_test import ReviewsDatabase

db = ReviewsDatabase('main_reviews.db')
df = db.get_all_reviews()

# maciej kałuski'nin yorumunu bul
maciej_reviews = df[df['reviewer_name'].str.contains('maciej', case=False, na=False)]

print('🔍 maciej kałuski YORUM KONTROLÜ:')
print('=' * 60)

if len(maciej_reviews) > 0:
    for i, (idx, row) in enumerate(maciej_reviews.iterrows()):
        print(f'📝 Yorum #{i+1}:')
        print(f'   👤 İsim: {row["reviewer_name"]}')
        print(f'   📏 Uzunluk: {len(row["review_text"])} karakter')
        print(f'   📅 Tarih: {row["date_original"]}')
        print(f'   🏢 İşletme: {row["business_name"]}')
        print(f'   📝 TAM METİN:')
        print(f'   "{row["review_text"]}"')
        print()
        print(f'📊 İlk 100 karakter: "{row["review_text"][:100]}..."')
        print(f'📊 Son 100 karakter: "...{row["review_text"][-100:]}"')
        print()
        
        # Streamlit'te görünecek hali (karakter sınırı varsa)
        truncated_150 = row["review_text"][:150] + "..." if len(row["review_text"]) > 150 else row["review_text"]
        truncated_200 = row["review_text"][:200] + "..." if len(row["review_text"]) > 200 else row["review_text"]
        truncated_300 = row["review_text"][:300] + "..." if len(row["review_text"]) > 300 else row["review_text"]
        
        print(f'📺 Streamlit 150 kar sınırı: "{truncated_150}"')
        print(f'📺 Streamlit 200 kar sınırı: "{truncated_200}"')
        print(f'📺 Streamlit 300 kar sınırı: "{truncated_300}"')
        print()
else:
    print('❌ maciej kałuski yorumu bulunamadı')

print('✅ Veritabanı kontrolü tamamlandı')
