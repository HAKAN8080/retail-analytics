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
- `Mağaza`: Mağaza adı/kodu
- `Ürün`: Ürün adı/kodu
- `Satış`: Satış miktarı (adet)
- `Stok`: Stok miktarı (adet)

**Örnek:**
```
Tarih,Mağaza,Ürün,Satış,Stok
2024-01-01,MGZ001,URN001,5,20
2024-01-01,MGZ002,URN001,2,15
```
""")

# ============================================
# YARDIMCI FONKSİYONLAR
# ============================================

def ornek_veri_olustur():
    """Örnek test verisi oluştur"""
    tarihler = pd.date_range(start='2024-01-01', end='2024-10-25', freq='D')
    magazalar = ['Mağaza A', 'Mağaza B', 'Mağaza C', 'Mağaza D', 'Mağaza E']
    urunler = ['Ürün X', 'Ürün Y', 'Ürün Z']
    
    data = []
    for tarih in tarihler:
        for magaza in magazalar:
            for urun in urunler:
                # Farklı satış paternleri
                if 'A' in magaza:
                    satis = np.random.poisson(5)  # Yüksek satış
                elif 'B' in magaza:
                    satis = np.random.poisson(2)  # Orta satış
                else:
                    satis = np.random.poisson(1)  # Düşük satış
                
                stok = np.random.randint(10, 50)
                data.append({
                    'Tarih': tarih.strftime('%Y-%m-%d'),
                    'Mağaza': magaza,
                    'Ürün': urun,
                    'Satış': satis,
                    'Stok': stok
                })
    
    return pd.DataFrame(data)

def analiz_yap(df, paket_boyutlari, sisme_kat, lojistik_kat, periyod):
    """Ana analiz fonksiyonu"""
    
    # Tarih kolonunu datetime'a çevir
    tarih_kolonu = None
    for col in df.columns:
        if col.lower() in ['tarih', 'date', 'tarİh']:
            tarih_kolonu = col
            break
    
    if tarih_kolonu:
        df[tarih_kolonu] = pd.to_datetime(df[tarih_kolonu])
    
    # Kolon isimlerini normalize et
    kolon_map = {}
    for col in df.columns:
        col_lower = col.lower()
        if 'ürün' in col_lower or 'urun' in col_lower or 'product' in col_lower:
            kolon_map[col] = 'Ürün'
        elif 'mağaza' in col_lower or 'magaza' in col_lower or 'store' in col_lower:
            kolon_map[col] = 'Mağaza'
        elif 'satış' in col_lower or 'satis' in col_lower or 'sales' in col_lower:
            kolon_map[col] = 'Satış'
        elif 'stok' in col_lower or 'stock' in col_lower:
            kolon_map[col] = 'Stok'
        elif 'tarih' in col_lower or 'date' in col_lower:
            kolon_map[col] = 'Tarih'
    
    df = df.rename(columns=kolon_map)
    
    # Periyod günü hesapla
    periyod_gun = 7 if periyod == "Haftalık" else 14
    
    sonuclar = []
    
    # Her ürün için analiz
    for urun in df['Ürün'].unique():
        urun_df = df[df['Ürün'] == urun]
        
        paket_sonuclari = []
        
        for paket_boyutu in paket_boyutlari:
            toplam_sisme = 0
            magaza_sayisi = 0
            dagitimlar = {'0': 0, '1-2': 0, '3-4': 0, '5-6': 0, '7+': 0}
            magaza_detaylari = []
            
            # Her mağaza için
            for magaza in urun_df['Mağaza'].unique():
                magaza_df = urun_df[urun_df['Mağaza'] == magaza]
                
                # Toplam satış ve periyod sayısı
                toplam_satis = magaza_df['Satış'].sum()
                
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
                    'magaza': magaza,
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
        help="Tarih, Mağaza, Ürün, Satış, Stok kolonlarını içeren CSV dosyası"
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
                df = pd.read_csv(uploaded_file)
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
                st.error(f"❌ Hata oluştu: {str(e)}")

# Veri önizleme
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Toplam Satır", f"{len(df):,}")
        with col2:
            st.metric("🏪 Mağaza Sayısı", len(df['Mağaza'].unique()) if 'Mağaza' in df.columns else 0)
        with col3:
            st.metric("📦 Ürün Sayısı", len(df['Ürün'].unique()) if 'Ürün' in df.columns else 0)
        with col4:
            st.metric("📅 Veri Aralığı", f"{len(df['Tarih'].unique())} gün" if 'Tarih' in df.columns else "N/A")
        
        with st.expander("🔍 Veri Önizleme (İlk 10 Satır)"):
            st.dataframe(df.head(10), use_container_width=True)
    
    except Exception as e:
        st.error(f"❌ Veri okuma hatası: {str(e)}")

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
            'Ürün': sonuc['urun'],
            'Önerilen Paket': f"{sonuc['en_iyi_paket']['paket_boyutu']}'lü",
            'Net Skor': sonuc['en_iyi_paket']['net_skor'],
            'Toplam Şişme': sonuc['en_iyi_paket']['toplam_sisme'],
            'Lojistik Tasarruf': sonuc['en_iyi_paket']['lojistik_tasarruf'],
            'Mağaza Sayısı': sonuc['en_iyi_paket']['magaza_sayisi']
        })
    
    ozet_df = pd.DataFrame(ozet_data)
    st.dataframe(
        ozet_df.style.background_gradient(subset=['Net Skor'], cmap='RdYlGn'),
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
            st.dataframe(
                detay_df.style.background_gradient(subset=['sisme'], cmap='Reds'),
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
        - `Tarih`: Satış tarihi
        - `Mağaza`: Mağaza kodu/adı
        - `Ürün`: Ürün kodu/adı
        - `Satış`: Satış adedi
        - `Stok`: Stok adedi
        
        **Öneriler:**
        - 2024 yılı başından güncel tarihe kadar veri
        - En az 1 ay, ideal 3+ ay veri
        - Tutarlı format
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
