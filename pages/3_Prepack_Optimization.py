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
# SIDEBAR ÖZELLEŞTIRME (BÜYÜK HARF & BOLD)
# ============================================
st.markdown("""
<style>
    /* Sidebar sayfa linklerini büyük harf ve bold yap */
    [data-testid="stSidebarNav"] li a {
        text-transform: uppercase !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }
    
    /* Aktif sayfayı daha belirgin yap */
    [data-testid="stSidebarNav"] li a[aria-current="page"] {
        background-color: rgba(151, 166, 195, 0.15) !important;
        color: #ff4b4b !important;
    }
    
    /* Hover efekti */
    [data-testid="stSidebarNav"] li a:hover {
        background-color: rgba(151, 166, 195, 0.1) !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR MENÜ
# ============================================
st.sidebar.title("🏠 Ana Sayfa Menüsü")

# Hızlı Erişim Linkleri
st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Hızlı Erişim")

st.sidebar.page_link("pages/0_Veri_Yukleme.py", label="📤 Veri Yükleme", icon="📂")
st.sidebar.markdown("---")
st.sidebar.page_link("pages/1_Lost_Sales.py", label="📉 Lost Sales", icon="📊")
st.sidebar.page_link("pages/2_Sevkiyat.py", label="🚚 Sevkiyat Planlama", icon="📦")
st.sidebar.page_link("pages/3_Prepack_Optimization.py", label="📦 Prepack Optimizasyon", icon="📦")
st.sidebar.page_link("pages/4_PO.py", label="💵 Alım Sipariş (PO)", icon="🛒")

st.sidebar.markdown("---")
st.sidebar.info("""
**💡 İpucu:**
Modüllere sol menüden veya yukarıdaki hızlı erişim butonlarından ulaşabilirsiniz.
""")

# ============================================
# ANA SAYFA
# ============================================
st.title("📊 Retail Analytics Platform")
st.markdown("---")

# ============================================
# HOŞ GELDİNİZ
# ============================================
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### 👋 Hoş Geldiniz!
    
    Bu platform, perakende operasyonlarınızı optimize etmek için güçlü analiz modülleri sunar:
    """)
    
    st.success("""
    **🚀 Hızlı Başlangıç:**
    
    1. Sol menüden bir modül seçin (Lost Sales, Sevkiyat, PO, Prepack)
    2. CSV dosyalarınızı yükleyin
    3. Parametreleri ayarlayın
    4. Analiz sonuçlarını görüntüleyin
    5. Raporları CSV formatında indirin
    """)

with col2:
    st.info("""
    ### 📚 Kullanım Kılavuzu
    
    **1️⃣ Veri Yükleme**
    - UTF-8 formatında CSV
    - Tarih: YYYY-MM-DD
    - Kod kolonları: Boşluksuz
    
    **2️⃣ Analiz**
    - Parametreleri ayarlayın
    - Hesapla butonuna tıklayın
    - Sonuçları inceleyin
    
    **3️⃣ Raporlama**
    - CSV indirme
    - Detaylı tablolar
    - Görselleştirmeler
    """)
    
    st.warning("""
    ### ⚠️ Önemli Notlar
    
    - Veriler session bazlı
    - Sunucuda saklanmaz
    - Tarayıcı kapatıldığında silinir
    - Büyük dosyalarda yavaşlama olabilir
    """)

st.markdown("---")

# Modül kartları
st.subheader("📦 Mevcut Modüller")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;'>
        <h3>📉</h3>
        <h4>Lost Sales</h4>
        <p>Satış kaybı analizi ve tahmin</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;'>
        <h3>🚚</h3>
        <h4>Sevkiyat</h4>
        <p>Sevkiyat planlama ve optimizasyon</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;'>
        <h3>💵</h3>
        <h4>Alım Sipariş</h4>
        <p>Tedarikçi sipariş yönetimi</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;'>
        <h3>📦</h3>
        <h4>Prepack</h4>
        <p>Paket büyüklüğü optimizasyonu</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Retail Analytics Platform v2.0</p>
    <p>Perakende operasyonlarınızı optimize edin 🚀</p>
    <p><small>Son Güncelleme: Ocak 2024</small></p>
</div>
""", unsafe_allow_html=True)
