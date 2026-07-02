import pandas as pd

print("GÜMRÜK KONTROLÜ BAŞLADI: Radardaki oyunlar filtreleniyor...")

# 1. Radar dosyamızı okuyoruz
try:
    radar_df = pd.read_csv("../data/radar_tablosu.csv")
except FileNotFoundError:
    print("HATA: Radar dosyası bulunamadı! Önce 1_radar_cek.py kodunu çalıştırmalısın.")
    exit()

# 2. Toplam Etkileşimi (İnceleme Sayısını) hesaplıyoruz
radar_df['toplam_inceleme'] = radar_df['positive'] + radar_df['negative']

# 3. GÜMRÜK FİLTRESİ: Sadece incelemesi 500'den büyük olanları al!
buyuk_oyunlar = radar_df[radar_df['toplam_inceleme'] >= 500].copy()
print(f"Radardaki {len(radar_df)} oyundan {len(buyuk_oyunlar)} tanesi gümrükten geçmeyi başardı.")

# 4. Ülke Atama Sözlüğümüz (Şimdilik Manuel, İleride API olacak)
ulke_sozlugu = {
    "Valve": "ABD",
    "Rockstar Games": "ABD",
    "Paradox Interactive": "İsveç",
    "CD PROJEKT RED": "Polonya",
    "Ubisoft": "Fransa",
    "TaleWorlds Entertainment": "Türkiye",
    "Klei Entertainment": "Kanada",
    "Re-Logic": "ABD",
    "Bethesda Game Studios": "ABD",
    "SCS Software": "Çekya",
    "Facepunch Studios": "İngiltere",
    "Krafton": "Güney Kore",
    "CAPCOM Co., Ltd.": "Japonya",
    "FromSoftware Inc.": "Japonya"
}

# 5. Stüdyo isimlerine bakarak ülkeleri eşleştiriyoruz
buyuk_oyunlar['ulke'] = buyuk_oyunlar['developer'].map(ulke_sozlugu)

# Sözlükte olmayan stüdyoların ülkesine "Bilinmiyor" yazıyoruz ki sistem çökmesin
buyuk_oyunlar['ulke'] = buyuk_oyunlar['ulke'].fillna('Bilinmiyor')

# 6. Temizlenmiş ve ülkesi bulunmuş bu elit oyunları ANA VİTRİN tablomuza kaydediyoruz.
buyuk_oyunlar.to_csv("../data/ana_vitrin_tablosu.csv", index=False)

print("İşlem Tamam! Pazar analizine uygun elit oyunlar 'data/ana_vitrin_tablosu.csv' dosyasına aktarıldı.")