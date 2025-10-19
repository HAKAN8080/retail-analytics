import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Paket Optimizasyon", layout="wide", page_icon="📦")

# Başlık
st.title("📦 Paket Büyüklüğü Optimizasyon Aracı")
st.markdown("**English Home & EVE Kozmetik** için bedensiz ürünlerde optimum paket büyüklüğünü belirleyin")

# Sidebar parametreler
st.sidebar.header("⚙️ Parametreler")
sisme_katsayi = st.sidebar.slider(
    "Şişme Maliyet Katsayısı", 
    min_value=0.1, 
    max_value=5.0, 
    value=1.0, 
    step=0.1,
    help="Her fazla ürün için ceza puanı"
)

lojistik_katsayi = st.sidebar.slider(
    "Lojistik Tasarruf Katsayısı", 
    min_value=1.0, 
    max_value=10.0, 
    value=3.0, 
    step=0.5,
    help="Her mağaza için lojistik avantaj puanı"
)

analiz_periyodu = st.sidebar.selectbox(
    "Analiz Periyodu",
    ["Haftalık", "İki Haftalık"]
)

paket_boyutlari = st.sidebar.multiselect(
    "Test Edilecek Paket Boyutları",
    [2, 3, 4, 5, 6, 8, 10],
    default=[2, 3, 4, 5, 6]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Veri Formatı")
st.sidebar.info("""
CSV dosyanız şu kolonları içermelidir:
- **Tarih**: (örn: 2024-01-01)
- **Mağaza**: Mağaza adı
- **Ürün**: Ürün adı
- **Satış**: Satış miktarı
- **Stok**: Stok miktarı
""")

def ornek_veri_olustur():
    """Örnek veri oluştur"""
    tarihler = pd.date_range(start='2024-01-01', end='2024-10-25', freq='D')
    magazalar = ['Mağaza A', 'Mağaza B', 'Mağaza C', 'Mağaza D', 'Mağaza E']
    urunler = ['Ürün X', 'Ürün Y', 'Ürün Z']
    
    data = []
    for tarih in tarihler:
        for magaza in magazalar:
            for urun in urunler:
                satis = np.random.poisson(3)
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
    tarih_kolonu = [col for col in df.columns if col.lower() in ['tarih', 'date']][0]
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
            
            # Her mağaza için
            for magaza in urun_df['Mağaza'].unique():
                magaza_df = urun_df[urun_df['Mağaza'] == magaza]
                
                # Toplam satış ve periyod sayısı
                toplam_satis = magaza_df['Satış'].sum()
                gun_sayisi = (magaza_df[tarih_kolonu].max() - magaza_df[tarih_kolonu].min()).days + 1
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
                'dagitimlar': dagitimlar
            })
        
        # En iyi paketi bul
        en_iyi_paket = max(paket_sonuclari, key=lambda x: x['net_skor'])
        
        sonuclar.append({
            'urun': urun,
            'paket_sonuclari': paket_sonuclari,
            'en_iyi_paket': en_iyi_paket
        })
    
    return sonuclar

# Ana sayfa
col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader("📁 CSV Dosyası Yükleyin", type=['csv'])

with col2:
    if st.button("📥 Örnek Veri İndir", use_container_width=True):
        ornek_df = ornek_veri_olustur()
        csv = ornek_df.to_csv(index=False)
        st.download_button(
            label="💾 İndir",
            data=csv,
            file_name="ornek_veri.csv",
            mime="text/csv"
        )

# Veri yüklendiyse analiz yap
if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        
        st.success(f"✅ Veri yüklendi: {len(df)} satır, {len(df.columns)} kolon")
        
        with st.expander("🔍 Veri Önizleme"):
            st.dataframe(df.head(10))
        
        # Analiz yap
        if st.button("🚀 Analizi Başlat", type="primary", use_container_width=True):
            with st.spinner("Analiz yapılıyor..."):
                sonuclar = analiz_yap(
                    df, 
                    paket_boyutlari, 
                    sisme_katsayi, 
                    lojistik_katsayi, 
                    analiz_periyodu
                )
                
                st.session_state['analiz_sonuclari'] = sonuclar
        
        # Sonuçları göster
        if 'analiz_sonuclari' in st.session_state:
            sonuclar = st.session_state['analiz_sonuclari']
            
            st.markdown("---")
            st.header("📊 Analiz Sonuçları")
            
            # Özet tablo
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
            st.dataframe(ozet_df, use_container_width=True, hide_index=True)
            
            # Her ürün için detaylı analiz
            for idx, sonuc in enumerate(sonuclar):
                st.markdown("---")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.subheader(f"📦 {sonuc['urun']}")
                with col2:
                    st.metric(
                        "Önerilen Paket",
                        f"{sonuc['en_iyi_paket']['paket_boyutu']}'lü",
                        delta=f"Skor: {sonuc['en_iyi_paket']['net_skor']}"
                    )
                
                # Metrikler
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏪 Mağaza Sayısı", sonuc['en_iyi_paket']['magaza_sayisi'])
                with col2:
                    st.metric("🎯 Net Skor", sonuc['en_iyi_paket']['net_skor'])
                with col3:
                    st.metric("📈 Şişme", sonuc['en_iyi_paket']['toplam_sisme'])
                with col4:
                    st.metric("💰 Lojistik", sonuc['en_iyi_paket']['lojistik_tasarruf'])
                
                # Grafik
                paket_df = pd.DataFrame(sonuc['paket_sonuclari'])
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=paket_df['paket_boyutu'],
                    y=paket_df['net_skor'],
                    name='Net Skor',
                    marker_color='#10b981'
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
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Mağaza dağılımı
                st.markdown("**Mağaza Satış Dağılımı (Önerilen Paket)**")
                dag_cols = st.columns(5)
                for i, (aralik, sayi) in enumerate(sonuc['en_iyi_paket']['dagitimlar'].items()):
                    with dag_cols[i]:
                        st.metric(f"{aralik} adet", f"{sayi} mağaza")
                
                # Öneri kutusu
                st.info(f"""
                **💡 Öneri:** {sonuc['en_iyi_paket']['paket_boyutu']}'lü paket kullanarak 
                toplam **{sonuc['en_iyi_paket']['lojistik_tasarruf']}** puan lojistik tasarruf sağlarken, 
                sadece **{sonuc['en_iyi_paket']['toplam_sisme']}** birim şişme ile karşılaşırsınız.
                """)
    
    except Exception as e:
        st.error(f"❌ Hata oluştu: {str(e)}")
        st.info("Lütfen CSV dosyanızın doğru formatta olduğundan emin olun.")

else:
    # Boş ekran
    st.info("👆 Lütfen CSV dosyanızı yükleyin veya örnek veriyi indirerek test edin")
    
    st.markdown("### 📋 Nasıl Çalışır?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **1️⃣ Veri Yükleme**
        - CSV dosyanızı yükleyin
        - Format: Tarih, Mağaza, Ürün, Satış, Stok
        """)
    
    with col2:
        st.markdown("""
        **2️⃣ Parametre Ayarları**
        - Şişme maliyet katsayısı
        - Lojistik tasarruf katsayısı
        - Analiz periyodu seçimi
        """)
    
    with col3:
        st.markdown("""
        **3️⃣ Sonuçlar**
        - Optimum paket önerisi
        - Detaylı skor analizi
        - Görsel karşılaştırmalar
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>📦 Paket Optimizasyon Aracı | English Home & EVE Kozmetik</p>
</div>
""", unsafe_allow_html=True)
