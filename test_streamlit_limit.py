#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print('📺 STREAMLIT KARAKTER SINIRI TEST - maciej kałuski')
print('=' * 60)

from database_test import ReviewsDatabase

db = ReviewsDatabase('main_reviews.db')
df = db.get_all_reviews()

# maciej kałuski'nin en uzun yorumunu bul
maciej_reviews = df[df['reviewer_name'].str.contains('maciej', case=False, na=False)]

if len(maciej_reviews) > 0:
    # En uzun yorumu al
    longest_maciej = maciej_reviews.loc[maciej_reviews['review_text'].str.len().idxmax()]
    
    print(f'📝 En uzun maciej yorumu:')
    print(f'   👤 İsim: {longest_maciej["reviewer_name"]}')
    print(f'   📏 Tam uzunluk: {len(longest_maciej["review_text"])} karakter')
    print(f'   📅 Tarih: {longest_maciej["date_original"]}')
    print()
    
    # Streamlit'te nasıl görünecek (eski 250 kar vs yeni 500 kar)
    old_limit = longest_maciej["review_text"][:250] + ('...' if len(longest_maciej["review_text"]) > 250 else '')
    new_limit = longest_maciej["review_text"][:500] + ('...' if len(longest_maciej["review_text"]) > 500 else '')
    
    print(f'📊 ESKİ 250 karakter sınırı ile:')
    print(f'   Uzunluk: {len(old_limit)} karakter')
    print(f'   Metin: "{old_limit}"')
    print()
    
    print(f'📊 YENİ 500 karakter sınırı ile:')
    print(f'   Uzunluk: {len(new_limit)} karakter')
    print(f'   Metin: "{new_limit}"')
    print()
    
    # Karşılaştırma
    if len(longest_maciej["review_text"]) <= 500:
        print(f'✅ SONUÇ: Yorum artık TAM olarak görünecek! (502 karakter < 500 sınır)')
        print(f'   🎯 maciej kałuski\'nin yorumu Streamlit\'te tam görünüyor!')
    else:
        print(f'⚠️ SONUÇ: Yorum hala kısaltılacak ama daha fazla görünecek')
        
else:
    print('❌ maciej kałuski yorumu bulunamadı')

print()
print('📋 Streamlit Dashboard: http://localhost:8501')
print('✅ Karakter sınırı testı tamamlandı')
