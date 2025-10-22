import streamlit as st
import pandas as pd

# ============================================
# SAYFA YAPILANDIRMASI
# ============================================
st.set_page_config(
    page_title="Retail Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# ANA SAYFA
# ============================================
st.title("📊 Retail Analytics Platform")
st.markdown("---")

# Hoş geldiniz mesajı
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### 👋 Hoş Geldiniz!
    
    Bu platform, perakende operasyonlarınızı optimize etmek için üç güçlü analiz modülü sunar:
    """)
    
    # Modül 1: Lost Sales
    st.markdown("""
    #### 📉 Lost Sales Analizi
    
    **Özellikler:**
    - 📊 **Satış Kaybı (SK) Hesaplama**: Stoksuz günler için potansiyel satış tahmini
    - 📈 **Trend Analizi**: 30 günlük satış trendi ile tahmin
    - 🔄 **Çok Seviyeli Fallback**: 5 katmanlı tahmin hiyerarşisi
    - 📅 **Gün Dağılım Analizi**: Hafta içi/hafta sonu satış dağılımı
    - 📋 **Detaylı Raporlama**: Ürün, mağaza ve mal grubu bazında analizler
    - 💾 **Veri Export**: CSV formatında sonuç indirme
    
    **Kullanım Alanları:**
    - Stok politikası optimizasyonu
    - Talep tahmini iyileştirme
    - Operasyonel kayıp analizi
    """)
    
    # Modül 2: Sevkiyat
    st.markdown("""
    #### 🚚 Sevkiyat Yönetimi
    
    **Özellikler:**
    - 📦 **Klasman Parametreleri**: Ürün bazlı sevkiyat kuralları
    - 🎯 **Segmentasyon Analizi**: Mağaza ve ürün segmentasyonu
    - 📊 **Stok/Satış Analizi**: 4 haftalık ortalama hesaplama
    - 🎚️ **Hedef Matris**: Segment bazlı şişme oranları
    - 🚀 **Sevkiyat Hesaplama**: Otomatik miktar belirleme
    - 📈 **Bütçe Takibi**: Alım ve sevkiyat bütçe kontrolü
    
    **Kullanım Alanları:**
    - Sevkiyat planlaması
    - Stok dağıtım optimizasyonu
    - Bütçe yönetimi
    """)
    
    # Modül 3: Prepack Optimizasyonu
    st.markdown("""
    #### 📦 Prepack Optimizasyonu
    
    **Özellikler:**
    - 📊 **Paket Büyüklüğü Analizi**: 2'li, 3'lü, 4'lü, 5'li, 6'lı paket simülasyonu
    - 💰 **Maliyet Optimizasyonu**: Şişme vs lojistik tasarruf dengesi
    - 📈 **Mağaza Segmentasyonu**: Satış hacmine göre mağaza grupları
    - 🎯 **Net Skor Hesaplama**: Optimum paket boyutu belirleme
    - 📅 **Periyodik Analiz**: Haftalık veya iki haftalık bazda
    - 📊 **Görsel Karşılaştırma**: İnteraktif grafiklerle karar desteği
    
    **Kullanım Alanları:**
    - Paket büyüklüğü optimizasyonu
    - Lojistik maliyet azaltma
    - Stok şişme kontrolü
    """)

with col2:
    st.info("""
    ### 🚀 Hızlı Başlangıç
    
    1️⃣ Sol menüden bir modül seçin
    
    2️⃣ CSV dosyalarınızı yükleyin
    
    3️⃣ Parametreleri ayarlayın
    
    4️⃣ Analiz sonuçlarını görün
    
    5️⃣ Raporları indirin
    """)
    
    st.success("""
    ### 💡 İpuçları
    
    - Tüm CSV dosyaları UTF-8 formatında olmalı
    - Tarih formatı: YYYY-MM-DD
    - Kod kolonları boşluk içermemeli
    - Negatif değerler otomatik 0'a çevrilir
    """)
    
    st.warning("""
    ### ⚠️ Önemli
    
    Veri güvenliği için:
    - Session bazlı çalışır
    - Veriler sunucuda saklanmaz
    - Tarayıcı kapatıldığında silinir
    """)

# ============================================
# İSTATİSTİKLER
# ============================================
st.markdown("---")
st.subheader("📊 Platform İstatistikleri")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Toplam Modül",
        value="3",
        delta="Lost Sales + Sevkiyat + Prepack"
    )

with col2:
    st.metric(
        label="Analiz Özellikleri",
        value="20+",
        delta="Detaylı analizler"
    )

with col3:
    st.metric(
        label="Desteklenen Format",
        value="CSV",
        delta="UTF-8 encoded"
    )

with col4:
    st.metric(
        label="Export Seçenekleri",
        value="CSV",
        delta="Hazır raporlar"
    )

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Retail Analytics Platform v2.0</p>
    <p>Perakende operasyonlarınızı optimize edin 🚀</p>
</div>
""", unsafe_allow_html=True)
