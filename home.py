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
menu = st.sidebar.radio(
    "Bölümler",
    ["🌟 Hoş Geldiniz", "📖 Modül Detayları", "📊 Platform Özellikleri", "❓ SSS"]
)

# Hızlı Erişim Linkleri
st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Hızlı Erişim")

st.sidebar.page_link("pages/0_Veri_Yukleme.py", label="📤 Veri Yükleme", icon="📂")
st.sidebar.markdown("---")
st.sidebar.page_link("pages/1_Lost_Sales.py", label="📉 Lost Sales", icon="📊")
st.sidebar.page_link("pages/2_Sevkiyat.py", label="🚚 Sevkiyat Planlama", icon="📦")
st.sidebar.page_link("pages/3_Prepack Optimizasyonu.py", label="📦 Prepack Optimizasyon", icon="📦")
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
# 🌟 HOŞ GELDİNİZ
# ============================================
if menu == "🌟 Hoş Geldiniz":
    # Hoş geldiniz mesajı
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        ### 👋 Hoş Geldiniz!
        
        Bu platform, perakende operasyonlarınızı optimize etmek için güçlü analiz modülleri sunar:
        """)
        
        st.info("""
        **🎯 Platform Amacı:**
        
        Retail Analytics Platform, perakende sektöründeki operasyonel verimliliği artırmak ve 
        veri odaklı kararlar almayı kolaylaştırmak için geliştirilmiştir.
        
        **✨ Neler Yapabilirsiniz?**
        - 📉 Satış kayıplarını tespit edin ve analiz edin
        - 🚚 Sevkiyat operasyonlarını optimize edin
        - 💵 Alım sipariş süreçlerini yönetin
        - 📦 Prepack optimizasyonu yapın
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
        
        st.success("""
        ### 💡 İpuçları
        
        - Örnek CSV'leri indirin
        - Veri formatını kontrol edin
        - Filtreleri kullanın
        - Segment analizlerini inceleyin
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
            <hr>
            <small>✅ Trend analizi<br>✅ Fallback mekanizması<br>✅ Gün dağılımı</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;'>
            <h3>🚚</h3>
            <h4>Sevkiyat</h4>
            <p>Sevkiyat planlama ve optimizasyon</p>
            <hr>
            <small>✅ Segmentasyon<br>✅ Hedef matris<br>✅ Önceliklendirme</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;'>
            <h3>💵</h3>
            <h4>Alım Sipariş</h4>
            <p>Tedarikçi sipariş yönetimi</p>
            <hr>
            <small>✅ Cover analizi<br>✅ Karlılık filtresi<br>✅ Segment katsayıları</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;'>
            <h3>📦</h3>
            <h4>Prepack</h4>
            <p>Paket büyüklüğü optimizasyonu</p>
            <hr>
            <small>✅ Simülasyon<br>✅ Maliyet analizi<br>✅ Net skor</small>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# 📖 MODÜL DETAYLARI
# ============================================
elif menu == "📖 Modül Detayları":
    st.subheader("📖 Modül Detayları ve Kullanım Kılavuzu")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📉 Lost Sales", "🚚 Sevkiyat", "💵 Alım Sipariş", "📦 Prepack"])
    
    with tab1:
        st.markdown("""
        ## 📉 Lost Sales Analizi
        
        ### 🎯 Amaç
        Stoksuz geçen günlerde oluşan potansiyel satış kayıplarını tespit eder ve tahmin eder.
        
        ### 📊 Özellikler
        
        **1. Satış Kaybı (SK) Hesaplama**
        - Stoksuz günler için potansiyel satış tahmini
        - 5 katmanlı fallback mekanizması ile yüksek doğruluk
        
        **2. Trend Analizi**
        - 30 günlük satış trendi
        - Hafta içi/hafta sonu dağılımı
        - Mevsimsel faktörler
        
        **3. Çok Seviyeli Fallback**
        ```
        Level 1: Ürün-Mağaza bazında ortalama
        Level 2: Mağaza-Mal Grubu bazında ortalama
        Level 3: Ürün bazında ortalama
        Level 4: Mal Grubu bazında ortalama
        Level 5: Global ortalama
        ```
        
        ### 📋 Gerekli Veriler
        - `gunluk_satis.csv`: Günlük satış verileri
        - `urun_master.csv`: Ürün bilgileri
        - `magaza_master.csv`: Mağaza bilgileri (opsiyonel)
        
        ### 🔧 Parametreler
        - Analiz periyodu (örn: son 30 gün)
        - Minimum stok eşiği
        - Fallback seviyesi
        
        ### 📈 Çıktılar
        - Ürün bazında satış kaybı
        - Mağaza bazında satış kaybı
        - Mal grubu bazında satış kaybı
        - Toplam satış kaybı tutarı
        - Detaylı CSV raporları
        """)
    
    with tab2:
        st.markdown("""
        ## 🚚 Sevkiyat Yönetimi
        
        ### 🎯 Amaç
        Depodan mağazalara yapılacak sevkiyatları optimize eder ve önceliklendirir.
        
        ### 📊 Özellikler
        
        **1. Segmentasyon**
        - Ürün segmentasyonu (Cover bazlı)
        - Mağaza segmentasyonu (Cover bazlı)
        - Özelleştirilebilir aralıklar
        
        **2. Hedef Matris**
        - Şişme oranı matrisi
        - Genleştirme oranı matrisi
        - Min oran matrisi
        - Initial matris (yeni ürünler)
        
        **3. Sıralama ve Önceliklendirme**
        - RPT (Replenishment) önceliği
        - Initial (Yeni ürün) önceliği
        - Min (Minimum stok) önceliği
        
        **4. Sevkiyat Hesaplama**
        ```
        İhtiyaç = (Forward Cover × Satış × Genleştirme) - (Stok + Yol)
        Sevkiyat = MIN(İhtiyaç, Depo Stok, Max Sevkiyat)
        ```
        
        ### 📋 Gerekli Veriler
        - `urun_master.csv`: Ürün bilgileri
        - `magaza_master.csv`: Mağaza bilgileri
        - `depo_stok.csv`: Depo stok durumu
        - `anlik_stok_satis.csv`: Mağaza stok ve satış
        - `kpi.csv`: KPI hedefleri
        - `yasak.csv`: Yasak kombinasyonlar (opsiyonel)
        - `haftalik_trend.csv`: Trend verileri (opsiyonel)
        
        ### 🔧 Parametreler
        - Segmentasyon aralıkları
        - Hedef matris değerleri
        - Sıralama öncelikleri
        - Forward cover hedefi
        
        ### 📈 Çıktılar
        - Mağaza-Ürün bazında sevkiyat miktarları
        - Öncelik sıralaması
        - Stok yokluğu kayıpları
        - Segment analizleri
        - Detaylı CSV raporları
        """)
    
    with tab3:
        st.markdown("""
        ## 💵 Alım Sipariş (PO)
        
        ### 🎯 Amaç
        Tedarikçiden alınması gereken ürün miktarlarını belirler.
        
        ### 📊 Özellikler
        
        **1. Cover Analizi**
        - Düşük cover tespiti
        - Segment bazında analiz
        - Trend bazlı tahmin
        
        **2. Karlılık Filtresi**
        - Brüt kar marjı kontrolü
        - Negatif marj uyarıları
        - Karlılık bazlı önceliklendirme
        
        **3. Genişletme Katsayıları**
        - Cover segment bazında katsayılar
        - Satış trendine göre ayarlama
        - Özelleştirilebilir matris
        
        **4. Alım Sipariş Hesaplama**
        ```
        Talep = Satış × Genleştirme × (Forward Cover + 2)
        Alım = Talep - (Stok + Yol + Depo) + Min Sevkiyat
        ```
        
        ### 📋 Gerekli Veriler
        - `anlik_stok_satis.csv`: Güncel durum
        - `depo_stok.csv`: Depo stok
        - `kpi.csv`: KPI hedefleri
        - Sevkiyat hesaplama sonuçları (opsiyonel)
        
        ### 🔧 Parametreler
        - Cover eşiği (örn: < 12)
        - Brüt kar marjı eşiği (örn: > %10)
        - Cover segment katsayıları
        - Forward cover hedefi
        
        ### 📈 Çıktılar
        - Ürün bazında alım miktarları
        - Cover segment analizi
        - Karlılık analizi
        - Top ürünler listesi
        - Detaylı CSV raporları
        """)
    
    with tab4:
        st.markdown("""
        ## 📦 Prepack Optimizasyonu
        
        ### 🎯 Amaç
        Optimum paket büyüklüğünü belirleyerek lojistik maliyetleri azaltır ve stok şişmesini kontrol eder.
        
        ### 📊 Özellikler
        
        **1. Paket Büyüklüğü Simülasyonu**
        - 2'li, 3'lü, 4'lü, 5'li, 6'lı paket seçenekleri
        - Her senaryo için detaylı hesaplama
        - Karşılaştırmalı analiz
        
        **2. Maliyet Optimizasyonu**
        ```
        Lojistik Tasarruf = Sevkiyat Sayısı Azalması × Birim Maliyet
        Şişme Maliyeti = Fazla Stok × Birim Maliyet × %
        Net Skor = Lojistik Tasarruf - Şişme Maliyeti
        ```
        
        **3. Mağaza Segmentasyonu**
        - Düşük satış (<5 adet/hafta)
        - Orta satış (5-15 adet/hafta)
        - Yüksek satış (>15 adet/hafta)
        
        **4. Periyodik Analiz**
        - Haftalık bazda
        - İki haftalık bazda
        - Özelleştirilebilir periyot
        
        ### 📋 Gerekli Veriler
        - Ürün-Mağaza satış verileri
        - Mevcut sevkiyat bilgileri
        - Lojistik maliyet parametreleri
        
        ### 🔧 Parametreler
        - Paket büyüklükleri
        - Lojistik birim maliyet
        - Şişme maliyet oranı
        - Mağaza segment eşikleri
        
        ### 📈 Çıktılar
        - Optimum paket büyüklüğü
        - Segment bazında öneriler
        - Net skor karşılaştırması
        - Maliyet tasarruf analizi
        - Görsel grafikler
        """)

# ============================================
# 📊 PLATFORM ÖZELLİKLERİ
# ============================================
elif menu == "📊 Platform Özellikleri":
    st.subheader("📊 Platform Özellikleri ve Teknik Detaylar")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔧 Teknik Özellikler
        
        **Altyapı:**
        - 🐍 Python 3.8+
        - 🎈 Streamlit Framework
        - 🐼 Pandas & NumPy
        - 📊 Plotly (opsiyonel)
        
        **Veri İşleme:**
        - ✅ UTF-8 encoding desteği
        - ✅ Büyük veri setleri (1M+ satır)
        - ✅ Otomatik veri temizleme
        - ✅ Hata yönetimi
        
        **Performans:**
        - ⚡ Hızlı hesaplama
        - 💾 Session state yönetimi
        - 🔄 Lazy loading
        - 📦 Optimize edilmiş algoritmalar
        """)
        
        st.markdown("""
        ### 🔐 Güvenlik
        
        - 🔒 Session bazlı çalışma
        - 🚫 Veri sunucuda saklanmaz
        - 🔄 Otomatik temizleme
        - ✅ GDPR uyumlu
        
        ### 📱 Kullanılabilirlik
        
        - 💻 Responsive tasarım
        - 🎨 Modern arayüz
        - 🖱️ Kolay navigasyon
        - 📊 İnteraktif grafikler
        """)
    
    with col2:
        st.markdown("""
        ### 📈 Analiz Yetenekleri
        
        **İstatistiksel Analizler:**
        - 📊 Tanımlayıcı istatistikler
        - 📈 Trend analizi
        - 🔄 Korelasyon analizi
        - 🎯 Tahmin modelleri
        
        **Segmentasyon:**
        - 🎯 Otomatik segmentasyon
        - 📐 Özelleştirilebilir aralıklar
        - 🔢 Çok boyutlu gruplama
        - 📊 Segment performans analizi
        
        **Raporlama:**
        - 📄 CSV export
        - 📊 Detaylı tablolar
        - 📈 Görsel raporlar
        - 💾 Batch işlemler
        """)
        
        st.markdown("""
        ### 🎓 Öğrenme Kaynakları
        
        - 📚 Kullanım kılavuzları
        - 🎥 Video öğreticiler (yakında)
        - 💬 Topluluk forumu (yakında)
        - 📧 Destek ekibi
        
        ### 🔄 Güncellemeler
        
        - 🆕 Düzenli özellik eklemeleri
        - 🐛 Bug düzeltmeleri
        - ⚡ Performans iyileştirmeleri
        - 📖 Dokümantasyon güncellemeleri
        """)
    
    st.markdown("---")
    
    # Platform istatistikleri
    st.subheader("📊 Platform İstatistikleri")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Toplam Modül",
            value="4",
            delta="Lost Sales + Sevkiyat + PO + Prepack"
        )
    
    with col2:
        st.metric(
            label="Analiz Özellikleri",
            value="25+",
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
# ❓ SSS (Sık Sorulan Sorular)
# ============================================
elif menu == "❓ SSS":
    st.subheader("❓ Sık Sorulan Sorular")
    
    # Genel Sorular
    with st.expander("🔍 CSV dosyalarımı nasıl hazırlamalıyım?", expanded=True):
        st.markdown("""
        **CSV Hazırlama Kuralları:**
        
        1. **Encoding**: UTF-8 formatında kaydedin
        2. **Ayırıcı**: Virgül (,) kullanın
        3. **Tarih Formatı**: YYYY-MM-DD (örn: 2024-01-15)
        4. **Kod Kolonları**: Boşluk içermemeli
        5. **Sayısal Değerler**: Nokta (.) ondalık ayırıcı olarak
        6. **Başlıklar**: İlk satırda kolon adları
        
        **Örnek:**
        ```csv
        urun_kod,magaza_kod,tarih,satis,stok
        U001,M001,2024-01-15,50,100
        U002,M001,2024-01-15,30,80
        ```
        """)
    
    with st.expander("💾 Verilerim güvende mi?"):
        st.markdown("""
        **Veri Güvenliği:**
        
        - ✅ Veriler sadece tarayıcınızda (session) tutulur
        - ✅ Sunucuda kalıcı olarak saklanmaz
        - ✅ Tarayıcı kapatıldığında otomatik silinir
        - ✅ GDPR ve veri koruma yasalarına uyumlu
        - ✅ Üçüncü taraflarla paylaşılmaz
        
        **Önemli:** Hassas verilerinizi yüklemeden önce anonymize etmenizi öneririz.
        """)
    
    with st.expander("⚡ Neden yavaş çalışıyor?"):
        st.markdown("""
        **Performans İpuçları:**
        
        1. **Dosya Boyutu**: 100MB üzeri dosyalar yavaş olabilir
        2. **Satır Sayısı**: 1M+ satır için daha fazla süre
        3. **Tarayıcı**: Chrome veya Edge önerilir
        4. **Bellek**: En az 4GB RAM önerilir
        5. **İnternet**: Stabil bağlantı gerekli
        
        **Çözümler:**
        - Dosyaları küçük parçalara bölün
        - Gereksiz kolonları çıkarın
        - Tarih aralığını daraltın
        - Tarayıcı önbelleğini temizleyin
        """)
    
    with st.expander("📊 Hangi analizleri yapabilirim?"):
        st.markdown("""
        **Mevcut Analizler:**
        
        **Lost Sales:**
        - Satış kaybı tahmini
        - Trend analizi
        - Fallback mekanizması
        - Gün dağılımı
        
        **Sevkiyat:**
        - Stok dağıtım optimizasyonu
        - Segmentasyon
        - Önceliklendirme
        - Hedef matris
        
        **Alım Sipariş:**
        - Cover analizi
        - Karlılık filtresi
        - Tedarikçi sipariş
        
        **Prepack:**
        - Paket optimizasyonu
        - Maliyet analizi
        - Net skor hesaplama
        """)
    
    with st.expander("🔄 Sonuçları nasıl kullanabilirim?"):
        st.markdown("""
        **Sonuç Kullanımı:**
        
        1. **CSV İndirme**: Her modülde CSV export mevcut
        2. **Excel'e Aktarma**: CSV'yi Excel'de açabilirsiniz
        3. **BI Araçları**: Power BI, Tableau ile entegre
        4. **ERP Sistemi**: Manuel veya API ile aktarım
        5. **Raporlama**: Hazır grafikler ve tablolar
        
        **Dosya Formatı:**
        - UTF-8 encoding
        - Başlıklar mevcut
        - Doğrudan kullanıma hazır
        """)
    
    with st.expander("❌ Hata mesajı aldım, ne yapmalıyım?"):
        st.markdown("""
        **Yaygın Hatalar ve Çözümleri:**
        
        **1. "Dosya yüklenemedi"**
        - CSV formatını kontrol edin
        - UTF-8 encoding kullanın
        - Dosya boyutunu azaltın
        
        **2. "Kolon bulunamadı"**
        - Gerekli kolonları kontrol edin
        - Kolon adlarını örnek CSV'ye göre düzenleyin
        - Boşlukları kaldırın
        
        **3. "Hesaplama hatası"**
        - Tarih formatını kontrol edin (YYYY-MM-DD)
        - Sayısal değerlerde karakter olmamalı
        - Negatif değerleri kontrol edin
        
        **4. "Bellek hatası"**
        - Dosya boyutunu küçültün
        - Tarayıcıyı yeniden başlatın
        - Gereksiz sekmeleri kapatın
        """)
    
    with st.expander("📞 Destek almak için ne yapmalıyım?"):
        st.markdown("""
        **Destek Kanalları:**
        
        1. **Dokümantasyon**: Bu SSS ve modül detayları
        2. **Örnek CSV'ler**: Her modülde mevcut
        3. **E-posta Desteği**: support@retailanalytics.com
        4. **Topluluk Forumu**: (yakında)
        
        **Destek Talebi Gönderirken:**
        - Hangi modülü kullandığınız
        - Hata mesajının ekran görüntüsü
        - Kullandığınız tarayıcı ve sürümü
        - Dosya formatı ve boyutu
        """)
    
    with st.expander("🆕 Yeni özellikler ne zaman gelecek?"):
        st.markdown("""
        **Roadmap (Yakında):**
        
        **Q2 2024:**
        - 📊 Excel export
        - 🗺️ Coğrafi haritalar
        - 📈 İleri analitik
        
        **Q3 2024:**
        - 🤖 Makine öğrenmesi tahminleri
        - 🔄 Otomatik güncellemeler
        - 📧 E-posta raporları
        
        **Q4 2024:**
        - 🌐 API entegrasyonu
        - 📱 Mobil uygulama
        - 🎨 Özelleştirilebilir dashboard
        
        **Öneri Gönder:**
        - features@retailanalytics.com
        """)

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
