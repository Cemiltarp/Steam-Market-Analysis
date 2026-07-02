import requests
import pandas as pd
from datetime import datetime
import os

print("RADAR ÇALIŞTIRILIYOR: Steam'deki güncel oyunlar taranıyor...")

# 1. BULUNDUĞUMUZ YERİ GARANTİYE ALIYORUZ (Hata Çözümü!)
# Bu kodlar, projeyi nereden çalıştırırsan çalıştır 'data' klasörünü otomatik bulur.
ana_klasor = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_klasoru = os.path.join(ana_klasor, "data")
radar_dosya_yolu = os.path.join(data_klasoru, "radar_tablosu.csv")

# 2. SteamSpy'dan son popüler oyunları çekiyoruz
url = "https://steamspy.com/api.php?request=top100in2weeks"
cevap = requests.get(url)
ham_veri = cevap.json()

# 3. Gelen JSON verisini Pandas tablosuna dönüştürüyoruz
tablo = pd.DataFrame(list(ham_veri.values()))

# 4. Sadece işimize yarayacak sütunları alıyoruz
filtrelenmis_tablo = tablo[['appid', 'name', 'developer', 'positive', 'negative', 'price', 'ccu']]

# 5. SİSTEM MİMARİSİ: Bu oyunların radara ne zaman düştüğünü bilmek için bugünün tarihini atıyoruz
bugunun_tarihi = datetime.now().strftime("%Y-%m-%d")
filtrelenmis_tablo['radar_tarihi'] = bugunun_tarihi

# 6. Veriyi 'data' klasörümüzün altındaki Radar tablosuna kaydediyoruz
filtrelenmis_tablo.to_csv(radar_dosya_yolu, index=False)

oyun_sayisi = len(filtrelenmis_tablo)
print(f"Radar Tamamlandı! {oyun_sayisi} adet oyun başarılı bir şekilde data klasörüne kilitlendi.")