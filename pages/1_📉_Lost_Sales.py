import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# ============================================
# SAYFA YAPILANDIRMASI
# ============================================
st.set_page_config(page_title="Lost Sales v4.0", page_icon="📉", layout="wide")

# ============================================
# SESSION STATE
# ============================================
for key in ['anlik_stok_satis', 'depo_stok', 'urun_master', 'magaza_master', 'haftalik_trend', 'lost_sales_sonuc', 'trend_gun_sayisi', 'gun_dagilim']:
    if key not in st.session_state:
        st.session_state[key] = None

if st.session_state.trend_gun_sayisi is None:
    st.session_state.trend_gun_sayisi = 30

if st.session_state.gun_dagilim is None:
    st.session_state.gun_dagilim = {
        'Pazartesi': 12.0, 'Salı': 12.0, 'Çarşamba': 12.0, 'Perşembe': 12.0,
        'Cuma': 12.0, 'Cumartesi': 20.0, 'Pazar': 20.0
    }

# ============================================
# YARDIMCI FONKSİYONLAR
# ============================================
def normalize_code(col_series):
    s = col_series.astype(str).str.strip()
    s = s.str.replace(r"\.0$", "", regex=True)
    s = s.replace({'nan': None, 'None': None})
    return s

def validate_data_quality(df, df_name):
    issues, warnings = [], []
    null_counts = df.isnull().sum()
    null_cols = null_counts[null_counts > 0]
    if len(null_cols) > 0:
        warnings.append(f"⚠️ {df_name}: Boş değerler var")
        for col, count in null_cols.items():
            warnings.append(f"  - {col}: {count:,} boş ({count/len(df)*100:.1f}%)")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        negative_count = (df[col] < 0).sum()
        if negative_count > 0:
            issues.append(f"❌ {df_name}: '{col}' kolonunda {negative_count:,} negatif → 0'a çevrilecek")
    
    if df_name == "Anlık Stok/Satış":
        dup_cols = ['magaza_kod', 'urun_kod']
        if all(col in df.columns for col in dup_cols):
            dup_count = df.duplicated(subset=dup_cols).sum()
            if dup_count > 0:
                issues.append(f"❌ {df_name}: {dup_count:,} duplicate kayıt")
    
    return issues, warnings

def clean_negative_values(df, columns):
    df = df.copy()
    for col in columns:
        if col in df.columns:
            if (df[col] < 0).any():
                df[col] = df[col].clip(lower=0)
    return df

# ============================================
# MENÜ
# ============================================
st.sidebar.title("📉 Lost Sales v4.0")
menu = st.sidebar.radio("Menü", ["🏠 Ana Sayfa", "📤 Veri Yükleme", "🔬 Analiz", "📊 Raporlar", "💾 Export"])

# ============================================
# ANA SAYFA
# ============================================
if menu == "🏠 Ana Sayfa":
    st.title("📉 Lost Sales Analizi v4.0 - SK Sistemi")
    st.markdown("---")
    
    st.info("""
    **Lost Sales:** Stok yetersizliği nedeniyle gerçekleşmeyen potansiyel satış
    
    🔥 **YENİ: SK (Satış Kaybı) Sistemi**
    - Trend'deki stoksuz günler için segment × gün bazlı SK hesaplanır
    - **Potansiyel Satış = Gerçek Satış + SK**
    - 5 seviyeli fallback: Ürün×Segment → Ürün×Global → MG×Segment → MG×Global → Kendi
    """)
    
    st.markdown("### 🚀 Kullanım Adımları")
    st.success("""
    1️⃣ Veri Yükleme → CSV dosyalarını yükle (Trend'de stok kolonu önemli!)
    2️⃣ Parametreler → Gün dağılım katsayılarını ayarla
    3️⃣ Analiz → SK hesaplamasını aktifleştir ve çalıştır
    4️⃣ Raporlar → SK istatistiklerini incele
    5️⃣ Export → Sonuçları indir
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Özellikler")
        st.markdown("""
        ✅ **🔥 SK (Satış Kaybı) hesaplama**
        ✅ **📅 Gün dağılım tablosu**
        ✅ **📊 Potansiyel satış analizi**
        ✅ Multi-level fallback (5 seviye)
        ✅ MG bazlı yeni ürün desteği
        ✅ Güvenilirlik skoru
        ✅ Detaylı SK raporları
        ✅ Veri kalitesi kontrolü
        """)
    
    with col2:
        st.markdown("### 📋 Gerekli Veriler")
        st.markdown("""
        🔴 **Zorunlu:**
        - Anlık Stok/Satış (7 günlük)
        - Depo Stok
        
        🟢 **Opsiyonel:**
        - Ürün Master (**mg kolonu önerilen!**)
        - Mağaza Master
        - **Trend (STOK kolonu ÖNEMLİ!)**
          Format: tarih, magaza_kod, urun_kod, satis, **stok**
        """)
    
    st.markdown("---")
    st.success("""
    🔥 **SK Sistemi Örnek:**
    
    Ruj X - M001 (30 gün trend):
    - Gün 1-10: Stoklu → 40 satış ✅
    - Gün 11-30: Stoksuz → 0 satış ❌
    
    SK Hesaplama:
    - Segment proxy: 28 adet/hafta
    - Cumartesi %18 → (28/7)×0.18 = 0.72 adet/gün
    - 20 gün SK = ~16 adet
    
    Potansiyel: 40 + 16 = 56 adet
    Günlük ort: 56/30 = 1.87 ✅ (eski: 1.33 ❌)
    """)

# ============================================
# VERİ YÜKLEME
# ============================================
elif menu == "📤 Veri Yükleme":
    st.header("📤 Veri Yükleme")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔴 Zorunlu Veriler")
        
        anlik_file = st.file_uploader("📊 Anlık Stok/Satış CSV", type=['csv'], key='anlik')
        if anlik_file:
            try:
                df = pd.read_csv(anlik_file)
                required = ['magaza_kod', 'urun_kod', 'stok', 'satis']
                if all(x in df.columns for x in required):
                    issues, warnings = validate_data_quality(df, "Anlık Stok/Satış")
                    df = clean_negative_values(df, ['stok', 'satis'])
                    st.session_state.anlik_stok_satis = df
                    st.success(f"✅ Yüklendi: {len(df):,} satır")
                    
                    if issues or warnings:
                        with st.expander("⚠️ Veri Kalitesi", expanded=True):
                            for issue in issues:
                                st.error(issue)
                            for warning in warnings:
                                st.warning(warning)
                else:
                    st.error(f"❌ Eksik kolonlar: {', '.join(required)}")
            except Exception as e:
                st.error(f"❌ Hata: {e}")
        
        depo_file = st.file_uploader("📦 Depo Stok CSV", type=['csv'], key='depo')
        if depo_file:
            try:
                df = pd.read_csv(depo_file)
                required = ['depo_kod', 'urun_kod', 'stok']
                if all(x in df.columns for x in required):
                    df = clean_negative_values(df, ['stok'])
                    st.session_state.depo_stok = df
                    st.success(f"✅ Yüklendi: {len(df):,} satır")
                else:
                    st.error(f"❌ Eksik kolonlar: {', '.join(required)}")
            except Exception as e:
                st.error(f"❌ Hata: {e}")
    
    with col2:
        st.subheader("🟢 Opsiyonel Veriler")
        
        urun_file = st.file_uploader("🏷️ Ürün Master CSV", type=['csv'], key='urun')
        if urun_file:
            try:
                df = pd.read_csv(urun_file)
                st.session_state.urun_master = df
                st.success(f"✅ Yüklendi: {len(df):,} ürün")
                st.info(f"Kolonlar: {', '.join(df.columns.tolist()[:5])}...")
            except Exception as e:
                st.error(f"❌ Hata: {e}")
        
        magaza_file = st.file_uploader("🏪 Mağaza Master CSV", type=['csv'], key='magaza')
        if magaza_file:
            try:
                df = pd.read_csv(magaza_file)
                st.session_state.magaza_master = df
                st.success(f"✅ Yüklendi: {len(df):,} mağaza")
            except Exception as e:
                st.error(f"❌ Hata: {e}")
        
        trend_file = st.file_uploader("📈 Trend CSV (stok kolonu önemli!)", type=['csv'], key='trend')
        if trend_file:
            try:
                df = pd.read_csv(trend_file)
                required = ['tarih', 'magaza_kod', 'urun_kod', 'satis']
                
                if all(x in df.columns for x in required):
                    df['tarih'] = pd.to_datetime(df['tarih'], errors='coerce')
                    
                    if 'stok' not in df.columns:
                        st.warning("⚠️ 'stok' kolonu yok - SK analizi yapılamaz!")
                    
                    st.session_state.haftalik_trend = df
                    st.success(f"✅ Yüklendi: {len(df):,} satır")
                    
                    min_tarih = df['tarih'].min()
                    max_tarih = df['tarih'].max()
                    gun_sayisi = (max_tarih - min_tarih).days + 1
                    
                    st.info(f"📅 {min_tarih.strftime('%d.%m.%Y')} - {max_tarih.strftime('%d.%m.%Y')} ({gun_sayisi} gün)")
                    st.info(f"📋 Kolonlar: {', '.join(df.columns.tolist())}")
                    
                    st.session_state.trend_gun_sayisi = gun_sayisi
                else:
                    st.error(f"❌ Eksik kolonlar: {', '.join(required)}")
            except Exception as e:
                st.error(f"❌ Hata: {e}")
    
    st.markdown("---")
    st.subheader("📊 Yüklü Veri Durumu")
    
    data_status = pd.DataFrame({
        'Veri': ['Anlık Stok/Satış', 'Depo Stok', 'Ürün Master', 'Mağaza Master', 'Trend'],
        'Zorunlu': ['🔴', '🔴', '🟢', '🟢', '🟢'],
        'Durum': [
            '✅ Yüklü' if st.session_state.anlik_stok_satis is not None else '❌ Yok',
            '✅ Yüklü' if st.session_state.depo_stok is not None else '❌ Yok',
            '✅ Yüklü' if st.session_state.urun_master is not None else '❌ Yok',
            '✅ Yüklü' if st.session_state.magaza_master is not None else '❌ Yok',
            f"✅ ({st.session_state.trend_gun_sayisi} gün)" if st.session_state.haftalik_trend is not None else '❌ Yok'
        ],
        'Satır': [
            f"{len(st.session_state.anlik_stok_satis):,}" if st.session_state.anlik_stok_satis is not None else '-',
            f"{len(st.session_state.depo_stok):,}" if st.session_state.depo_stok is not None else '-',
            f"{len(st.session_state.urun_master):,}" if st.session_state.urun_master is not None else '-',
            f"{len(st.session_state.magaza_master):,}" if st.session_state.magaza_master is not None else '-',
            f"{len(st.session_state.haftalik_trend):,}" if st.session_state.haftalik_trend is not None else '-'
        ]
    })
    
    st.dataframe(data_status, use_container_width=True, hide_index=True)

# ============================================
# ANALİZ
# ============================================
elif menu == "🔬 Analiz":
    st.header("🔬 Lost Sales Analizi")
    st.markdown("---")
    
    if st.session_state.anlik_stok_satis is None or st.session_state.depo_stok is None:
        st.error("❌ Zorunlu verileri yükleyin!")
        st.info("'Veri Yükleme' menüsünden Anlık Stok/Satış ve Depo Stok yükleyin.")
        st.stop()
    
    st.success("✅ Zorunlu veriler hazır!")
    st.markdown("---")
    
    # PARAMETRELER
    st.subheader("⚙️ Analiz Parametreleri")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        stok_esik = st.number_input("Stok Tükenme Eşiği", 0, 100, 0)
    with col2:
        min_satis = st.number_input("Minimum Satış", 0, 1000, 1)
    with col3:
        kayip_gun = st.number_input("Kayıp Gün (İleri)", 1, 30, 7)
    with col4:
        if st.session_state.haftalik_trend is not None:
            trend_kullan = st.checkbox("📈 Trend + SK", value=True,
                help="Trend'de stoksuz günler için SK hesapla")
        else:
            trend_kullan = False
            st.info("Trend yok")
    
    st.markdown("---")
    
    # GÜN DAĞILIM
    st.subheader("📅 Günlük Satış Dağılım Katsayıları")
    
    with st.expander("🔧 Gün Dağılım Ayarları", expanded=False):
        st.info("""
        **Gün Dağılım:** Haftanın her gününün toplam haftalık satış içindeki payı.
        Stoksuz günler için SK hesaplamada kullanılır.
        Toplam %100 olmalı!
        """)
        
        col1, col2, col3 = st.columns(3)
        gun_dagilim = {}
        
        with col1:
            st.write("**Hafta İçi:**")
            gun_dagilim['Pazartesi'] = st.slider("Pzt %", 0.0, 30.0, st.session_state.gun_dagilim['Pazartesi'], 0.5)
            gun_dagilim['Salı'] = st.slider("Sal %", 0.0, 30.0, st.session_state.gun_dagilim['Salı'], 0.5)
            gun_dagilim['Çarşamba'] = st.slider("Çar %", 0.0, 30.0, st.session_state.gun_dagilim['Çarşamba'], 0.5)
        
        with col2:
            gun_dagilim['Perşembe'] = st.slider("Per %", 0.0, 30.0, st.session_state.gun_dagilim['Perşembe'], 0.5)
            gun_dagilim['Cuma'] = st.slider("Cum %", 0.0, 30.0, st.session_state.gun_dagilim['Cuma'], 0.5)
        
        with col3:
            st.write("**Hafta Sonu:**")
            gun_dagilim['Cumartesi'] = st.slider("Cmt %", 0.0, 40.0, st.session_state.gun_dagilim['Cumartesi'], 0.5)
            gun_dagilim['Pazar'] = st.slider("Paz %", 0.0, 40.0, st.session_state.gun_dagilim['Pazar'], 0.5)
        
        toplam_yuzde = sum(gun_dagilim.values())
        
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col2:
            if abs(toplam_yuzde - 100.0) < 0.1:
                st.success(f"✅ Toplam: %{toplam_yuzde:.1f}")
            else:
                st.error(f"❌ Toplam: %{toplam_yuzde:.1f}")
        
        if st.button("💾 Gün Dağılımını Kaydet", use_container_width=True):
            if abs(toplam_yuzde - 100.0) < 0.1:
                st.session_state.gun_dagilim = gun_dagilim.copy()
                st.success("✅ Kaydedildi!")
                st.rerun()
            else:
                st.error("❌ Toplam %100 olmalı!")
        
        gun_df = pd.DataFrame({
            'Gün': list(gun_dagilim.keys()),
            'Oran (%)': list(gun_dagilim.values())
        })
        
        fig_gun = px.bar(gun_df, x='Gün', y='Oran (%)', title='Gün Dağılım',
                        color='Oran (%)', color_continuous_scale='Blues')
        st.plotly_chart(fig_gun, use_container_width=True)
    
    # Özet
    gun_ozet = st.session_state.gun_dagilim
    haftaici_ort = sum([gun_ozet[g] for g in ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma']]) / 5
    haftasonu_ort = (gun_ozet['Cumartesi'] + gun_ozet['Pazar']) / 2
    
    col1, col2, col3 = st.columns(3)
    col1.metric("📅 Hafta İçi Ort", f"%{haftaici_ort:.1f}")
    col2.metric("🎉 Hafta Sonu Ort", f"%{haftasonu_ort:.1f}")
    col3.metric("📊 Toplam", f"%{sum(gun_ozet.values()):.1f}")
    
    st.markdown("---")
    
    # HESAPLA BUTONU
    if st.button("🚀 LOST SALES HESAPLA", type="primary", use_container_width=True):
        try:
            progress = st.progress(0)
            status = st.empty()
            
            status.text("📊 Veriler hazırlanıyor...")
            progress.progress(10)
            
            anlik = st.session_state.anlik_stok_satis.copy()
            depo = st.session_state.depo_stok.copy()
            
            anlik['urun_kod'] = normalize_code(anlik['urun_kod'])
            anlik['magaza_kod'] = normalize_code(anlik['magaza_kod'])
            depo['urun_kod'] = normalize_code(depo['urun_kod'])
            
            # Günlük satış
            gun_isimleri = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
            bugun_adi = gun_isimleri[datetime.now().weekday()]
            bugun_yuzde = gun_ozet[bugun_adi]
            anlik['gunluk_satis'] = anlik['satis'] * (bugun_yuzde / 100)
            
            progress.progress(20)
            
            # Segmentasyon
            status.text("🎯 Segmentasyon...")
            magaza_agg = anlik.groupby('magaza_kod').agg({'stok': 'sum', 'satis': 'sum'}).reset_index()
            magaza_agg['cover'] = np.where(magaza_agg['satis'] > 0,
                                          magaza_agg['stok'] / (magaza_agg['satis'] / 7.0), 999)
            
            segment_ranges = [(0, 4), (5, 8), (9, 12), (12, 15), (15, 20), (20, float('inf'))]
            segment_labels = [f"{int(r[0])}-{int(r[1]) if r[1] != float('inf') else '20+'}" for r in segment_ranges]
            
            magaza_agg['segment'] = pd.cut(magaza_agg['cover'],
                bins=[r[0] for r in segment_ranges] + [segment_ranges[-1][1]],
                labels=segment_labels, include_lowest=True)
            
            anlik = anlik.merge(magaza_agg[['magaza_kod', 'segment']], on='magaza_kod', how='left')
            anlik['segment'] = anlik['segment'].astype(str)
            
            progress.progress(40)
            
            # Depo stok
            status.text("📦 Depo stok...")
            depo_toplam = depo.groupby('urun_kod')['stok'].sum().reset_index()
            depo_toplam.columns = ['urun_kod', 'depo_stok']
            anlik = anlik.merge(depo_toplam, on='urun_kod', how='left')
            anlik['depo_stok'] = anlik['depo_stok'].fillna(0)
            
            # Stok durumu
            anlik['magaza_stok_durumu'] = np.where(anlik['stok'] <= stok_esik, 'Tükendi', 'Var')
            anlik['depo_stok_durumu'] = np.where(anlik['depo_stok'] > 0, 'Var', 'Yok')
            anlik['lost_sales_tip'] = np.select([
                (anlik['magaza_stok_durumu'] == 'Tükendi') & (anlik['depo_stok_durumu'] == 'Var'),
                (anlik['magaza_stok_durumu'] == 'Tükendi') & (anlik['depo_stok_durumu'] == 'Yok')
            ], ['Tip 1: Depoda Var', 'Tip 2: Depoda Yok'], default='Kayıp Yok')
            
            progress.progress(60)
            
            # PROXY HESAPLAMA
            status.text("🧮 Proxy hesaplanıyor...")
            
            mg_fallback_var = False
            sk_kullanildi = False
            
            if trend_kullan and st.session_state.haftalik_trend is not None:
                status.text("📈 Trend + SK analizi...")
                
                trend_df = st.session_state.haftalik_trend.copy()
                trend_df['urun_kod'] = normalize_code(trend_df['urun_kod'])
                trend_df['magaza_kod'] = normalize_code(trend_df['magaza_kod'])
                
                if 'tarih' in trend_df.columns:
                    trend_df['tarih'] = pd.to_datetime(trend_df['tarih'], errors='coerce')
                    trend_df['gun_index'] = trend_df['tarih'].dt.dayofweek
                    trend_df['gun_adi'] = trend_df['gun_index'].map({
                        0: 'Pazartesi', 1: 'Salı', 2: 'Çarşamba', 3: 'Perşembe',
                        4: 'Cuma', 5: 'Cumartesi', 6: 'Pazar'
                    })
                
                trend_df = trend_df.merge(magaza_agg[['magaza_kod', 'segment']], on='magaza_kod', how='left')
                trend_df['segment'] = trend_df['segment'].astype(str)
                
                if 'stok' in trend_df.columns:
                    trend_df['stoklu'] = trend_df['stok'] > 0
                    sk_kullanildi = True
                else:
                    trend_df['stoklu'] = True
                
                stoklu_trend = trend_df[trend_df['stoklu'] == True].copy()
                
                # Segment ortalaması
                segment_haftalik = stoklu_trend.groupby(['urun_kod', 'segment']).agg({'satis': 'sum'}).reset_index()
                segment_haftalik['haftalik_satis'] = segment_haftalik['satis']
                segment_haftalik = segment_haftalik[['urun_kod', 'segment', 'haftalik_satis']]
                
                # Global ortalama
                urun_haftalik = stoklu_trend.groupby('urun_kod').agg({'satis': 'sum'}).reset_index()
                urun_haftalik['global_haftalik_satis'] = urun_haftalik['satis']
                urun_haftalik = urun_haftalik[['urun_kod', 'global_haftalik_satis']]
                
                # MG fallback
                if st.session_state.urun_master is not None:
                    urun_m = st.session_state.urun_master.copy()
                    if 'urun_kod' in urun_m.columns and 'mg' in urun_m.columns:
                        urun_m['urun_kod'] = normalize_code(urun_m['urun_kod'])
                        urun_mg_map = urun_m[['urun_kod', 'mg']].copy()
                        
                        stoklu_trend = stoklu_trend.merge(urun_mg_map, on='urun_kod', how='left')
                        
                        mg_segment_haftalik = stoklu_trend.groupby(['mg', 'segment']).agg({'satis': 'sum'}).reset_index()
                        mg_segment_haftalik['mg_segment_haftalik'] = mg_segment_haftalik['satis']
                        mg_segment_haftalik = mg_segment_haftalik[['mg', 'segment', 'mg_segment_haftalik']]
                        
                        mg_global_haftalik = stoklu_trend.groupby('mg').agg({'satis': 'sum'}).reset_index()
                        mg_global_haftalik['mg_global_haftalik'] = mg_global_haftalik['satis']
                        mg_global_haftalik = mg_global_haftalik[['mg', 'mg_global_haftalik']]
                        
                        mg_fallback_var = True
                
                # SK hesapla
                if sk_kullanildi:
                    trend_df = trend_df.merge(segment_haftalik, on=['urun_kod', 'segment'], how='left')
                    trend_df = trend_df.merge(urun_haftalik, on='urun_kod', how='left')
                    
                    if mg_fallback_var:
                        trend_df = trend_df.merge(urun_mg_map, on='urun_kod', how='left')
                        trend_df = trend_df.merge(mg_segment_haftalik, on=['mg', 'segment'], how='left')
                        trend_df = trend_df.merge(mg_global_haftalik, on='mg', how='left')
                    
                    # Gün dağılım
                    gun_dagilim_df = pd.DataFrame({
                        'gun_adi': list(gun_ozet.keys()),
                        'gun_dagilim_yuzde': list(gun_ozet.values())
                    })
                    trend_df = trend_df.merge(gun_dagilim_df, on='gun_adi', how='left')
                    trend_df['gun_dagilim_yuzde'] = trend_df['gun_dagilim_yuzde'].fillna(14.3)
                    
                    # SK hesapla
                    trend_df['sk_haftalik_proxy'] = trend_df['haftalik_satis'].fillna(trend_df['global_haftalik_satis'])
                    
                    if mg_fallback_var:
                        trend_df['sk_haftalik_proxy'] = trend_df['sk_haftalik_proxy'].fillna(
                            trend_df['mg_segment_haftalik']).fillna(trend_df['mg_global_haftalik'])
                    
                    trend_df['sk_gunluk'] = np.where(
                        trend_df['stoklu'] == False,
                        trend_df['sk_haftalik_proxy'] * (trend_df['gun_dagilim_yuzde'] / 100),
                        0
                    )
                    
                    trend_df['potansiyel_satis'] = trend_df['satis'] + trend_df['sk_gunluk']
                    
                    # Potansiyel satıştan ortalama
                    trend_gun_sayisi = st.session_state.trend_gun_sayisi or 30
                    
                    segment_potansiyel = trend_df.groupby(['urun_kod', 'segment']).agg({
                        'potansiyel_satis': 'sum',
                        'stoklu': 'sum'
                    }).reset_index()
                    
                    segment_potansiyel['stoklu_gun_sayisi'] = segment_potansiyel['stoklu']
                    segment_potansiyel['stoksuz_gun_sayisi'] = trend_gun_sayisi - segment_potansiyel['stoklu_gun_sayisi']
                    segment_potansiyel['stoklu_gun_orani'] = (segment_potansiyel['stoklu_gun_sayisi'] / trend_gun_sayisi * 100).round(1)
                    segment_potansiyel['segment_ort_gunluk'] = segment_potansiyel['potansiyel_satis'] / trend_gun_sayisi
                    segment_potansiyel = segment_potansiyel[['urun_kod', 'segment', 'segment_ort_gunluk', 
                                                             'stoklu_gun_sayisi', 'stoksuz_gun_sayisi', 'stoklu_gun_orani']]
                    
                    urun_potansiyel = trend_df.groupby('urun_kod').agg({'potansiyel_satis': 'sum'}).reset_index()
                    urun_potansiyel['global_ort_gunluk'] = urun_potansiyel['potansiyel_satis'] / trend_gun_sayisi
                    urun_potansiyel = urun_potansiyel[['urun_kod', 'global_ort_gunluk']]
                    
                    if mg_fallback_var:
                        mg_potansiyel_segment = trend_df.groupby(['mg', 'segment']).agg({'potansiyel_satis': 'sum'}).reset_index()
                        mg_potansiyel_segment['mg_segment_ort_gunluk'] = mg_potansiyel_segment['potansiyel_satis'] / trend_gun_sayisi
                        mg_potansiyel_segment = mg_potansiyel_segment[['mg', 'segment', 'mg_segment_ort_gunluk']]
                        
                        mg_potansiyel_global = trend_df.groupby('mg').agg({'potansiyel_satis': 'sum'}).reset_index()
                        mg_potansiyel_global['mg_global_ort_gunluk'] = mg_potansiyel_global['potansiyel_satis'] / trend_gun_sayisi
                        mg_potansiyel_global = mg_potansiyel_global[['mg', 'mg_global_ort_gunluk']]
                    
                    anlik = anlik.merge(segment_potansiyel, on=['urun_kod', 'segment'], how='left')
                    anlik = anlik.merge(urun_potansiyel, on='urun_kod', how='left')
                    
                    if mg_fallback_var:
                        anlik = anlik.merge(urun_mg_map, on='urun_kod', how='left')
                        anlik = anlik.merge(mg_potansiyel_segment, on=['mg', 'segment'], how='left')
                        anlik = anlik.merge(mg_potansiyel_global, on='mg', how='left')
                    
                    proxy_kaynak = f"Trend + SK ({trend_gun_sayisi} gün)"
                else:
                    # SK olmadan trend
                    segment_ort = stoklu_trend.groupby(['urun_kod', 'segment'])['satis'].mean().reset_index()
                    segment_ort.columns = ['urun_kod', 'segment', 'segment_ort_gunluk']
                    
                    urun_global = stoklu_trend.groupby('urun_kod')['satis'].mean().reset_index()
                    urun_global.columns = ['urun_kod', 'global_ort_gunluk']
                    
                    anlik = anlik.merge(segment_ort, on=['urun_kod', 'segment'], how='left')
                    anlik = anlik.merge(urun_global, on='urun_kod', how='left')
                    
                    proxy_kaynak = "Trend (SK yok - stok kolonu eksik)"
            else:
                # Anlık veri
                status.text("📊 Anlık veri proxy...")
                stoklu_df = anlik[anlik['magaza_stok_durumu'] == 'Var'].copy()
                
                segment_ort = stoklu_df.groupby(['urun_kod', 'segment'])['gunluk_satis'].mean().reset_index()
                segment_ort.columns = ['urun_kod', 'segment', 'segment_ort_gunluk']
                
                urun_global = stoklu_df.groupby('urun_kod')['gunluk_satis'].mean().reset_index()
                urun_global.columns = ['urun_kod', 'global_ort_gunluk']
                
                anlik = anlik.merge(segment_ort, on=['urun_kod', 'segment'], how='left')
                anlik = anlik.merge(urun_global, on='urun_kod', how='left')
                
                proxy_kaynak = "Anlık Veri (7 günlük)"
            
            progress.progress(70)
            
            # Kayıp hesapla
            status.text("💸 Kayıp hesaplanıyor...")
            
            if mg_fallback_var:
                anlik['tahmin_gunluk'] = np.where(
                    anlik['magaza_stok_durumu'] == 'Tükendi',
                    anlik['segment_ort_gunluk'].fillna(anlik['global_ort_gunluk'])
                        .fillna(anlik.get('mg_segment_ort_gunluk', 0))
                        .fillna(anlik.get('mg_global_ort_gunluk', 0))
                        .fillna(anlik['gunluk_satis']),
                    anlik['gunluk_satis']
                )
                
                anlik['proxy_fallback_tip'] = np.select([
                    anlik['segment_ort_gunluk'].notna(),
                    anlik['global_ort_gunluk'].notna(),
                    anlik.get('mg_segment_ort_gunluk', pd.Series([np.nan]*len(anlik))).notna(),
                    anlik.get('mg_global_ort_gunluk', pd.Series([np.nan]*len(anlik))).notna()
                ], [
                    'Ürün × Segment',
                    'Ürün × Global',
                    'MG × Segment (Yeni Ürün)',
                    'MG × Global (Yeni Ürün)'
                ], default='Kendi Satışı')
            else:
                anlik['tahmin_gunluk'] = np.where(
                    anlik['magaza_stok_durumu'] == 'Tükendi',
                    anlik['segment_ort_gunluk'].fillna(anlik['global_ort_gunluk']).fillna(anlik['gunluk_satis']),
                    anlik['gunluk_satis']
                )
                
                anlik['proxy_fallback_tip'] = np.select([
                    anlik['segment_ort_gunluk'].notna(),
                    anlik['global_ort_gunluk'].notna()
                ], ['Ürün × Segment', 'Ürün × Global'], default='Kendi Satışı')
            
            anlik['tahmini_kayip'] = anlik['tahmin_gunluk'] * kayip_gun
            
            # Master veriler
            if st.session_state.urun_master is not None:
                urun_m = st.session_state.urun_master.copy()
                if 'urun_kod' in urun_m.columns:
                    urun_m['urun_kod'] = normalize_code(urun_m['urun_kod'])
                    cols = ['urun_kod']
                    if 'urun_ad' in urun_m.columns:
                        cols.append('urun_ad')
                    anlik = anlik.merge(urun_m[cols], on='urun_kod', how='left')
            
            if st.session_state.magaza_master is not None:
                mag_m = st.session_state.magaza_master.copy()
                if 'magaza_kod' in mag_m.columns:
                    mag_m['magaza_kod'] = normalize_code(mag_m['magaza_kod'])
                    cols = ['magaza_kod']
                    if 'magaza_ad' in mag_m.columns:
                        cols.append('magaza_ad')
                    anlik = anlik.merge(mag_m[cols], on='magaza_kod', how='left')
            
            progress.progress(90)
            
            # Filtrele
            kayip_df = anlik[
                (anlik['lost_sales_tip'] != 'Kayıp Yok') &
                (anlik['gunluk_satis'] >= min_satis) &
                (anlik['tahmini_kayip'] > 0)
            ].copy()
            
            st.session_state.lost_sales_sonuc = kayip_df
            
            progress.progress(100)
            status.text("✅ Tamamlandı!")
            
            st.success("🎉 Analiz tamamlandı!")
            st.balloons()
            
            # ÖZET METRİKLER
            st.markdown("---")
            st.subheader("📊 Hızlı Özet")
            
            # Tablo formatında özet
            ozet_data = {
                'Metrik': ['💸 Toplam Kayıp', '🏪 Tip 1', '📦 Tip 2', '🏷️ SKU', 
                          '📈 Proxy', '🔥 SK', '🏷️ MG Fallback'],
                'Değer': [
                    f"{int(kayip_df['tahmini_kayip'].sum()):,}",
                    f"{int(kayip_df[kayip_df['lost_sales_tip'] == 'Tip 1: Depoda Var']['tahmini_kayip'].sum()):,}",
                    f"{int(kayip_df[kayip_df['lost_sales_tip'] == 'Tip 2: Depoda Yok']['tahmini_kayip'].sum()):,}",
                    f"{kayip_df['urun_kod'].nunique()}",
                    proxy_kaynak if sk_kullanildi else "Anlık",
                    "✅ Aktif" if sk_kullanildi else "❌ Yok",
                    f"{(kayip_df['proxy_fallback_tip'].str.contains('MG', na=False)).sum():,}" if mg_fallback_var else f"{kayip_df.get('segment_ort_gunluk', pd.Series([np.nan]*len(kayip_df))).isnull().sum():,}"
                ]
            }
            
            st.dataframe(pd.DataFrame(ozet_data), use_container_width=True, hide_index=True)
            
            # SK İstatistikleri
            if sk_kullanildi and 'stoklu_gun_orani' in kayip_df.columns:
                st.markdown("---")
                st.subheader("🔥 SK İstatistikleri")
                
                ort_stoklu = kayip_df['stoklu_gun_orani'].mean()
                dusuk = (kayip_df['stoklu_gun_orani'] < 50).sum()
                yuksek = (kayip_df['stoklu_gun_orani'] < 30).sum()
                
                if ort_stoklu >= 70:
                    kalite = "Yüksek ✅"
                elif ort_stoklu >= 50:
                    kalite = "Orta ⚠️"
                else:
                    kalite = "Düşük ❌"
                
                sk_ozet = {
                    'Metrik': ['📊 Ort. Stoklu Gün', '⚠️ Düşük Güvenilir', '🔴 Yüksek SK', '📈 Trend Kalitesi'],
                    'Değer': [f"%{ort_stoklu:.1f}", f"{dusuk:,}", f"{yuksek:,}", kalite]
                }
                
                st.dataframe(pd.DataFrame(sk_ozet), use_container_width=True, hide_index=True)
            
            # Proxy dağılımı
            if 'proxy_fallback_tip' in kayip_df.columns:
                st.markdown("---")
                st.subheader("🔄 Proxy Yöntemi Dağılımı")
                
                fallback_dist = kayip_df['proxy_fallback_tip'].value_counts().reset_index()
                fallback_dist.columns = ['Yöntem', 'Kayıt']
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    fig = px.bar(fallback_dist, x='Yöntem', y='Kayıt',
                                title='Proxy Hesaplama Yöntemi',
                                color='Kayıt', color_continuous_scale='Blues')
                    fig.update_xaxes(tickangle=45)  # update_xaxis değil update_xaxes!
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.dataframe(fallback_dist, use_container_width=True, hide_index=True)
        
        except Exception as e:
            st.error(f"❌ Hata: {e}")
            import traceback
            st.code(traceback.format_exc())

# ============================================
# RAPORLAR
# ============================================
elif menu == "📊 Raporlar":
    st.header("📊 Detaylı Raporlar")
    st.markdown("---")
    
    df = st.session_state.lost_sales_sonuc
    
    if df is None:
        st.warning("⚠️ Henüz analiz yapılmadı!")
        st.info("'Analiz' menüsünden hesaplama yapın.")
        st.stop()
    
    # Özet metrikler
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💸 Toplam Kayıp", f"{int(df['tahmini_kayip'].sum()):,}")
    col2.metric("🏷️ SKU", df['urun_kod'].nunique())
    col3.metric("🏪 Mağaza", df['magaza_kod'].nunique())
    col4.metric("📋 Satır", f"{len(df):,}")
    
    st.markdown("---")
    
    # Tablar
    tab1, tab2, tab3, tab4 = st.tabs(["📦 Ürün Bazında", "🏪 Mağaza Bazında", "📊 Grafikler", "📅 Zaman Analizi"])
    
    with tab1:
        st.subheader("📦 Ürün Bazında Analiz")
        
        grup_cols = ['urun_kod', 'lost_sales_tip']
        if 'urun_ad' in df.columns:
            grup_cols.insert(1, 'urun_ad')
        
        urun_grp = df.groupby(grup_cols)['tahmini_kayip'].sum().reset_index()
        urun_grp['tahmini_kayip'] = urun_grp['tahmini_kayip'].round(0).astype(int)
        urun_grp = urun_grp.sort_values('tahmini_kayip', ascending=False)
        
        st.dataframe(urun_grp.head(50), use_container_width=True, height=400)
        
        csv = urun_grp.to_csv(index=False, encoding='utf-8-sig')
        st.download_button("📥 CSV İndir", csv,
            f"urun_analizi_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")
    
    with tab2:
        st.subheader("🏪 Mağaza Bazında Analiz")
        
        grup_cols = ['magaza_kod', 'lost_sales_tip']
        if 'magaza_ad' in df.columns:
            grup_cols.insert(1, 'magaza_ad')
        
        mag_grp = df.groupby(grup_cols)['tahmini_kayip'].sum().reset_index()
        mag_grp['tahmini_kayip'] = mag_grp['tahmini_kayip'].round(0).astype(int)
        mag_grp = mag_grp.sort_values('tahmini_kayip', ascending=False)
        
        st.dataframe(mag_grp.head(50), use_container_width=True, height=400)
        
        csv = mag_grp.to_csv(index=False, encoding='utf-8-sig')
        st.download_button("📥 CSV İndir", csv,
            f"magaza_analizi_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv")
    
    with tab3:
        st.subheader("📊 Görselleştirme")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Tip dağılımı
            tip_dag = df.groupby('lost_sales_tip')['tahmini_kayip'].sum().reset_index()
            fig1 = px.pie(tip_dag, values='tahmini_kayip', names='lost_sales_tip',
                         title='Tip Dağılımı',
                         color_discrete_map={'Tip 1: Depoda Var': '#FF6B6B', 'Tip 2: Depoda Yok': '#4ECDC4'})
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Top 10 Ürün
            if 'urun_ad' in df.columns:
                top10 = df.groupby('urun_ad')['tahmini_kayip'].sum().nlargest(10).reset_index()
                y_col = 'urun_ad'
            else:
                top10 = df.groupby('urun_kod')['tahmini_kayip'].sum().nlargest(10).reset_index()
                y_col = 'urun_kod'
            
            fig2 = px.bar(top10, x='tahmini_kayip', y=y_col, orientation='h',
                         title='Top 10 Ürün', color='tahmini_kayip', color_continuous_scale='Reds')
            st.plotly_chart(fig2, use_container_width=True)
        
        # Segment analizi
        if 'segment' in df.columns:
            st.markdown("---")
            seg_dag = df.groupby(['segment', 'lost_sales_tip'])['tahmini_kayip'].sum().reset_index()
            
            fig3 = px.bar(seg_dag, x='segment', y='tahmini_kayip', color='lost_sales_tip',
                         title='Segment × Tip', barmode='stack',
                         color_discrete_map={'Tip 1: Depoda Var': '#FF6B6B', 'Tip 2: Depoda Yok': '#4ECDC4'})
            st.plotly_chart(fig3, use_container_width=True)
    
    with tab4:
        st.subheader("📅 Zaman Bazlı Analiz")
        
        # Trend verisi kontrolü
        if st.session_state.haftalik_trend is None:
            st.warning("⚠️ Trend verisi yok! Bu analiz için trend.csv gerekli.")
            st.info("Trend verisi yükleyip tekrar analiz yapın.")
        else:
            trend_df = st.session_state.haftalik_trend.copy()
            
            if 'tarih' in trend_df.columns:
                trend_df['tarih'] = pd.to_datetime(trend_df['tarih'], errors='coerce')
                trend_df = trend_df.dropna(subset=['tarih'])
                
                # Yıl-Hafta hesapla
                trend_df['yil'] = trend_df['tarih'].dt.year
                trend_df['hafta'] = trend_df['tarih'].dt.isocalendar().week
                trend_df['yil_hafta'] = trend_df['yil'].astype(str) + '-W' + trend_df['hafta'].astype(str).str.zfill(2)
                
                # Stok durumu
                if 'stok' in trend_df.columns:
                    trend_df['stoklu'] = trend_df['stok'] > 0
                    trend_df['stoksuz'] = ~trend_df['stoklu']
                else:
                    trend_df['stoklu'] = True
                    trend_df['stoksuz'] = False
                    st.warning("⚠️ 'stok' kolonu yok - SK hesaplanamıyor")
                
                # Haftalık toplam
                haftalik = trend_df.groupby('yil_hafta').agg({
                    'satis': 'sum',
                    'stoksuz': 'sum'
                }).reset_index()
                
                haftalik.columns = ['Yıl-Hafta', 'Toplam Satış', 'Stoksuz Gün Sayısı']
                
                # SK tahmini (basit)
                if 'stok' in trend_df.columns:
                    # Ortalama günlük satış
                    ort_gunluk = haftalik['Toplam Satış'].mean() / 7
                    haftalik['Tahmini SK'] = (haftalik['Stoksuz Gün Sayısı'] * ort_gunluk).round(0).astype(int)
                    haftalik['Potansiyel Satış'] = haftalik['Toplam Satış'] + haftalik['Tahmini SK']
                    haftalik['SK/Satış (%)'] = ((haftalik['Tahmini SK'] / haftalik['Potansiyel Satış']) * 100).round(1)
                else:
                    haftalik['Tahmini SK'] = 0
                    haftalik['Potansiyel Satış'] = haftalik['Toplam Satış']
                    haftalik['SK/Satış (%)'] = 0.0
                
                haftalik['Toplam Satış'] = haftalik['Toplam Satış'].astype(int)
                haftalik['Potansiyel Satış'] = haftalik['Potansiyel Satış'].astype(int)
                
                # Özet metrikler
                st.markdown("### 📊 Toplam Özet")
                
                col1, col2, col3, col4 = st.columns(4)
                
                toplam_satis = haftalik['Toplam Satış'].sum()
                toplam_sk = haftalik['Tahmini SK'].sum()
                toplam_potansiyel = haftalik['Potansiyel Satış'].sum()
                ort_sk_oran = (toplam_sk / toplam_potansiyel * 100) if toplam_potansiyel > 0 else 0
                
                col1.metric("📈 Toplam Satış", f"{toplam_satis:,}")
                col2.metric("🔥 Toplam SK", f"{toplam_sk:,}")
                col3.metric("💎 Potansiyel Satış", f"{toplam_potansiyel:,}")
                col4.metric("📊 Ort SK/Satış", f"%{ort_sk_oran:.1f}")
                
                st.markdown("---")
                
                # Tablo
                st.markdown("### 📋 Haftalık Detay")
                st.dataframe(haftalik, use_container_width=True, hide_index=True)
                
                # Grafik
                st.markdown("---")
                st.markdown("### 📊 Haftalık Trend Grafiği")
                
                # Grafik için veri hazırla
                haftalik_melted = haftalik.melt(
                    id_vars=['Yıl-Hafta'],
                    value_vars=['Toplam Satış', 'Tahmini SK'],
                    var_name='Tip',
                    value_name='Adet'
                )
                
                fig_trend = px.bar(
                    haftalik_melted,
                    x='Yıl-Hafta',
                    y='Adet',
                    color='Tip',
                    title='Haftalık Satış vs SK Trendi',
                    barmode='stack',
                    color_discrete_map={
                        'Toplam Satış': '#4ECDC4',
                        'Tahmini SK': '#FF6B6B'
                    }
                )
                
                fig_trend.update_xaxes(tickangle=45)
                fig_trend.update_layout(
                    xaxis_title="Hafta",
                    yaxis_title="Adet",
                    legend_title="Metrik"
                )
                
                st.plotly_chart(fig_trend, use_container_width=True)
                
                # SK Oranı Grafiği
                st.markdown("---")
                st.markdown("### 📈 SK/Satış Oranı Trendi")
                
                fig_oran = px.line(
                    haftalik,
                    x='Yıl-Hafta',
                    y='SK/Satış (%)',
                    title='Haftalık SK/Satış Oranı (%)',
                    markers=True
                )
                
                fig_oran.update_xaxes(tickangle=45)
                fig_oran.update_traces(line_color='#FF6B6B', marker=dict(size=8))
                fig_oran.add_hline(y=ort_sk_oran, line_dash="dash", 
                                  line_color="gray",
                                  annotation_text=f"Ortalama: %{ort_sk_oran:.1f}")
                
                st.plotly_chart(fig_oran, use_container_width=True)
                
                # İndirme
                st.markdown("---")
                csv_haftalik = haftalik.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    "📥 Haftalık Analiz İndir (CSV)",
                    csv_haftalik,
                    f"haftalik_analiz_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    "text/csv",
                    use_container_width=True
                )
            else:
                st.error("❌ Trend verisinde 'tarih' kolonu bulunamadı!")

# ============================================
# EXPORT
# ============================================
elif menu == "💾 Export":
    st.header("💾 Sonuçları Dışa Aktar")
    st.markdown("---")
    
    df = st.session_state.lost_sales_sonuc
    
    if df is None:
        st.warning("⚠️ Henüz analiz yapılmadı!")
        st.info("'Analiz' menüsünden hesaplama yapın.")
        st.stop()
    
    st.success(f"✅ {len(df):,} satır veri hazır")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📄 Detaylı Rapor")
        csv = df.to_csv(index=False, encoding='utf-8-sig')
        st.download_button("📥 CSV İndir (Tümü)", csv,
            f"lost_sales_detay_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv",
            use_container_width=True)
    
    with col2:
        st.subheader("📦 Ürün Özeti")
        grup_cols = ['urun_kod']
        if 'urun_ad' in df.columns:
            grup_cols.append('urun_ad')
        urun_ozet = df.groupby(grup_cols)['tahmini_kayip'].sum().reset_index()
        urun_ozet['tahmini_kayip'] = urun_ozet['tahmini_kayip'].round(0).astype(int)
        
        csv_urun = urun_ozet.to_csv(index=False, encoding='utf-8-sig')
        st.download_button("📥 CSV İndir (Ürün)", csv_urun,
            f"lost_sales_urun_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv",
            use_container_width=True)
    
    with col3:
        st.subheader("🏪 Mağaza Özeti")
        grup_cols = ['magaza_kod']
        if 'magaza_ad' in df.columns:
            grup_cols.append('magaza_ad')
        mag_ozet = df.groupby(grup_cols)['tahmini_kayip'].sum().reset_index()
        mag_ozet['tahmini_kayip'] = mag_ozet['tahmini_kayip'].round(0).astype(int)
        
        csv_mag = mag_ozet.to_csv(index=False, encoding='utf-8-sig')
        st.download_button("📥 CSV İndir (Mağaza)", csv_mag,
            f"lost_sales_magaza_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", "text/csv",
            use_container_width=True)

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 10px;'>
    <p>📉 <strong>Lost Sales v4.0 - SK Sistemi</strong></p>
    <p style='font-size: 0.9em;'>
        ✅ Veri Kalitesi | ✅ Multi-Level Fallback | 
        ✅ MG Bazlı Yeni Ürün | ✅ <strong>SK Hesaplama</strong> | 
        ✅ <strong>Gün Dağılım</strong> | ✅ <strong>Potansiyel Satış</strong>
    </p>
    <p style='font-size: 0.8em;'>
        Potansiyel Satış = Gerçek Satış + SK | 
        Fallback: Ürün×Segment → Ürün×Global → MG×Segment → MG×Global → Kendi
    </p>
    <p style='font-size: 0.8em;'>AR4U - Thorius</p>
</div>
""", unsafe_allow_html=True)
