#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print('📊 DAHA FAZLA GENİŞLETME ANALİZİ - MEVCUT VERİLER')
print('=' * 60)

from database_test import ReviewsDatabase

db = ReviewsDatabase('main_reviews.db')
df = db.get_all_reviews()

# Yorum uzunluklarına göre kategorize et
if len(df) > 0:
    text_lengths = []
    for _, row in df.iterrows():
        text = row['review_text'] if row['review_text'] else ''
        length = len(text)
        text_lengths.append({
            'reviewer': row['reviewer_name'][:20],
            'length': length,
            'text_preview': text[:100] + '...' if len(text) > 100 else text,
            'date': row['date_original']
        })
    
    # Uzunluk sıralaması
    text_lengths.sort(key=lambda x: x['length'], reverse=True)
    
    print('🔝 EN UZUN YORUMLAR (Muhtemelen genişletilmiş):')
    for i, item in enumerate(text_lengths[:8]):
        reviewer = item['reviewer']
        length = item['length']
        preview = item['text_preview']
        print(f'{i+1:2d}. {reviewer:20} | {length:3d} kar. | {preview}')
    
    print()
    print('📏 KISA YORUMLAR (Genişletilmemiş/gerekmiyor):')
    short_reviews = [x for x in text_lengths if x['length'] > 0 and x['length'] < 150]
    for i, item in enumerate(short_reviews[:5]):
        reviewer = item['reviewer']
        length = item['length']
        preview = item['text_preview']
        print(f'{i+1:2d}. {reviewer:20} | {length:3d} kar. | {preview}')
    
    # İstatistikler
    lengths_only = [x['length'] for x in text_lengths if x['length'] > 0]
    
    print()
    print('📈 GENEL İSTATİSTİKLER:')
    print(f'  Toplam yorum: {len(lengths_only)}')
    print(f'  Ortalama uzunluk: {sum(lengths_only)/len(lengths_only):.1f} karakter')
    print(f'  En kısa: {min(lengths_only)} karakter')
    print(f'  En uzun: {max(lengths_only)} karakter')
    
    # Başarı analizi
    very_long = len([x for x in lengths_only if x > 300])
    medium = len([x for x in lengths_only if 150 <= x <= 300])
    short = len([x for x in lengths_only if x < 150])
    
    print()
    print('✅ DAHA FAZLA GENİŞLETME BAŞARI ANALİZİ:')
    print(f'  300+ karakter (tam genişletilmiş): {very_long} adet ({very_long/len(lengths_only)*100:.1f}%)')
    print(f'  150-300 karakter (kısmi/orta): {medium} adet ({medium/len(lengths_only)*100:.1f}%)')
    print(f'  150- karakter (genişletilmemiş): {short} adet ({short/len(lengths_only)*100:.1f}%)')
    
    if very_long > 0:
        print()
        print('🎯 SONUÇ: "Daha fazla" genişletme sistemi ÇALIŞIYOR!')
        print(f'  {very_long} yorumda tam genişletme başarılı!')
        
        # En başarılı örnekleri göster
        print()
        print('🌟 EN BAŞARILI GENİŞLETME ÖRNEKLERİ:')
        super_long = [x for x in text_lengths if x['length'] > 350]
        for i, item in enumerate(super_long[:5]):
            print(f'  {i+1}. {item["reviewer"]:15} - {item["length"]} karakter')
            print(f'     "{item["text_preview"][:120]}..."')
            print()
    else:
        print()
        print('⚠️ SONUÇ: Henüz tam genişletilmiş uzun yorum tespit edilmedi.')

else:
    print('❌ Veritabanında veri yok')
