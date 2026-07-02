import requests
import pandas as pd
from datetime import datetime

print("RADAR ÇALIŞTIRILIYOR: Steam'deki güncel oyunlar taranıyor...")

# SteamSpy'dan son 2 haftanın popüler 100 oyununu (şimdilik test için) çekiyoruz
url = "https://steamspy.com/api.php?request=top100in2weeks"
cevap = requests.get(url)
ham_veri = cevap.json()

# Gelen JSON verisini Pandas tablosuna dönüştürüyoruz
tablo = pd.DataFrame(list(ham_veri.values()))

# Sadece işimize yarayacak sütunları alıyoruz (Gereksiz kalabalıktan kurtulalım)
filtrelenmis_tablo = tablo[['appid', 'name', 'developer', 'positive', 'negative', 'price', 'ccu']]

# SİSTEM MİMARİSİ: Bu oyunların radara ne zaman düştüğünü bilmek için bugünün tarihini atıyoruz
bugunun_tarihi = datetime.now().strftime("%Y-%m-%d")
filtrelenmis_tablo['radar_tarihi'] = bugunun_tarihi

# Veriyi 'data' klasörümüzün altındaki Radar tablosuna CSV olarak kaydediyoruz
# 'index=False' diyerek satır numaralarının dosyayı kirletmesini engelliyoruz
filtrelenmis_tablo.to_csv("../data/radar_tablosu.csv", index=False)

# Kullanıcıya bilgi ver
oyun_sayisi = len(filtrelenmis_tablo)
print(f"Radar Tamamlandı! {oyun_sayisi} adet oyun başarılı bir şekilde 'data/radar_tablosu.csv' dosyasına kilitlendi.")