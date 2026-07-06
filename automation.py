import subprocess
import time
import schedule
import sys
from datetime import datetime

def boru_hattini_calistir():
    zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{zaman}] SİSTEM: Veri Hattı Tetiklendi")
    
    python_cmd = "py" 
    max_yeniden_baslatma = 2
    deneme_sayaci = 0
    
    while deneme_sayaci <= max_yeniden_baslatma:
        try:
            if deneme_sayaci > 0:
                print(f"\n SİSTEM YENİDEN BAŞLATILIYOR. (Kalan Hak: {max_yeniden_baslatma - deneme_sayaci + 1})")
                time.sleep(5) #İnternetin toparlanması için 5 saniye bekle
                
            print("Adım 1/3: Pazar Arandı")
            subprocess.run([python_cmd, "src/1_arama.py"], check=True)
            
            print("Adım 2/3: Ülke bulundu")
            subprocess.run([python_cmd, "src/2_ulke_bul.py"], check=True)
            
            print("Adım 3/3: Veri Çekildi")
            subprocess.run([python_cmd, "src/3_veri_yapilandirma"
            ".py"], check=True)
            
            zaman_bitis = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{zaman_bitis}]  GÜNCELLEME TAMAMLANDI. Sistem uyku moduna geçiyor.")
            
            
            return 
            
        except subprocess.CalledProcessError as e:
            deneme_sayaci += 1
            print(f"\n KRİTİK HATA: Adım başarısız oldu (Hata Kodu: {e.returncode})")
            
            if deneme_sayaci > max_yeniden_baslatma:
                print("DİKKAT: Sistem 2 kez baştan başlatıldı ancak ağ/API sorunu aşılamadı!")
                
                sys.exit() # sorun yaşandığı için sistem kapatılıyor ve güvenli şekilde bozulmamış oluyor

# Zamanlayıcı Her 12 Saatte Bir
schedule.every(12).hours.do(boru_hattini_calistir)

print("Otomasyon Aktif Edildi")
print("İlk tur başlatılıyor.\n")

# İlk tetikleme
boru_hattini_calistir()

# Sonsuz döngü 
while True:
    schedule.run_pending()
    time.sleep(60)