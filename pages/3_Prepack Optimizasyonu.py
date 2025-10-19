import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np

# ============================================
# SAYFA YAPILANDIRMASI
# ============================================
st.set_page_config(
    page_title="Prepack Optimizasyonu",
    page_icon="📦",
    layout="wide"
)

# ============================================
# BAŞLIK
# ============================================
st.title("📦 Prepack Optimizasyonu")
st.markdown("**English Home & EVE Kozmetik** için bedensiz ürünlerde optimum paket büyüklüğünü belirleyin")
st.markdown("---")

# ============================================
# SIDEBAR PARAMETRELER
# ============================================
st.sidebar.header("⚙️ Parametreler")

sisme_katsayi = st.sidebar.slider(
    "Şişme Maliyet Katsayısı", 
    min_value=0.1, 
    max_value=5.0, 
    value=1.0, 
    step=0.1,
    help="Her fazla ürün için ceza puanı (Stok maliyeti, raf alanı kaybı, eskime riski)"
)

lojistik_katsayi = st.sidebar.slider(
    "Lojistik Tasarruf Katsayısı", 
    min_value=1.0, 
    max_value=10.0, 
    value=3.0, 
    step=0.5,
    help="Her mağaza için lojistik avantaj puanı (Sevkiyat, paketleme, depo tasarrufu)"
)

analiz_periyodu = st.sidebar.selectbox(
    "Analiz Periyodu",
    ["Haftalık", "İki Haftalık"],
    help="Satış ortalaması hesaplama periyodu"
)

paket_boyutlari = st.sidebar.multiselect(
    "Test Edilecek Paket Boyutları",
    [2, 3, 4, 5, 6, 8, 10],
    default=[2, 3, 4, 5, 6],
    help="Simülasyon yapılacak paket büyüklükleri"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Veri Formatı")
st.sidebar.info("""
**CSV Kolon Yapısı:**
- `Tarih`: 2024-01-01 formatında
- `magaza_kod`: Mağaza kodu
- `urun_kod`: Ürün kodu
- `satis`: Satış miktarı (adet)
- `stok`: Stok miktarı (adet)

**Örnek:**
```
Tarih,magaza_kod,urun_kod,satis,stok
2024-01-01,MGZ001,URN001,5,20
2024-01-01,MGZ002,URN001,2,15
```
""")

# ============================================
# YARDIMCI FONKSİYONLAR
# ============================================

def csv_oku(file):
    """CSV dosyasını farklı encoding ve delimiter'larla okumayı dene"""
    encodings = ['utf-8-sig', 'utf-8', 'latin1', 'cp1252', 'iso-8859-9', 'windows-1254']
    delimiters = [',', ';', '\t', '|']
    
    for encoding in encodings:
        for delimiter in delimiters:
            try:
                file.seek(0)  # Dosya pointerını başa al
                df = pd.read_csv(file, encoding=encoding, delimiter=delimiter)
                
                # Başarılı okuma kontrolü
                if len(df.columns) > 1 and len(df) > 0:
                    # Kolon isimlerini temizle
                    df.columns = df.columns.str.strip()
                    st.success(f"✅ Dosya başarıyla okundu! (Encoding: {encoding}, Delimiter: '{delimiter}')")
                    return df
            except Exception:
                continue
    
    return None

def kolon_normalize(df):
    """Kolon isimlerini normalize et ve eşleştir"""
    import unicodedata
    
    def temizle(text):
        """Türkçe karakterleri ve özel karakterleri temizle"""
        if not isinstance(text, str):
            return text
        # Unicode normalizasyonu
        text = unicodedata.normalize('NFKD', text)
        # ASCII'ye çevir
        text = text.encode('ascii', 'ignore').decode('ascii')
        # Küçük harfe çevir ve boşlukları temizle
        text = text.lower().strip()
        return text
    
    kolon_map = {}
    for col in df.columns:
        col_clean = temizle(col)
        
        # Eşleştirme - yeni kolon isimleri
        if any(x in col_clean for x in ['tarih', 'date']):
            kolon_map[col] = 'Tarih'
        elif any(x in col_clean for x in ['magaza', 'store', 'magazakod', 'magazakodu']):
            kolon_map[col] = 'magaza_kod'
        elif any(x in col_clean for x in ['urun', 'product', 'urunkod', 'urunkodu']):
            kolon_map[col] = 'urun_kod'
        elif any(x in col_clean for x in ['satis', 'sales']):
            kolon_map[col] = 'satis'
        elif any(x in col_clean for x in ['stok', 'stock']):
            kolon_map[col] = 'stok'
    
    return kolon_map

def ornek_veri_olustur():
    """Örnek test verisi oluştur"""
    tarihler = pd.date_range(start='2024-01-01', end='2024-10-25', freq='D')
    magazalar = ['MGZ001', 'MGZ002', 'MGZ003', 'MGZ004', 'MGZ005']
    urunler = ['URN001', 'URN002', 'URN003']
    
    data = []
    for tarih in tarihler:
        for magaza in magazalar:
            for urun in urunler:
                # Farklı satış paternleri
                if magaza in ['MGZ001', 'MGZ002']:
                    satis = np.random.poisson(5)  # Yüksek satış
                elif magaza == 'MGZ003':
                    satis = np.random.poisson(2)  # Orta satış
                else:
                    satis = np.random.poisson(1)  # Düşük satış
                
                stok = np.random.randint(10, 50)
                data.append({
                    'Tarih': tarih.strftime('%Y-%m-%d'),
                    'magaza_kod': magaza,
                    'urun_kod': urun,
                    'satis': satis,
                    'stok': stok
                })
    
    return pd.DataFrame(data)

def analiz_yap(df, paket_boyutlari, sisme_kat, lojistik_kat, periyod):
    """Ana analiz fonksiyonu"""
    
    # Tarih kolonunu datetime'a çevir
    if 'Tarih' in df.columns:
        df['Tarih'] = pd.to_datetime(df['Tarih'])
    
    # Kolon isimlerini normalize et
    kolon_map = kolon_normalize(df)
    df = df.rename(columns=kolon_map)
    
    # Gerekli kolonları kontrol et
    gerekli_kolonlar = ['Tarih', 'magaza_kod', 'urun_kod', 'satis', 'stok']
    eksik_kolonlar = [k for k in gerekli_kolonlar if k not in df.columns]
    
    if eksik_kolonlar:
        st.error(f"❌ Eksik kolonlar: {', '.join(eksik_kolonlar)}")
        st.info(f"Mevcut kolonlar: {', '.join(df.columns.tolist())}")
        return []
    
    # Periyod günü hesapla
    periyod_gun = 7 if periyod == "Haftalık" else 14
    
    sonuclar = []
    
    # Her ürün için analiz
    for urun in df['urun_kod'].unique():
        urun_df = df[df['urun_kod'] == urun]
        
        paket_sonuclari = []
        
        for paket_boyutu in paket_boyutlari:
            toplam_sisme = 0
            magaza_sayisi = 0
            dagitimlar = {'0': 0, '1-2': 0, '3-4': 0, '5-6': 0, '7+': 0}
            magaza_detaylari = []
            
            # Her mağaza için
            for magaza in urun_df['magaza_kod'].unique():
                magaza_df = urun_df[urun_df['magaza_kod'] == magaza]
                
                # Toplam satış ve periyod sayısı
                toplam_satis = magaza_df['satis'].sum()
                
                if 'Tarih' in magaza_df.columns:
                    gun_sayisi = (magaza_df['Tarih'].max() - magaza_df['Tarih'].min()).days + 1
                else:
                    gun_sayisi = len(magaza_df)
                
                periyod_sayisi = max(1, gun_sayisi / periyod_gun)
                
                # Ortalama satış
                ortalama_satis = toplam_satis / periyod_sayisi
                
                # Dağılıma ekle
                if ortalama_satis == 0:
                    dagitimlar['0'] += 1
                elif ortalama_satis <= 2:
                    dagitimlar['1-2'] += 1
                elif ortalama_satis <= 4:
                    dagitimlar['3-4'] += 1
                elif ortalama_satis <= 6:
                    dagitimlar['5-6'] += 1
                else:
                    dagitimlar['7+'] += 1
                
                # Şişme hesapla
                ihtiyac = np.ceil(ortalama_satis)
                gonderilecek = np.ceil(ihtiyac / paket_boyutu) * paket_boyutu
                sisme = max(0, gonderilecek - ihtiyac)
                
                toplam_sisme += sisme
                magaza_sayisi += 1
                
                magaza_detaylari.append({
                    'magaza_kod': magaza,
                    'ortalama_satis': round(ortalama_satis, 2),
                    'ihtiyac': int(ihtiyac),
                    'gonderilecek': int(gonderilecek),
                    'sisme': int(sisme)
                })
            
            # Skorları hesapla
            lojistik_tasarruf = magaza_sayisi * lojistik_kat
            sisme_maliyeti = toplam_sisme * sisme_kat
            net_skor = lojistik_tasarruf - sisme_maliyeti
            
            paket_sonuclari.append({
                'paket_boyutu': paket_boyutu,
                'toplam_sisme': round(toplam_sisme, 1),
                'lojistik_tasarruf': round(lojistik_tasarruf, 1),
                'sisme_maliyeti': round(sisme_maliyeti, 1),
                'net_skor': round(net_skor, 1),
                'magaza_sayisi': magaza_sayisi,
                'dagitimlar': dagitimlar,
                'magaza_detaylari': magaza_detaylari
            })
        
        # En iyi paketi bul
        if paket_sonuclari:
            en_iyi_paket = max(paket_sonuclari, key=lambda x: x['net_skor'])
            
            sonuclar.append({
                'urun': urun,
                'paket_sonuclari': paket_sonuclari,
                'en_iyi_paket': en_iyi_paket
            })
    
    return sonuclar

# ============================================
# ANA UYGULAMA
# ============================================

# Dosya yükleme bölümü
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    uploaded_file = st.file_uploader(
        "📁 CSV Dosyası Yükleyin",
        type=['csv'],
        help="Tarih, magaza_kod, urun_kod, satis, stok kolonlarını içeren CSV dosyası"
    )

with col2:
    if st.button("📥 Örnek Veri İndir", use_container_width=True):
        ornek_df = ornek_veri_olustur()
        csv = ornek_df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button(
            label="💾 CSV İndir",
            data=csv,
            file_name="prepack_ornek_veri.csv",
            mime="text/csv",
            use_container_width=True
        )

with col3:
    if uploaded_file and st.button("🚀 Analizi Başlat", type="primary", use_container_width=True):
        with st.spinner("⏳ Analiz yapılıyor..."):
            try:
                df = csv_oku(uploaded_file)
                
                if df is None:
                    st.error("❌ CSV dosyası okunamadı!")
                elif paket_boyutlari is None or len(paket_boyutlari) == 0:
                    st.error("❌ Lütfen en az bir paket boyutu seçin!")
                else:
                    sonuclar = analiz_yap(
                        df, 
                        paket_boyutlari, 
                        sisme_katsayi, 
                        lojistik_katsayi, 
                        analiz_periyodu
                    )
                    st.session_state['analiz_sonuclari'] = sonuclar
                    st.session_state['analiz_df'] = df
                    st.success("✅ Analiz tamamlandı!")
            except Exception as e:
                st.error(f"❌ Analiz hatası: {str(e)}")
                st.exception(e)  # Detaylı hata bilgisi

# Veri önizleme
if uploaded_file is not None:
    try:
        df = csv_oku(uploaded_file)
        
        if df is None:
            st.error("❌ CSV dosyası okunamadı. Lütfen dosya formatını kontrol edin.")
            st.info("""
            **Olası çözümler:**
            - Dosyanın UTF-8 encoding ile kaydedildiğinden emin olun
            - Excel'den CSV olarak kaydederken 'CSV UTF-8 (Virgülle ayrılmış)' seçeneğini kullanın
            - Kolon ayırıcısının virgül (,) olduğundan emin olun
            - Dosyanın boş olmadığını kontrol edin
            """)
        else:
            # Kolon kontrolü
            kolon_map = kolon_normalize(df)
            df_normalized = df.rename(columns=kolon_map)
            
            gerekli_kolonlar = ['Tarih', 'magaza_kod', 'urun_kod', 'satis', 'stok']
            eksik_kolonlar = [k for k in gerekli_kolonlar if k not in df_normalized.columns]
            
            if eksik_kolonlar:
                st.warning(f"⚠️ Eksik kolonlar: {', '.join(eksik_kolonlar)}")
                st.info(f"""
                **Mevcut kolonlar:** {', '.join(df.columns.tolist())}
                
                **Beklenen kolonlar:** Tarih, magaza_kod, urun_kod, satis, stok
                
                Kolon eşleştirme otomatik yapılacak, ancak tam eşleşme bulunamadı.
                """)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Toplam Satır", f"{len(df):,}")
            with col2:
                if 'magaza_kod' in df_normalized.columns:
                    st.metric("🏪 Mağaza Sayısı", len(df_normalized['magaza_kod'].unique()))
                else:
                    st.metric("🏪 Mağaza Sayısı", "N/A")
            with col3:
                if 'urun_kod' in df_normalized.columns:
                    st.metric("📦 Ürün Sayısı", len(df_normalized['urun_kod'].unique()))
                else:
                    st.metric("📦 Ürün Sayısı", "N/A")
            with col4:
                if 'Tarih' in df_normalized.columns:
                    st.metric("📅 Veri Aralığı", f"{len(df_normalized['Tarih'].unique())} gün")
                else:
                    st.metric("📅 Veri Aralığı", "N/A")
            
            with st.expander("🔍 Veri Önizleme (İlk 10 Satır)"):
                st.dataframe(df.head(10), use_container_width=True)
    
    except Exception as e:
        st.error(f"❌ Beklenmeyen hata: {str(e)}")
        st.info("Lütfen destek için hata mesajını kaydedin.")

# ============================================
# SONUÇLARI GÖSTER
# ============================================
if 'analiz_sonuclari' in st.session_state:
    sonuclar = st.session_state['analiz_sonuclari']
    
    st.markdown("---")
    st.header("📊 Analiz Sonuçları")
    
    # Özet tablo
    st.subheader("🎯 Öneriler Özeti")
    ozet_data = []
    for sonuc in sonuclar:
        ozet_data.append({
            'Ürün Kodu': sonuc['urun'],
            'Önerilen Paket': f"{sonuc['en_iyi_paket']['paket_boyutu']}'lü",
            'Net Skor': sonuc['en_iyi_paket']['net_skor'],
            'Toplam Şişme': sonuc['en_iyi_paket']['toplam_sisme'],
            'Lojistik Tasarruf': sonuc['en_iyi_paket']['lojistik_tasarruf'],
            'Mağaza Sayısı': sonuc['en_iyi_paket']['magaza_sayisi']
        })
    
    ozet_df = pd.DataFrame(ozet_data)
    
    # Styling (matplotlib gerekmeyen basit versiyon)
    try:
        st.dataframe(
            ozet_df.style.background_gradient(subset=['Net Skor'], cmap='RdYlGn'),
            use_container_width=True,
            hide_index=True
        )
    except ImportError:
        # Matplotlib yoksa basit tablo göster
        st.dataframe(
            ozet_df,
            use_container_width=True,
            hide_index=True
        )
    
    # CSV indirme
    csv = ozet_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 Özet Tabloyu İndir (CSV)",
        data=csv,
        file_name=f"prepack_ozet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    
    # Her ürün için detaylı analiz
    for idx, sonuc in enumerate(sonuclar):
        st.markdown(f"## 📦 {sonuc['urun']}")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            st.metric(
                "🎯 Önerilen Paket",
                f"{sonuc['en_iyi_paket']['paket_boyutu']}'lü",
                delta=f"Skor: {sonuc['en_iyi_paket']['net_skor']}"
            )
        
        # Metrikler
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏪 Mağaza Sayısı", sonuc['en_iyi_paket']['magaza_sayisi'])
        with col2:
            st.metric("💰 Lojistik Tasarruf", f"+{sonuc['en_iyi_paket']['lojistik_tasarruf']}")
        with col3:
            st.metric("📈 Şişme Miktarı", f"{sonuc['en_iyi_paket']['toplam_sisme']}")
        with col4:
            st.metric("⚠️ Şişme Maliyeti", f"-{sonuc['en_iyi_paket']['sisme_maliyeti']}")
        
        # Grafik
        paket_df = pd.DataFrame(sonuc['paket_sonuclari'])
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=paket_df['paket_boyutu'],
            y=paket_df['net_skor'],
            name='Net Skor',
            marker_color='#10b981',
            text=paket_df['net_skor'],
            textposition='outside'
        ))
        fig.add_trace(go.Bar(
            x=paket_df['paket_boyutu'],
            y=paket_df['lojistik_tasarruf'],
            name='Lojistik Tasarruf',
            marker_color='#8b5cf6'
        ))
        fig.add_trace(go.Bar(
            x=paket_df['paket_boyutu'],
            y=paket_df['sisme_maliyeti'],
            name='Şişme Maliyeti',
            marker_color='#f59e0b'
        ))
        
        fig.update_layout(
            title="Paket Büyüklüğü Karşılaştırması",
            xaxis_title="Paket Büyüklüğü",
            yaxis_title="Puan",
            barmode='group',
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Mağaza dağılımı
        st.markdown("**📊 Mağaza Satış Dağılımı (Önerilen Paket)**")
        dag_cols = st.columns(5)
        for i, (aralik, sayi) in enumerate(sonuc['en_iyi_paket']['dagitimlar'].items()):
            with dag_cols[i]:
                st.metric(f"{aralik} adet/periyod", f"{sayi} mağaza")
        
        # Mağaza detayları
        with st.expander(f"🔍 {sonuc['urun']} - Mağaza Detayları"):
            detay_df = pd.DataFrame(sonuc['en_iyi_paket']['magaza_detaylari'])
            try:
                st.dataframe(
                    detay_df.style.background_gradient(subset=['sisme'], cmap='Reds'),
                    use_container_width=True,
                    hide_index=True
                )
            except ImportError:
                st.dataframe(
                    detay_df,
                    use_container_width=True,
                    hide_index=True
                )
        
        # Öneri kutusu
        st.info(f"""
        **💡 Öneri:** {sonuc['en_iyi_paket']['paket_boyutu']}'lü paket kullanarak:
        - ✅ Toplam **{sonuc['en_iyi_paket']['lojistik_tasarruf']}** puan lojistik tasarruf
        - ⚠️ Sadece **{sonuc['en_iyi_paket']['toplam_sisme']}** birim şişme
        - 🎯 Net Skor: **{sonuc['en_iyi_paket']['net_skor']}** puan
        """)
        
        if idx < len(sonuclar) - 1:
            st.markdown("---")

else:
    # Boş ekran - kullanım talimatları
    st.info("👆 Lütfen CSV dosyanızı yükleyin ve 'Analizi Başlat' butonuna tıklayın")
    
    st.markdown("---")
    st.markdown("## 📋 Nasıl Çalışır?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 1️⃣ Veri Hazırlama
        
        **Gerekli Kolonlar:**
        - `Tarih`: Satış tarihi (YYYY-MM-DD)
        - `magaza_kod`: Mağaza kodu
        - `urun_kod`: Ürün kodu
        - `satis`: Satış adedi (sayısal)
        - `stok`: Stok adedi (sayısal)
        
        **Öneriler:**
        - 2024 yılı başından güncel tarihe kadar veri
        - En az 1 ay, ideal 3+ ay veri
        - Kolon isimleri tam olmalı
        - Türkçe karakter kullanmayın
        """)
    
    with col2:
        st.markdown("""
        ### 2️⃣ Parametre Ayarları
        
        **Şişme Katsayısı:**
        - Fazla stok maliyeti
        - Raf alanı kaybı
        - Eskime riski
        
        **Lojistik Katsayısı:**
        - Sevkiyat tasarrufu
        - Paketleme kolaylığı
        - Depo verimliliği
        """)
    
    with col3:
        st.markdown("""
        ### 3️⃣ Sonuç Analizi
        
        **Net Skor:**
        ```
        Lojistik Tasarruf
        - Şişme Maliyeti
        = Net Skor
        ```
        
        **En yüksek skora sahip paket önerilir**
        
        **Mağaza dağılımını inceleyin**
        """)
    
    st.markdown("---")
    st.markdown("## 🎯 Örnek Senaryo")
    
    st.markdown("""
    **Durum:** Bir ürün için 3 farklı paket boyutu değerlendiriliyor:
    
    | Paket | Lojistik | Şişme | Net Skor |
    |-------|----------|-------|----------|
    | 2'li  | +15      | -8    | **+7**   |
    | 3'lü  | +15      | -12   | **+3**   |
    | 4'lü  | +15      | -18   | **-3**   |
    
    **Sonuç:** 2'li paket önerilir çünkü en yüksek net skora sahip!
    """)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>📦 Prepack Optimizasyonu | Retail Analytics Platform v2.0</p>
    <p>English Home & EVE Kozmetik için özel geliştirilmiştir</p>
</div>
""", unsafe_allow_html=True)
