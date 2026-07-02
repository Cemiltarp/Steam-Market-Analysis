import streamlit as st
import pandas as pd
import os

# 1. WEB SİTESİ AYARLARI
st.set_page_config(page_title="Steam Pazar Analizi", page_icon="🎮", layout="wide")

st.title("🎮 Steam Sermaye Piyasası Analizi")
st.markdown("Bu canlı panel, Steam'deki elit oyunların stüdyolarını ve ülkelerin pazar paylarını analiz eder.")

# 2. VİTRİN VERİSİNİ BUL VE OKU (Yine kurşun geçirmez dosya yolu)
ana_klasor = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
vitrin_dosya_yolu = os.path.join(ana_klasor, "data", "ana_vitrin_tablosu.csv")

try:
    df = pd.read_csv(vitrin_dosya_yolu)
    st.success(f"Sistem Aktif! Gümrükten geçen {len(df)} adet oyun analiz ediliyor.")
    
    # Ekrana yan yana iki kolon açıyoruz
    sol_kolon, sag_kolon = st.columns(2)
    
    with sol_kolon:
        st.subheader("🌍 Ülkelere Göre Elit Oyun Sayısı")
        # Hangi ülkeden kaç oyun var hesapla ve çubuk grafik çiz
        ulke_dagilimi = df['ulke'].value_counts()
        st.bar_chart(ulke_dagilimi)
        
    with sag_kolon:
        st.subheader("💰 Stüdyolara Göre Fiyat Analizi (Ortalama)")
        # Sektördeki stüdyolar ortalama kaç dolara oyun satıyor?
        # Sadece bilinen stüdyoları al, fiyat ortalamasını bul ve çiz
        fiyat_analizi = df.groupby('developer')['price'].mean().sort_values(ascending=False).head(10)
        st.bar_chart(fiyat_analizi)

    st.divider() # Araya şık bir çizgi atıyoruz

    # Ham Veriyi de aşağıya havalı bir tablo olarak koyuyoruz
    st.subheader("📦 Pazarın Aktörleri (Gümrükten Geçenler)")
    st.dataframe(df)

except FileNotFoundError:
    st.error("HATA: Vitrin tablosu bulunamadı. Önce Radar ve Gümrük kodlarını çalıştırmalısın!")