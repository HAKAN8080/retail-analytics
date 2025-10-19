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
    min_value=1.0, 
    max_value=10.0, 
    value=1.0, 
    step=0.5,
    help="Şişme maliyeti çarpanı: (Paket Boyutu - Ortalama Satış) × Bu Katsayı"
)

lojistik_katsayi = st.sidebar.slider(
    "Lojistik Tasarruf Katsayısı", 
    min_value=1.0, 
    max_value=10.0, 
    value=3.0, 
    step=0.5,
    help="Lojistik tasarruf çarpanı: (1 / Paket Boyutu) × Bu Katsayı"
)

analiz_periyodu = st.sidebar.selectbox(
    "Analiz Periyodu",
    ["Tüm Veri (2 Haftalık Ort.)", "İki Haftalık", "Haftalık"],
    help="Satış ortalaması hesaplama periyodu"
)

paket_boyutlari = list(range(3, 21))
st.sidebar.info(f"📦 Test Edilecek Paket Boyutları: 3'lü - 20'li (Toplam {len(paket_boyutlari)} paket)")

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

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧮 Formüller")
st.sidebar.success("""
**Lojistik Tasarruf:**
```
(1 / Paket Boyutu) × 
Lojistik Katsayı × 
Mağaza Sayısı
```

**Şişme Maliyeti:**
```
Toplam Şişme × 
Şişme Katsayı
```

**Net Skor:**
```
Lojistik Tasarruf - 
Şişme Maliyeti
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
    if periyod == "Tüm Veri (2 Haftalık Ort.)":
        periyod_gun = 14  # 2 haftalık ortalama için
        tum_veri_modu = True
    elif periyod == "İki Haftalık":
        periyod_gun = 14
        tum_veri_modu = False
    else:  # Haftalık
        periyod_gun = 7
        tum_veri_modu = False
    
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
                
                # Periyod sayısı hesaplama
                if tum_veri_modu:
                    # Tüm veriyi al, 2 haftalık ortalamaya böl
                    periyod_sayisi = gun_sayisi / 14
                else:
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
                
                # Şişme hesapla - YENİ FORMÜL
                ihtiyac = ortalama_satis
                gonderilecek = np.ceil(ihtiyac / paket_boyutu) * paket_boyutu
                sisme = max(0, gonderilecek - ihtiyac)
                
                toplam_sisme += sisme
                magaza_sayisi += 1
                
                magaza_detaylari.append({
                    'magaza_kod': magaza,
                    'ortalama_satis': round(ortalama_satis, 2),
                    'ihtiyac': round(ihtiyac, 2),
                    'gonderilecek': int(gonderilecek),
                    'sisme': round(sisme, 2)
                })
            
            # Skorları hesapla - YENİ FORMÜLLER
            # Lojistik Tasarruf = (1 / paket_boyutu) * lojistik_katsayi
            lojistik_tasarruf = (1 / paket_boyutu) * lojistik_kat * magaza_sayisi
            
            # Şişme Maliyeti = Σ(paket_boyutu - ortalama_satis) * sisme_katsayi
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
                'magaza_detaylari': magaza_detaylari,
                'lojistik_kat': lojistik_kat,  # Katsayıları kaydet
                'sisme_kat': sisme_kat
            })
        
        # En iyi paketi bul - 0'a en yakın net skor
        if paket_sonuclari:
            en_iyi_paket = min(paket_sonuclari, key=lambda x: abs(x['net_skor']))
            
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
    
    # Özet tablo - TÜM PAKET BOYUTLARI
    st.subheader("🎯 Öneriler Özeti - Tüm Paket Boyutları")
    
    for sonuc in sonuclar:
        st.markdown(f"### 📦 {sonuc['urun']}")
        
        # Her paket boyutu için sonuçları göster
        ozet_data = []
        for paket_sonuc in sonuc['paket_sonuclari']:
            en_iyi = "⭐" if paket_sonuc['paket_boyutu'] == sonuc['en_iyi_paket']['paket_boyutu'] else ""
            ozet_data.append({
                '': en_iyi,
                'Paket Boyutu': f"{paket_sonuc['paket_boyutu']}'lü",
                'Net Skor': round(paket_sonuc['net_skor'], 2),
                'Lojistik Tasarruf': round(paket_sonuc['lojistik_tasarruf'], 2),
                'Şişme Miktarı': round(paket_sonuc['toplam_sisme'], 2),
                'Şişme Maliyeti': round(paket_sonuc['sisme_maliyeti'], 2),
                'Mağaza Sayısı': paket_sonuc['magaza_sayisi']
            })
        
        ozet_df = pd.DataFrame(ozet_data)
        
        # En iyi paketi vurgula
        def highlight_best(row):
            if row[''] == '⭐':
                return ['background-color: #d4edda'] * len(row)
            return [''] * len(row)
        
        try:
            st.dataframe(
                ozet_df.style.apply(highlight_best, axis=1),
                use_container_width=True,
                hide_index=True
            )
        except:
            st.dataframe(ozet_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
    
    # CSV indirme - TÜM SONUÇLAR
    st.subheader("💾 Rapor İndirme")
    
    # Tüm sonuçları birleştir
    tum_sonuclar = []
    for sonuc in sonuclar:
        for paket_sonuc in sonuc['paket_sonuclari']:
            en_iyi = "✓" if paket_sonuc['paket_boyutu'] == sonuc['en_iyi_paket']['paket_boyutu'] else ""
            tum_sonuclar.append({
                'Ürün Kodu': sonuc['urun'],
                'En İyi': en_iyi,
                'Paket Boyutu': paket_sonuc['paket_boyutu'],
                'Net Skor': round(paket_sonuc['net_skor'], 2),
                'Lojistik Tasarruf': round(paket_sonuc['lojistik_tasarruf'], 2),
                'Şişme Miktarı': round(paket_sonuc['toplam_sisme'], 2),
                'Şişme Maliyeti': round(paket_sonuc['sisme_maliyeti'], 2),
                'Mağaza Sayısı': paket_sonuc['magaza_sayisi'],
                '0 adet': paket_sonuc['dagitimlar']['0'],
                '1-2 adet': paket_sonuc['dagitimlar']['1-2'],
                '3-4 adet': paket_sonuc['dagitimlar']['3-4'],
                '5-6 adet': paket_sonuc['dagitimlar']['5-6'],
                '7+ adet': paket_sonuc['dagitimlar']['7+']
            })
    
    rapor_df = pd.DataFrame(tum_sonuclar)
    csv = rapor_df.to_csv(index=False, encoding='utf-8-sig')
    
    st.download_button(
        label="📥 Tüm Sonuçları İndir (CSV)",
        data=csv,
        file_name=f"prepack_detayli_rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
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
        
        # Mağaza dağılımı - LİSTE FORMAT
        st.markdown("**📊 Mağaza Satış Dağılımı (Önerilen Paket)**")
        
        dag_data = []
        for aralik, sayi in sonuc['en_iyi_paket']['dagitimlar'].items():
            dag_data.append({
                'Satış Aralığı (adet/periyod)': aralik,
                'Mağaza Sayısı': sayi,
                'Oran (%)': round(sayi / sonuc['en_iyi_paket']['magaza_sayisi'] * 100, 1) if sonuc['en_iyi_paket']['magaza_sayisi'] > 0 else 0
            })
        
        dag_df = pd.DataFrame(dag_data)
        st.dataframe(dag_df, use_container_width=True, hide_index=True)
        
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
        
        # Öneri kutusu - GÜNCEL FORMÜLLER
        en_iyi = sonuc['en_iyi_paket']
        st.info(f"""
        **💡 Öneri:** {en_iyi['paket_boyutu']}'lü paket kullanarak:
        - ✅ Lojistik Tasarruf: **{en_iyi['lojistik_tasarruf']:.2f}** puan
          - Formül: (1/{en_iyi['paket_boyutu']}) × {en_iyi['lojistik_kat']} × {en_iyi['magaza_sayisi']} mağaza
        - ⚠️ Şişme Maliyeti: **{en_iyi['sisme_maliyeti']:.2f}** puan
          - Toplam Şişme: {en_iyi['toplam_sisme']:.2f} birim × {en_iyi['sisme_kat']}
        - 🎯 Net Skor: **{en_iyi['net_skor']:.2f}** puan
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
        
        **Şişme Katsayısı (1-10):**
        - Fazla stok maliyeti
        - Raf alanı kaybı
        - Eskime riski
        - Formül: Σ(Şişme) × Katsayı
        
        **Lojistik Katsayısı (1-10):**
        - Sevkiyat tasarrufu
        - Paketleme kolaylığı
        - Depo verimliliği
        - Formül: (1/Paket) × Katsayı × Mağaza Sayısı
        
        **Analiz Periyodu:**
        - Tüm Veri: Tüm veriye bak, 2 hafta ort.
        - İki Haftalık: 14 günlük ortalama
        - Haftalık: 7 günlük ortalama
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
        
        **Tüm paket boyutlarını görebilirsiniz**
        
        **18 farklı paket testi (3-20)**
        """)
    
    st.markdown("---")
    st.markdown("## 🎯 Örnek Senaryo")
    
    st.markdown("""
    **Durum:** Bir ürün için farklı paket boyutları değerlendiriliyor (10 mağaza):
    
    | Paket | Lojistik Formül | Lojistik | Şişme | Net Skor |
    |-------|-----------------|----------|-------|----------|
    | 3'lü  | (1/3)×3×10      | +10.0    | -8.5  | **+1.5** |
    | 4'lü  | (1/4)×3×10      | +7.5     | -12.0 | **-4.5** |
    | 5'li  | (1/5)×3×10      | +6.0     | -15.5 | **-9.5** |
    
    **Sonuç:** 3'lü paket önerilir çünkü en yüksek net skora sahip!
    
    **Not:** Küçük paketler daha fazla lojistik tasarruf sağlar ama şişme de daha az olur.
    """)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    <p>📦 Prepack Optimizasyonu | Retail Analytics Platform v3.0</p>
    <p>English Home & EVE Kozmetik için özel geliştirilmiştir</p>
    <p style='font-size: 0.8em; margin-top: 10px;'>
        ✨ Yeni: 3-20 paket aralığı | Gelişmiş formüller | Detaylı raporlama
    </p>
</div>
""", unsafe_allow_html=True)
