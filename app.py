"""
🚀 Retail Analytics Sistemi
Ana Sayfa
"""
import streamlit as st

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Retail Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Basit ve temiz
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
        color: #1f77b4;
    }
    .info-box {
        background-color: #f0f8ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Ana başlık
st.markdown('<div class="main-header">📊 Retail Analytics Sistemi</div>', unsafe_allow_html=True)
st.markdown("---")

# Giriş
st.markdown("""
## 👋 Hoşgeldiniz!

Bu sistem, retail operasyonlarınızı optimize etmek için geliştirilmiş modüler bir çözümdür.
""")

# Modül kartları
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 📤 Veri Yönetimi
    
    **Veri Yükleme Modülü**
    - CSV dosya yükleme
    - Veri doğrulama
    - Session yönetimi
    - Format kontrolleri
    
    👉 *Tüm modüller için veri girişi buradan yapılır*
    """)
    
    if st.button("📤 Veri Yükleme'ye Git", use_container_width=True):
        st.switch_page("pages/0_Veri_Yukleme.py")

with col2:
    st.markdown("""
    ### 💵 Alım Sipariş (PO)
    
    **Purchase Order Modülü**
    - Cover bazlı hesaplama
    - Kar marjı filtreleme
    - Koli yuvarlaması
    - Depo bazlı çıktılar
    
    👉 *Tedarikçi sipariş optimizasyonu*
    """)
    
    if st.button("💵 Alım Sipariş'e Git", use_container_width=True):
        st.switch_page("pages/4_PO.py")

st.markdown("---")

# Diğer modüller
st.markdown("### 📋 Diğer Modüller")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container():
        st.markdown("#### 📉 Lost Sales")
        st.caption("Kayıp satış analizi")
        if st.button("🔍 Lost Sales", use_container_width=True, key="lost"):
            st.switch_page("pages/1_Lost_Sales.py")

with col2:
    with st.container():
        st.markdown("#### 🚚 Sevkiyat")
        st.caption("Mağaza sevkiyat optimizasyonu")
        if st.button("📦 Sevkiyat", use_container_width=True, key="sevk"):
            st.switch_page("pages/2_Sevkiyat.py")

with col3:
    with st.container():
        st.markdown("#### 📦 Prepack")
        st.caption("Prepack optimizasyonu")
        if st.button("🎁 Prepack", use_container_width=True, key="prepack"):
            st.switch_page("pages/3_Prepack_Optimization.py")

st.markdown("---")

# Genel Bilgilendirme
st.markdown("## 🎯 Sistem Özellikleri")

col1, col2 = st.columns(2)

with col1:
    st.info("""
    **💡 Modüler Yapı**
    
    Her modül bağımsız çalışır:
    - Ayrı veri gereksinimleri
    - Özel hesaplama mantıkları
    - Farklı çıktı formatları
    - Session state yönetimi
    """)

with col2:
    st.success("""
    **✅ Başlangıç Adımları**
    
    1. **Veri Yükleme** sayfasına gidin
    2. Kullanmak istediğiniz modül için gerekli CSV'leri yükleyin
    3. İlgili modüle geçin ve analizleri çalıştırın
    4. Sonuçları indirin ve kullanın
    """)

# PO Modülü İçin Özel Bilgi
st.markdown("---")
st.markdown("## 💵 Alım Sipariş (PO) Modülü - Detaylar")

with st.expander("📊 PO Modülü Nasıl Çalışır?", expanded=False):
    st.markdown("""
    ### Hesaplama Mantığı
    
    **1. Cover Hesaplama:**
    ```
    Cover = (Toplam Stoklar) / (Mağaza Satış Hızı)
    Toplam Stoklar = Mağaza Stok + Yolda + Depo Stok
    ```
    
    **2. Filtreler (Varsayılan):**
    - Cover < 15 hafta
    - Brüt Kar Marjı > -20%
    
    **3. Sipariş Formülü:**
    ```
    Brüt İhtiyaç = (Satış × Genişletme × (FC + 2)) - Mevcut Stoklar + Karşılanamayan Min
    Net İhtiyaç = Brüt İhtiyaç - Açık Sipariş
    ```
    
    **4. Özellikler:**
    - ✅ Koli bazında yuvarlama
    - ✅ İthal ürün faktörü (FC × 1.2)
    - ✅ Pasif ürün kontrolü
    - ✅ Yasak ürün filtreleme
    - ✅ Detaylı KPI hedefleri (marka+MG bazlı)
    
    **5. Çıktılar:**
    - 📊 Segment bazlı raporlar
    - 🏪 Depo bazlı sipariş listeleri
    - 💰 Karlılık analizi
    - 👥 Tedarikçi bazlı özet
    """)

with st.expander("📋 Gerekli CSV Dosyaları", expanded=False):
    st.markdown("""
    ### Zorunlu Dosyalar:
    
    1. **Anlık Stok/Satış**
       - Sütunlar: `urun_kod`, `stok`, `yol`, `satis`, `ciro`, `smm`
       - Açıklama: Mağaza bazlı güncel stok ve satış verileri
    
    2. **Depo Stok**
       - Sütunlar: `urun_kod`, `depo_kod`, `stok`
       - Açıklama: Depo bazlı stok seviyeleri
    
    3. **KPI**
       - Sütunlar: `forward_cover`, `servis_seviyesi`, vs.
       - Açıklama: Genel hedef ve parametreler
    
    ### Opsiyonel (Önerilen):
    
    4. **Ürün Master**
       - Sütunlar: `urun_kod`, `satici_kod`, `mg`, `marka_kod`, `durum`, `ithal`, `koli_ici`
       - Açıklama: Ürün detay bilgileri
    
    5. **PO Yasak**
       - Sütunlar: `urun_kodu`, `yasak_durum`, `acik_siparis`
       - Açıklama: Yasak ürünler ve açık siparişler
    
    6. **PO Detay KPI**
       - Sütunlar: `marka_kod`, `mg`, `cover_hedef`, `bkar_hedef`
       - Açıklama: Marka+MG bazında özel hedefler
    """)

# Footer
st.markdown("---")
st.caption("🚀 Retail Analytics v2.0 | Made with ❤️ using Streamlit")
