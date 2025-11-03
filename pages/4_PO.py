import streamlit as st
import pandas as pd
import numpy as np
import time

# 🎯 STREAMLIT ARROW HATASI ÇÖZÜMÜ - TÜM DATAFRAME'LERİ KAPAT
def disable_dataframes(data, **kwargs):
    if isinstance(data, pd.DataFrame):
        st.write(f"📊 Veri: {data.shape[0]} satır × {data.shape[1]} sütun")
        st.write("📋 Sütunlar:", list(data.columns))
        
        # İlk 3 satırı basitçe göster
        if st.checkbox("👀 İlk 3 satırı göster"):
            for i in range(min(3, len(data))):
                with st.expander(f"Satır {i+1}"):
                    for col in data.columns:
                        st.write(f"**{col}:** {data.iloc[i][col]}")
        return
    
    # DataFrame değilse normal göster
    st.write(data)

# TÜM DATAFRAME GÖSTERİMLERİNİ DEĞİŞTİR
st.dataframe = disable_dataframes
st.data_editor = disable_dataframes  
st.table = disable_dataframes




# 🎯 DATAFRAME GÖSTERİMİNİ BASİTLEŞTİR
def simple_display(data, **kwargs):
    if isinstance(data, pd.DataFrame):
        st.write(f"📊 Veri: {len(data)} satır × {len(data.columns)} sütun")
        if st.checkbox("🔍 İlk 10 satırı göster"):
            for i in range(min(10, len(data))):
                st.write(f"**Satır {i+1}:**", dict(data.iloc[i]))
        return
    st.write(data)

st.dataframe = simple_display

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Alım Sipariş (PO)",
    page_icon="💵",
    layout="wide"
)

# Session state başlatma
if 'urun_master' not in st.session_state:
    st.session_state.urun_master = None
if 'magaza_master' not in st.session_state:
    st.session_state.magaza_master = None
if 'anlik_stok_satis' not in st.session_state:
    st.session_state.anlik_stok_satis = None
if 'depo_stok' not in st.session_state:
    st.session_state.depo_stok = None
if 'kpi' not in st.session_state:
    st.session_state.kpi = None
if 'segmentation_params' not in st.session_state:
    st.session_state.segmentation_params = {
        'product_ranges': [(0, 4), (5, 8), (9, 12), (12, 15), (15, 20), (20, float('inf'))],
        'store_ranges': [(0, 4), (5, 8), (9, 12), (12, 15), (15, 20), (20, float('inf'))]
    }
if 'cover_segment_matrix' not in st.session_state:
    st.session_state.cover_segment_matrix = None
if 'sevkiyat_sonuc' not in st.session_state:
    st.session_state.sevkiyat_sonuc = None
if 'alim_siparis_sonuc' not in st.session_state:
    st.session_state.alim_siparis_sonuc = None
if 'po_yasak' not in st.session_state:
    st.session_state.po_yasak = None
if 'po_detay_kpi' not in st.session_state:
    st.session_state.po_detay_kpi = None

# Sidebar menü 
st.sidebar.title("💵 Alım Sipariş (Purchase Order)")
menu = st.sidebar.radio(
    "Menü",
    ["🏠 Ana Sayfa", "💵 Alım Sipariş Hesaplama", "📊 Alım Sipariş Raporları", "📦 Depo Bazlı Sipariş"]
)

# ============================================
# 🏠 ANA SAYFA
# ============================================
if menu == "🏠 Ana Sayfa":
    st.title("💵 Alım Sipariş (Purchase Order) Sistemi")
    st.markdown("---")
    
    # VERİ KONTROLÜ
    required_data = {
        "Anlık Stok/Satış": st.session_state.anlik_stok_satis,
        "Depo Stok": st.session_state.depo_stok,
        "KPI": st.session_state.kpi
    }
    
    optional_data = {
        "PO Yasak": st.session_state.po_yasak,
        "PO Detay KPI": st.session_state.po_detay_kpi,
        "Ürün Master": st.session_state.urun_master,
        "Mağaza Master": st.session_state.magaza_master
    }
    
    missing_data = [name for name, data in required_data.items() if data is None]
    
    if missing_data:
        st.error("❌ Gerekli veriler yüklenmemiş!")
        st.warning(f"**Eksik veriler:** {', '.join(missing_data)}")
        
        st.info("""
        **👉 Lütfen önce veri yükleme sayfasından CSV dosyalarınızı yükleyin.**
        
        **Zorunlu dosyalar:**
        - Anlık Stok/Satış
        - Depo Stok
        - KPI
        
        **Opsiyonel dosyalar (önerilir):**
        - Ürün Master (koli bilgisi, durum, ithal bilgisi için)
        - PO Yasak (yasak ürünler ve açık siparişler için)
        - PO Detay KPI (marka/MG bazında özel hedefler için)
        """)
        
        if st.button("➡️ Veri Yükleme Sayfasına Git", type="primary", width='stretch'):
            st.switch_page("pages/0_Veri_Yukleme.py")
        
        st.stop()
    
    # Opsiyonel veri durumu
    st.markdown("### 📊 Veri Durumu")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Zorunlu Veriler:**")
        for name, data in required_data.items():
            if data is not None:
                st.success(f"✅ {name}")
            else:
                st.error(f"❌ {name}")
    
    with col2:
        st.markdown("**Opsiyonel Veriler:**")
        for name, data in optional_data.items():
            if data is not None:
                st.success(f"✅ {name}")
            else:
                st.warning(f"⚠️ {name}")
    
    st.markdown("---")
    
    st.markdown("""
    ### 🎯 Yenilikler ve Özellikler
    
    **🆕 Gelişmiş Özellikler:**
    
    1. **📋 PO Yasak Kontrolü**
       - Yasak ürünleri otomatik filtreleme
       - Açık sipariş miktarlarını düşme
    
    2. **🎯 Detaylı KPI Hedefleri**
       - Marka + Mal Grubu bazında özel cover ve marj hedefleri
       - Dinamik hedef yönetimi
    
    3. **📦 Koli Bazında Sipariş**
       - Otomatik koli yuvarlaması
       - Adet ve koli bazında gösterim
    
    4. **✅ Ürün Durumu Kontrolü**
       - Pasif ürünleri otomatik çıkarma
       - İthal ürünler için farklı forward cover
    
    5. **🏪 Depo Bazlı Çıktı**
       - Her depo için ayrı sipariş listesi
       - Tedarikçi bazında gruplama
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 📐 Güncellenmiş Formül (DÜZELTİLDİ ✅)
```
    Net İhtiyaç = Brüt İhtiyaç - Açık Sipariş
    Brüt İhtiyaç = [(Satış × Genişletme × (Forward Cover + 2)] - [Mevcut Stoklar] + Karşılanamayan Min İhtiyaç
    
    Karşılanamayan Min İhtiyaç = MAX(0, Min Gerekli Stok - Mevcut Stoklar)
    
    Forward Cover Düzeltmesi:
    - İthal ürünler için: FC × 1.2
    - Yerli ürünler için: FC × 1.0
    
    Koli Yuvarlaması:
    Koli Sayısı = YUKARI_YUVARLA(Net İhtiyaç / Koli İçi)
    Final Miktar = Koli Sayısı × Koli İçi
```
    
    **⚠️ ÖNEMLİ DÜZELTME:** 
    Min sevkiyat artık direkt eklenmek yerine, sadece karşılanamayan minimum ihtiyaç kadar ekleniyor!
    """)

# ============================================
# 💵 ALIM SİPARİŞ HESAPLAMA
# ============================================
elif menu == "💵 Alım Sipariş Hesaplama":
    st.title("💵 Alım Sipariş Hesaplama")
    st.markdown("---")
    
    # Veri kontrolleri
    required_data = {
        "Anlık Stok/Satış": st.session_state.anlik_stok_satis,
        "Depo Stok": st.session_state.depo_stok,
        "KPI": st.session_state.kpi
    }
    
    missing_data = [name for name, data in required_data.items() if data is None]
    
    if missing_data:
        st.error(f"❌ Eksik veriler: {', '.join(missing_data)}")
        st.info("👉 Lütfen önce veri yükleme sayfasından gerekli verileri yükleyin.")
        st.stop()
    
    st.success("✅ Tüm gerekli veriler hazır!")
    
    # Opsiyonel veri bilgisi
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.session_state.po_yasak is not None:
            st.info("✅ PO Yasak aktif")
        else:
            st.warning("⚠️ PO Yasak yok")
    
    with col2:
        if st.session_state.po_detay_kpi is not None:
            st.info("✅ Detay KPI aktif")
        else:
            st.warning("⚠️ Detay KPI yok")
    
    with col3:
        if st.session_state.urun_master is not None:
            st.info("✅ Ürün Master aktif")
        else:
            st.warning("⚠️ Ürün Master yok")
    
    with col4:
        if st.session_state.sevkiyat_sonuc is not None:
            st.info("✅ Sevkiyat var")
        else:
            st.warning("⚠️ Sevkiyat yok")
    
    st.markdown("---")
    
    # Filtreler
    st.subheader("🎯 Hesaplama Filtreleri")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        cover_threshold = st.number_input(
            "Cover < X için hesapla",
            min_value=0,
            max_value=100,
            value=12,
            step=1,
            help="Sadece cover değeri X'ten küçük ürünler hesaplanır"
        )
    
    with col2:
        margin_threshold = st.number_input(
            "Brüt Kar Marjı > % Y için hesapla",
            min_value=-100.0,
            max_value=100.0,
            value=10.0,
            step=0.5,
            help="Sadece kar marjı %Y'den büyük ürünler hesaplanır"
        )
    
    with col3:
        use_detail_kpi = st.checkbox(
            "🎯 Detay KPI Kullan",
            value=st.session_state.po_detay_kpi is not None,
            disabled=st.session_state.po_detay_kpi is None,
            help="Marka+MG bazında özel hedefler kullanılır"
        )
    
    # İthal ürün faktörü
    col1, col2 = st.columns(2)
    
    with col1:
        ithal_factor = st.number_input(
            "İthal Ürün FC Çarpanı",
            min_value=1.0,
            max_value=2.0,
            value=1.2,
            step=0.05,
            help="İthal ürünler için forward cover bu katsayı ile çarpılır"
        )
    
    with col2:
        round_to_koli = st.checkbox(
            "📦 Koli Yuvarlaması Yap",
            value=True,
            help="Sipariş miktarlarını koli adedine yuvarla"
        )
    
    st.markdown("---")
    
    # Cover Segment Matrix
    st.subheader("📊 Cover Segment Genişletme Katsayıları")
    
    product_ranges = st.session_state.segmentation_params['product_ranges']
    cover_segments = [f"{int(r[0])}-{int(r[1]) if r[1] != float('inf') else 'inf'}" for r in product_ranges]
    
    def sort_segments(segments):
        def get_sort_key(seg):
            try:
                return int(seg.split('-')[0])
            except:
                return 9999
        return sorted(segments, key=get_sort_key)
    
    cover_segments_sorted = sort_segments(cover_segments)
    
    if 'cover_segment_matrix' not in st.session_state or st.session_state.cover_segment_matrix is None:
        st.session_state.cover_segment_matrix = pd.DataFrame({
            'cover_segment': cover_segments_sorted,
            'katsayi': [1.5, 1.3, 1.0, 0.8, 0.6, 0.4][:len(cover_segments_sorted)]
        })
    
    edited_cover_matrix = st.data_editor(
        st.session_state.cover_segment_matrix,
        width='stretch',
        hide_index=True,
        column_config={
            "cover_segment": st.column_config.TextColumn(
                "Cover Segment",
                disabled=True,
                width="medium"
            ),
            "katsayi": st.column_config.NumberColumn(
                "Genişletme Katsayısı",
                min_value=0.0,
                max_value=10.0,
                step=0.1,
                format="%.2f",
                required=True,
                width="medium"
            )
        }
    )
    
    if st.button("💾 Cover Segment Matrisini Kaydet"):
        st.session_state.cover_segment_matrix = edited_cover_matrix
        st.success("✅ Kaydedildi!")
    
    st.markdown("---")
    
    # HESAPLAMA
    if st.button("🚀 Alım Sipariş Hesapla", type="primary", width='stretch'):
        try:
            with st.spinner("📊 Hesaplama yapılıyor..."):
                
                # 1. VERİLERİ HAZIRLA
                anlik_df = st.session_state.anlik_stok_satis.copy()
                depo_df = st.session_state.depo_stok.copy()
                kpi_df = st.session_state.kpi.copy()
                cover_matrix = st.session_state.cover_segment_matrix.copy()
                
                # Debug bilgileri
                st.write("**📊 Veri Durumu:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Anlık Stok/Satış", f"{len(anlik_df):,} satır")
                with col2:
                    st.metric("Depo Stok", f"{len(depo_df):,} satır")
                with col3:
                    st.metric("KPI", f"{len(kpi_df)} satır")
                
                # Veri tiplerini düzelt
                anlik_df['urun_kod'] = anlik_df['urun_kod'].astype(str)
                depo_df['urun_kod'] = depo_df['urun_kod'].astype(str).apply(
                    lambda x: str(int(float(x))) if '.' in str(x) else str(x)
                )
                
                # 2. ÜRÜN MASTER VARSA EKLE - AD ALANLARI KALDIRILDI
                if st.session_state.urun_master is not None:
                    urun_master = st.session_state.urun_master.copy()
                    urun_master['urun_kod'] = urun_master['urun_kod'].astype(str)
                    
                    # Gerekli kolonları seç - AD ALANLARI YOK
                    master_cols = ['urun_kod']
                    if 'satici_kod' in urun_master.columns:
                        master_cols.append('satici_kod')
                    if 'mg' in urun_master.columns:
                        master_cols.append('mg')
                    if 'marka_kod' in urun_master.columns:
                        master_cols.append('marka_kod')
                    if 'durum' in urun_master.columns:
                        master_cols.append('durum')
                    if 'ithal' in urun_master.columns:
                        master_cols.append('ithal')
                    if 'koli_ici' in urun_master.columns:
                        master_cols.append('koli_ici')
                    
                    urun_master_subset = urun_master[master_cols].drop_duplicates('urun_kod')
                else:
                    urun_master_subset = None
                
                # 3. ÜRÜN BAZINDA TOPLAMA
                urun_toplam = anlik_df.groupby('urun_kod').agg({
                    'urun_kod': 'first',
                    'stok': 'sum',
                    'yol': 'sum',
                    'satis': 'sum',
                    'ciro': 'sum',
                    'smm': 'sum'
                }).reset_index(drop=True)
                
                st.write(f"**🏷️ Toplam ürün:** {len(urun_toplam):,}")
                
                # Ürün master'ı ekle
                if urun_master_subset is not None:
                    urun_toplam = urun_toplam.merge(urun_master_subset, on='urun_kod', how='left')
                    
                    # Durum kontrolü - Pasif ürünleri çıkar
                    if 'durum' in urun_toplam.columns:
                        aktif_sayisi = len(urun_toplam)
                        urun_toplam = urun_toplam[urun_toplam['durum'] != 'Pasif']
                        pasif_sayisi = aktif_sayisi - len(urun_toplam)
                        if pasif_sayisi > 0:
                            st.info(f"ℹ️ {pasif_sayisi} pasif ürün çıkarıldı")
                
                # 4. DEPO STOK EKLE
                depo_toplam = depo_df.groupby('urun_kod')['stok'].sum().reset_index()
                depo_toplam.columns = ['urun_kod', 'depo_stok']
                
                urun_toplam = urun_toplam.merge(depo_toplam, on='urun_kod', how='left')
                urun_toplam['depo_stok'] = urun_toplam['depo_stok'].fillna(0)
                
                # 5. PO YASAK KONTROLÜ
                if st.session_state.po_yasak is not None:
                    po_yasak = st.session_state.po_yasak.copy()
                    po_yasak['urun_kodu'] = po_yasak['urun_kodu'].astype(str)
                    
                    urun_toplam = urun_toplam.merge(
                        po_yasak[['urun_kodu', 'yasak_durum', 'acik_siparis']],
                        left_on='urun_kod',
                        right_on='urun_kodu',
                        how='left'
                    )
                    
                    urun_toplam['yasak_durum'] = urun_toplam['yasak_durum'].fillna(0)
                    urun_toplam['acik_siparis'] = urun_toplam['acik_siparis'].fillna(0)
                    
                    # Yasak ürünleri çıkar
                    yasak_sayisi = (urun_toplam['yasak_durum'] == 1).sum()
                    urun_toplam = urun_toplam[urun_toplam['yasak_durum'] != 1]
                    
                    if yasak_sayisi > 0:
                        st.warning(f"⚠️ {yasak_sayisi} yasak ürün çıkarıldı")
                else:
                    urun_toplam['acik_siparis'] = 0
                
                # 6. BRÜT KAR VE MARJ HESAPLA
                ortalama_smm = urun_toplam['smm'].mean()
                ortalama_ciro = urun_toplam['ciro'].mean()
                
                if ortalama_smm < ortalama_ciro * 0.1:
                    urun_toplam['toplam_smm'] = urun_toplam['smm'] * urun_toplam['satis']
                else:
                    urun_toplam['toplam_smm'] = urun_toplam['smm']
                
                urun_toplam['brut_kar'] = urun_toplam['ciro'] - urun_toplam['toplam_smm']
                urun_toplam['brut_kar_marji'] = np.where(
                    urun_toplam['ciro'] > 0,
                    (urun_toplam['brut_kar'] / urun_toplam['ciro'] * 100),
                    0
                )
                
                # 7. COVER HESAPLA
                urun_toplam['toplam_stok'] = (
                    urun_toplam['stok'] + 
                    urun_toplam['yol'] + 
                    urun_toplam['depo_stok']
                )
                
                urun_toplam['cover'] = np.where(
                    urun_toplam['satis'] > 0,
                    urun_toplam['toplam_stok'] / urun_toplam['satis'],
                    999
                )
                
                # 8. COVER SEGMENT ATAMASI
                product_ranges = st.session_state.segmentation_params['product_ranges']
                product_labels = [f"{int(r[0])}-{int(r[1]) if r[1] != float('inf') else 'inf'}" for r in product_ranges]
                
                urun_toplam['cover_segment'] = pd.cut(
                    urun_toplam['cover'],
                    bins=[r[0] for r in product_ranges] + [product_ranges[-1][1]],
                    labels=product_labels,
                    include_lowest=True
                )
                
                urun_toplam['cover_segment'] = urun_toplam['cover_segment'].astype(str)
                
                # 9. GENİŞLETME KATSAYISI
                urun_toplam = urun_toplam.merge(
                    cover_matrix.rename(columns={'katsayi': 'genlestirme_katsayisi'}),
                    on='cover_segment',
                    how='left'
                )
                urun_toplam['genlestirme_katsayisi'] = urun_toplam['genlestirme_katsayisi'].fillna(1.0)
                
                # 10. FORWARD COVER
                default_fc = kpi_df['forward_cover'].mean()
                urun_toplam['forward_cover'] = default_fc
                
                # Detay KPI varsa kullan
                if use_detail_kpi and st.session_state.po_detay_kpi is not None:
                    detay_kpi = st.session_state.po_detay_kpi.copy()
                    
                    # Marka ve MG kodları varsa join yap
                    if 'marka_kod' in urun_toplam.columns and 'mg' in urun_toplam.columns:
                        # MG kodu düzeltmesi
                        if 'mg_kod' in detay_kpi.columns:
                            detay_kpi.rename(columns={'mg_kod': 'mg'}, inplace=True)
                        
                        urun_toplam = urun_toplam.merge(
                            detay_kpi[['marka_kod', 'mg', 'cover_hedef', 'bkar_hedef']],
                            on=['marka_kod', 'mg'],
                            how='left'
                        )
                        
                        # Özel hedefler varsa kullan
                        urun_toplam['target_cover'] = urun_toplam['cover_hedef'].fillna(cover_threshold)
                        urun_toplam['target_margin'] = urun_toplam['bkar_hedef'].fillna(margin_threshold)
                        
                        detay_sayisi = urun_toplam['cover_hedef'].notna().sum()
                        if detay_sayisi > 0:
                            st.info(f"ℹ️ {detay_sayisi} ürün için özel hedefler uygulandı")
                    else:
                        urun_toplam['target_cover'] = cover_threshold
                        urun_toplam['target_margin'] = margin_threshold
                else:
                    urun_toplam['target_cover'] = cover_threshold
                    urun_toplam['target_margin'] = margin_threshold
                
                # İthal ürün faktörü
                if 'ithal' in urun_toplam.columns:
                    urun_toplam['forward_cover'] = np.where(
                        urun_toplam['ithal'] == 1,
                        urun_toplam['forward_cover'] * ithal_factor,
                        urun_toplam['forward_cover']
                    )
                    
                    ithal_sayisi = (urun_toplam['ithal'] == 1).sum()
                    if ithal_sayisi > 0:
                        st.info(f"ℹ️ {ithal_sayisi} ithal ürün için FC × {ithal_factor} uygulandı")
                
                # 11. MIN SEVK EKLE (KARŞILANAMAYAN MİNİMUM İHTİYAÇ) ✅ DÜZELTİLDİ
                if st.session_state.sevkiyat_sonuc is not None:
                    sevk_df = st.session_state.sevkiyat_sonuc.copy()
                    sevk_df['urun_kod'] = sevk_df['urun_kod'].astype(str)
                    
                    # Minimum gerekli stok seviyesi
                    min_sevk = sevk_df.groupby('urun_kod')['sevkiyat_miktari'].sum().reset_index()
                    min_sevk.columns = ['urun_kod', 'min_gerekli_stok']
                    
                    urun_toplam = urun_toplam.merge(min_sevk, on='urun_kod', how='left')
                    urun_toplam['min_gerekli_stok'] = urun_toplam['min_gerekli_stok'].fillna(0)
                    
                    # Mevcut stokları hesapla (cover hesabında kullanılan toplam_stok)
                    urun_toplam['mevcut_stok'] = urun_toplam['toplam_stok']
                    
                    # Karşılanamayan minimum ihtiyacı hesapla
                    # Sadece mevcut stokların minimum gerekli stoku karşılayamadığı miktar
                    urun_toplam['karsilanamayan_min'] = np.maximum(
                        0,
                        urun_toplam['min_gerekli_stok'] - urun_toplam['mevcut_stok']
                    )
                    
                    # Debug bilgisi için min_sevk_adeti kolonunu da koruyalım
                    urun_toplam['min_sevk_adeti'] = urun_toplam['min_gerekli_stok']
                    
                    # Karşılanamayan miktar bilgisini göster
                    karsilanamayan_toplam = urun_toplam['karsilanamayan_min'].sum()
                    min_gerekli_toplam = urun_toplam['min_gerekli_stok'].sum()
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📦 Min Gerekli Stok", f"{min_gerekli_toplam:,.0f} adet")
                    with col2:
                        st.metric("📊 Mevcut Stoklar", f"{urun_toplam['mevcut_stok'].sum():,.0f} adet")
                    with col3:
                        st.metric("❗ Karşılanamayan", f"{karsilanamayan_toplam:,.0f} adet")
                    
                    if karsilanamayan_toplam > 0:
                        karsilanamayan_yuzde = (karsilanamayan_toplam / min_gerekli_toplam * 100) if min_gerekli_toplam > 0 else 0
                        st.info(f"📦 Toplam minimum ihtiyacın %{karsilanamayan_yuzde:.1f}'i karşılanamıyor ve siparişe eklenecek")
                else:
                    urun_toplam['min_gerekli_stok'] = 0
                    urun_toplam['karsilanamayan_min'] = 0
                    urun_toplam['min_sevk_adeti'] = 0
                    urun_toplam['mevcut_stok'] = urun_toplam['toplam_stok']
                
                # 12. FİLTRELERİ UYGULA
                urun_toplam['filtre_uygun'] = (
                    (urun_toplam['cover'] < urun_toplam['target_cover']) &
                    (urun_toplam['brut_kar_marji'] > urun_toplam['target_margin'])
                )
                
                filtre_sayisi = urun_toplam['filtre_uygun'].sum()
                st.write(f"**✅ Filtreye uygun:** {filtre_sayisi} ürün")
                
                # 13. ALIM SİPARİŞ HESAPLA (DÜZELTİLMİŞ FORMÜL) ✅
                urun_toplam['talep'] = (
                    urun_toplam['satis'] * 
                    urun_toplam['genlestirme_katsayisi'] * 
                    (urun_toplam['forward_cover'] + 2)
                )
                
                # Brüt ihtiyaç - DÜZELTİLMİŞ FORMÜL
                urun_toplam['brut_ihtiyac'] = (
                    urun_toplam['talep'] - 
                    urun_toplam['mevcut_stok'] + 
                    urun_toplam['karsilanamayan_min']  # ✅ Sadece karşılanamayan miktar ekleniyor
                )
                
                # ESKİ VE YENİ HESAPLAMA KARŞILAŞTIRMASI (DEBUG)
                if st.session_state.sevkiyat_sonuc is not None:
                    # Eski formülle hesaplama (karşılaştırma için)
                    urun_toplam['brut_ihtiyac_eski'] = (
                        urun_toplam['talep'] - 
                        urun_toplam['mevcut_stok'] + 
                        urun_toplam['min_sevk_adeti']  # Eski: tüm min sevkiyat eklenirdi
                    )
                    
                    fark_toplam = (urun_toplam['brut_ihtiyac_eski'] - urun_toplam['brut_ihtiyac']).sum()
                    if fark_toplam > 0:
                        st.success(f"✅ Yeni formül ile {fark_toplam:,.0f} adet gereksiz sipariş önlendi!")
                        
                        with st.expander("📊 Formül Karşılaştırması"):
                            karsilastirma_df = urun_toplam[
                                (urun_toplam['min_gerekli_stok'] > 0) & 
                                (urun_toplam['karsilanamayan_min'] < urun_toplam['min_sevk_adeti'])
                            ][['urun_kod', 'mevcut_stok', 'min_gerekli_stok', 'karsilanamayan_min', 'brut_ihtiyac_eski', 'brut_ihtiyac']].head(10)
                            
                            if len(karsilastirma_df) > 0:
                                karsilastirma_df['tasarruf'] = karsilastirma_df['brut_ihtiyac_eski'] - karsilastirma_df['brut_ihtiyac']
                                st.dataframe(karsilastirma_df, width='stretch')
                
                # Net ihtiyaç (açık siparişleri düş)
                urun_toplam['net_ihtiyac'] = urun_toplam['brut_ihtiyac'] - urun_toplam['acik_siparis']
                
                # Sadece filtreye uygun ve pozitif olanlar
                urun_toplam['alim_siparis'] = np.where(
                    (urun_toplam['filtre_uygun']) & (urun_toplam['net_ihtiyac'] > 0),
                    urun_toplam['net_ihtiyac'],
                    0
                )
                
                # 14. KOLİ YUVARLAMASI
                if round_to_koli and 'koli_ici' in urun_toplam.columns:
                    urun_toplam['koli_ici'] = pd.to_numeric(urun_toplam['koli_ici'], errors='coerce').fillna(1)
                    
                    # Koli sayısını hesapla
                    urun_toplam['alim_koli'] = np.where(
                        (urun_toplam['alim_siparis'] > 0) & (urun_toplam['koli_ici'] > 0),
                        np.ceil(urun_toplam['alim_siparis'] / urun_toplam['koli_ici']),
                        0
                    )
                    
                    # Yuvarlanmış adet
                    urun_toplam['alim_siparis_yuvarli'] = urun_toplam['alim_koli'] * urun_toplam['koli_ici']
                    
                    # Orijinal ile fark
                    yuvarlama_farki = (urun_toplam['alim_siparis_yuvarli'] - urun_toplam['alim_siparis']).sum()
                    if yuvarlama_farki > 0:
                        st.info(f"📦 Koli yuvarlaması ile +{yuvarlama_farki:,.0f} adet eklendi")
                    
                    # Yuvarlanmış değeri kullan
                    urun_toplam['alim_siparis_final'] = urun_toplam['alim_siparis_yuvarli']
                else:
                    urun_toplam['alim_siparis_final'] = urun_toplam['alim_siparis']
                    urun_toplam['alim_koli'] = 0
                    if 'koli_ici' not in urun_toplam.columns:
                        urun_toplam['koli_ici'] = 1
                
                # Depo kodu ekle (varsa)
                if 'depo_kod' in depo_df.columns:
                    depo_urun = depo_df[['urun_kod', 'depo_kod']].drop_duplicates()
                    urun_toplam = urun_toplam.merge(depo_urun, on='urun_kod', how='left')
                
                # 15. SONUÇLARI KAYDET
                st.session_state.alim_siparis_sonuc = urun_toplam.copy()
                
                st.success("✅ Alım sipariş hesaplaması tamamlandı!")
                st.balloons()
                
                # ÖZET METRİKLER
                st.markdown("---")
                st.subheader("📊 Sonuç Özeti")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    toplam_alim = urun_toplam['alim_siparis_final'].sum()
                    st.metric("📦 Toplam Alım", f"{toplam_alim:,.0f} adet")
                
                with col2:
                    alim_sku = (urun_toplam['alim_siparis_final'] > 0).sum()
                    st.metric("🏷️ Alım Gereken SKU", f"{alim_sku}")
                
                with col3:
                    if 'alim_koli' in urun_toplam.columns:
                        toplam_koli = urun_toplam['alim_koli'].sum()
                        st.metric("📦 Toplam Koli", f"{toplam_koli:,.0f}")
                
                with col4:
                    if 'acik_siparis' in urun_toplam.columns:
                        toplam_acik = urun_toplam['acik_siparis'].sum()
                        st.metric("📋 Açık Sipariş", f"{toplam_acik:,.0f}")
                
                # DETAYLI TABLO - AD ALANLARI KALDIRILDI
                st.markdown("---")
                st.subheader("📋 Alım Sipariş Detayı")
                
                # Sadece pozitif olanları göster
                pozitif_df = urun_toplam[urun_toplam['alim_siparis_final'] > 0].copy()
                
                if len(pozitif_df) > 0:
                    # Gösterilecek kolonları seç - AD ALANLARI YOK
                    display_cols = ['urun_kod', 'cover_segment', 'cover', 'brut_kar_marji', 
                                    'satis', 'toplam_stok']
                    
                    # Yeni eklenen kolonlar
                    if 'min_gerekli_stok' in pozitif_df.columns:
                        display_cols.append('min_gerekli_stok')
                    
                    if 'karsilanamayan_min' in pozitif_df.columns:
                        display_cols.append('karsilanamayan_min')
                    
                    if 'acik_siparis' in pozitif_df.columns:
                        display_cols.append('acik_siparis')
                    
                    display_cols.append('alim_siparis_final')
                    
                    if 'koli_ici' in pozitif_df.columns:
                        display_cols.extend(['koli_ici', 'alim_koli'])
                    
                    if 'satici_kod' in pozitif_df.columns:
                        display_cols.append('satici_kod')
                    
                    if 'depo_kod' in pozitif_df.columns:
                        display_cols.append('depo_kod')
                    
                    display_df = pozitif_df[display_cols].sort_values('alim_siparis_final', ascending=False)
                    
                    # Format için sütun isimleri
                    format_dict = {
                        'cover': '{:.2f}',
                        'brut_kar_marji': '{:.2f}%',
                        'satis': '{:,.0f}',
                        'toplam_stok': '{:,.0f}',
                        'min_gerekli_stok': '{:,.0f}',
                        'karsilanamayan_min': '{:,.0f}',
                        'acik_siparis': '{:,.0f}',
                        'alim_siparis_final': '{:,.0f}',
                        'koli_ici': '{:.0f}',
                        'alim_koli': '{:,.0f}'
                    }
                    
                    # Sadece mevcut sütunları formatla
                    format_dict = {k: v for k, v in format_dict.items() if k in display_df.columns}
                    
                    st.dataframe(
                        display_df.style.format(format_dict),
                        width='stretch',
                        height=400
                    )
                    
                    # Export butonları
                    st.markdown("---")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        csv_data = display_df.to_csv(index=False, encoding='utf-8-sig')
                        st.download_button(
                            label="📥 CSV İndir",
                            data=csv_data,
                            file_name=f"alim_siparis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv",
                            width='stretch'
                        )
                    
                    with col2:
                        if st.button("📊 Depo Bazlı Görünüme Git", width='stretch'):
                            st.switch_page("pages/4_PO.py")  # Aynı sayfada menü değiştir
                
                else:
                    st.warning("⚠️ Filtrelere uygun ürün bulunamadı!")
        
        except Exception as e:
            st.error(f"❌ Hata oluştu: {str(e)}")
            import traceback
            st.code(traceback.format_exc())

# ============================================
# 📊 ALIM SİPARİŞ RAPORLARI
# ============================================
elif menu == "📊 Alım Sipariş Raporları":
    st.title("📊 Alım Sipariş Raporları")
    st.markdown("---")
    
    if st.session_state.alim_siparis_sonuc is None:
        st.warning("⚠️ Henüz alım sipariş hesaplaması yapılmadı!")
        st.info("Lütfen önce 'Alım Sipariş Hesaplama' menüsünden hesaplama yapın.")
        st.stop()
    
    sonuc_df = st.session_state.alim_siparis_sonuc.copy()
    
    # Final sütunu varsa kullan, yoksa normal alim_siparis kullan
    if 'alim_siparis_final' in sonuc_df.columns:
        alim_column = 'alim_siparis_final'
    else:
        alim_column = 'alim_siparis'
    
    # Sadece alım > 0 olanlar
    alim_df = sonuc_df[sonuc_df[alim_column] > 0].copy()
    
    if len(alim_df) == 0:
        st.info("ℹ️ Alım sipariş ihtiyacı olan ürün bulunamadı.")
        st.stop()
    
    # Genel özet
    st.subheader("📈 Genel Özet")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Toplam Alım", f"{alim_df[alim_column].sum():,.0f}")
    
    with col2:
        st.metric("🏷️ Ürün Sayısı", f"{len(alim_df)}")
    
    with col3:
        if 'alim_koli' in alim_df.columns:
            st.metric("📦 Toplam Koli", f"{alim_df['alim_koli'].sum():,.0f}")
    
    with col4:
        if 'acik_siparis' in alim_df.columns:
            acik_dusülen = alim_df['acik_siparis'].sum()
            st.metric("📋 Açık Sipariş Düşüldü", f"{acik_dusülen:,.0f}")
    
    # Yeni formül metrikleri
    if 'karsilanamayan_min' in alim_df.columns:
        st.markdown("---")
        st.subheader("📊 Min İhtiyaç Analizi")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_gerekli = alim_df['min_gerekli_stok'].sum() if 'min_gerekli_stok' in alim_df.columns else 0
            st.metric("📦 Toplam Min Gerekli", f"{min_gerekli:,.0f}")
        
        with col2:
            karsilanamayan = alim_df['karsilanamayan_min'].sum()
            st.metric("❗ Karşılanamayan", f"{karsilanamayan:,.0f}")
        
        with col3:
            if min_gerekli > 0:
                karsilanma_orani = ((min_gerekli - karsilanamayan) / min_gerekli * 100)
                st.metric("✅ Karşılanma Oranı", f"%{karsilanma_orani:.1f}")
    
    st.markdown("---")
    
    # Tab'lar
    tabs = ["🎯 Segment Analizi", "💰 Karlılık Analizi", "📦 Tedarikçi Analizi", "🏪 Depo Analizi"]
    tab1, tab2, tab3, tab4 = st.tabs(tabs)
    
    # SEGMENT ANALİZİ
    with tab1:
        st.subheader("🎯 Cover Segment Bazında Analiz")
        
        segment_analiz = alim_df.groupby('cover_segment').agg({
            'urun_kod': 'count',
            alim_column: 'sum',
            'satis': 'sum',
            'brut_kar': 'sum'
        }).reset_index()
        
        segment_analiz.columns = ['Cover Segment', 'Ürün Sayısı', 'Toplam Alım', 'Toplam Satış', 'Toplam Brüt Kar']
        
        # Sırala
        segment_analiz['sort_key'] = segment_analiz['Cover Segment'].apply(
            lambda x: int(x.split('-')[0]) if x.split('-')[0].isdigit() else 9999
        )
        segment_analiz = segment_analiz.sort_values('sort_key').drop('sort_key', axis=1)
        
        segment_analiz['Alım Payı %'] = (segment_analiz['Toplam Alım'] / segment_analiz['Toplam Alım'].sum() * 100).round(2)
        
        st.dataframe(
            segment_analiz.style.format({
                'Ürün Sayısı': '{:.0f}',
                'Toplam Alım': '{:,.0f}',
                'Toplam Satış': '{:,.0f}',
                'Toplam Brüt Kar': '{:,.2f}',
                'Alım Payı %': '{:.1f}%'
            }),
            width='stretch'
        )
    
    # KARLILIK ANALİZİ
    with tab2:
        st.subheader("💰 Kar Marjı Bazında Analiz")
        
        # Marj kategorileri
        alim_df['marj_kategori'] = pd.cut(
            alim_df['brut_kar_marji'],
            bins=[-np.inf, 0, 10, 20, 30, 50, np.inf],
            labels=['Negatif', '%0-10', '%10-20', '%20-30', '%30-50', '%50+']
        )
        
        marj_analiz = alim_df.groupby('marj_kategori').agg({
            'urun_kod': 'count',
            alim_column: 'sum',
            'brut_kar': 'sum'
        }).reset_index()
        
        marj_analiz.columns = ['Marj Kategorisi', 'Ürün Sayısı', 'Toplam Alım', 'Toplam Brüt Kar']
        
        st.dataframe(
            marj_analiz.style.format({
                'Ürün Sayısı': '{:.0f}',
                'Toplam Alım': '{:,.0f}',
                'Toplam Brüt Kar': '{:,.2f}'
            }),
            width='stretch'
        )
    
    # TEDARİKÇİ ANALİZİ - AD ALANLARI KALDIRILDI
    with tab3:
        if 'satici_kod' in alim_df.columns:
            st.subheader("📦 Tedarikçi Bazında Analiz")
            
            tedarikci_analiz = alim_df.groupby(['satici_kod']).agg({
                'urun_kod': 'count',
                alim_column: 'sum'
            }).reset_index()
            
            tedarikci_analiz.columns = ['Tedarikçi Kod', 'Ürün Sayısı', 'Toplam Alım']
            tedarikci_analiz = tedarikci_analiz.sort_values('Toplam Alım', ascending=False)
            
            # Koli bilgisi varsa ekle
            if 'alim_koli' in alim_df.columns:
                koli_analiz = alim_df.groupby(['satici_kod'])['alim_koli'].sum().reset_index()
                tedarikci_analiz = tedarikci_analiz.merge(koli_analiz, on='satici_kod', how='left')
                tedarikci_analiz.rename(columns={'alim_koli': 'Toplam Koli'}, inplace=True)
            
            st.dataframe(
                tedarikci_analiz.style.format({
                    'Ürün Sayısı': '{:.0f}',
                    'Toplam Alım': '{:,.0f}',
                    'Toplam Koli': '{:,.0f}' if 'Toplam Koli' in tedarikci_analiz.columns else None
                }),
                width='stretch'
            )
        else:
            st.info("ℹ️ Tedarikçi bilgisi bulunamadı (Ürün Master'da satici_kod yok)")
    
    # DEPO ANALİZİ
    with tab4:
        if 'depo_kod' in alim_df.columns:
            st.subheader("🏪 Depo Bazında Analiz")
            
            depo_analiz = alim_df.groupby(['depo_kod']).agg({
                'urun_kod': 'count',
                alim_column: 'sum'
            }).reset_index()
            
            depo_analiz.columns = ['Depo Kod', 'Ürün Sayısı', 'Toplam Alım']
            
            # Koli bilgisi varsa ekle
            if 'alim_koli' in alim_df.columns:
                depo_koli = alim_df.groupby(['depo_kod'])['alim_koli'].sum().reset_index()
                depo_analiz = depo_analiz.merge(depo_koli, on='depo_kod', how='left')
                depo_analiz.rename(columns={'alim_koli': 'Toplam Koli'}, inplace=True)
            
            depo_analiz = depo_analiz.sort_values('Toplam Alım', ascending=False)
            
            st.dataframe(
                depo_analiz.style.format({
                    'Ürün Sayısı': '{:.0f}',
                    'Toplam Alım': '{:,.0f}',
                    'Toplam Koli': '{:,.0f}' if 'Toplam Koli' in depo_analiz.columns else None
                }),
                width='stretch'
            )
        else:
            st.info("ℹ️ Depo bilgisi bulunamadı")

# ============================================
# 📦 DEPO BAZLI SİPARİŞ - AD ALANLARI KALDIRILDI
# ============================================
elif menu == "📦 Depo Bazlı Sipariş":
    st.title("📦 Depo Bazlı Sipariş Listeleri")
    st.markdown("---")
    
    if st.session_state.alim_siparis_sonuc is None:
        st.warning("⚠️ Henüz alım sipariş hesaplaması yapılmadı!")
        st.info("Lütfen önce 'Alım Sipariş Hesaplama' menüsünden hesaplama yapın.")
        st.stop()
    
    sonuc_df = st.session_state.alim_siparis_sonuc.copy()
    
    # Final sütunu varsa kullan
    if 'alim_siparis_final' in sonuc_df.columns:
        alim_column = 'alim_siparis_final'
    else:
        alim_column = 'alim_siparis'
    
    # Pozitif alımları filtrele
    alim_df = sonuc_df[sonuc_df[alim_column] > 0].copy()
    
    if len(alim_df) == 0:
        st.info("ℹ️ Alım sipariş ihtiyacı olan ürün bulunamadı.")
        st.stop()
    
    # Depo kodu yoksa default ata
    if 'depo_kod' not in alim_df.columns:
        alim_df['depo_kod'] = 'D001'
        st.info("ℹ️ Depo kodu bulunamadı, tüm siparişler D001 olarak gösteriliyor")
    
    # Depo seçimi
    depo_listesi = sorted(alim_df['depo_kod'].dropna().unique())
    
    col1, col2 = st.columns([2, 3])
    with col1:
        selected_depo = st.selectbox(
            "📍 Depo Seçin",
            options=['Tümü'] + depo_listesi,
            key="depo_select"
        )
    
    # Seçili depoya göre filtrele
    if selected_depo != 'Tümü':
        display_df = alim_df[alim_df['depo_kod'] == selected_depo].copy()
        st.subheader(f"📦 {selected_depo} Deposu Sipariş Listesi")
    else:
        display_df = alim_df.copy()
        st.subheader("📦 Tüm Depolar Sipariş Listesi")
    
    # Özet metrikler
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        toplam_adet = display_df[alim_column].sum()
        st.metric("📦 Toplam Adet", f"{toplam_adet:,.0f}")
    
    with col2:
        urun_sayisi = len(display_df)
        st.metric("🏷️ Ürün Sayısı", f"{urun_sayisi}")
    
    with col3:
        if 'alim_koli' in display_df.columns:
            toplam_koli = display_df['alim_koli'].sum()
            st.metric("📦 Toplam Koli", f"{toplam_koli:,.0f}")
    
    with col4:
        if 'satici_kod' in display_df.columns:
            tedarikci_sayisi = display_df['satici_kod'].nunique()
            st.metric("👥 Tedarikçi Sayısı", f"{tedarikci_sayisi}")
    
    st.markdown("---")
    
    # Tedarikçi filtresi (varsa)
    if 'satici_kod' in display_df.columns:
        col1, col2 = st.columns([2, 3])
        with col1:
            tedarikci_list = ['Tümü'] + sorted(display_df['satici_kod'].dropna().unique())
            selected_tedarikci = st.selectbox(
                "👥 Tedarikçi Filtresi",
                options=tedarikci_list,
                key="tedarikci_filter"
            )
        
        if selected_tedarikci != 'Tümü':
            display_df = display_df[display_df['satici_kod'] == selected_tedarikci]
            st.info(f"Filtre: {selected_tedarikci}")
    
    # Detaylı tablo
    st.subheader("📋 Sipariş Detayı")
    
    # Gösterilecek sütunları belirle - AD ALANLARI YOK
    display_cols = ['urun_kod']
    
    if 'satici_kod' in display_df.columns:
        display_cols.append('satici_kod')
    
    display_cols.append(alim_column)
    
    if 'koli_ici' in display_df.columns:
        display_cols.append('koli_ici')
    
    if 'alim_koli' in display_df.columns:
        display_cols.append('alim_koli')
    
    # Yeni eklenen kolonlar
    if 'karsilanamayan_min' in display_df.columns:
        display_cols.append('karsilanamayan_min')
    
    display_cols.extend(['cover', 'brut_kar_marji', 'satis'])
    
    if 'depo_kod' in display_df.columns and selected_depo == 'Tümü':
        display_cols.append('depo_kod')
    
    # Sadece mevcut sütunları göster
    display_cols = [col for col in display_cols if col in display_df.columns]
    
    final_df = display_df[display_cols].sort_values(alim_column, ascending=False)
    
    # Sütun isimlerini düzenle
    column_rename = {
        'urun_kod': 'Ürün Kodu',
        'satici_kod': 'Tedarikçi Kod',
        alim_column: 'Alım (Adet)',
        'koli_ici': 'Koli İçi',
        'alim_koli': 'Alım (Koli)',
        'karsilanamayan_min': 'Karşılanamayan Min',
        'cover': 'Cover',
        'brut_kar_marji': 'Kar Marjı %',
        'satis': 'Satış',
        'depo_kod': 'Depo'
    }
    
    final_df = final_df.rename(columns=column_rename)
    
    # Formatla ve göster
    format_dict = {
        'Alım (Adet)': '{:,.0f}',
        'Koli İçi': '{:.0f}',
        'Alım (Koli)': '{:,.0f}',
        'Karşılanamayan Min': '{:,.0f}',
        'Cover': '{:.2f}',
        'Kar Marjı %': '{:.2f}%',
        'Satış': '{:,.0f}'
    }
    
    # Sadece mevcut sütunları formatla
    format_dict = {k: v for k, v in format_dict.items() if k in final_df.columns}
    
    st.dataframe(
        final_df.style.format(format_dict),
        width='stretch',
        height=500
    )
    
    # Export
    st.markdown("---")
    st.subheader("📥 Dışa Aktar")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Mevcut görünümü indir
        csv_data = final_df.to_csv(index=False, encoding='utf-8-sig')
        filename = f"siparis_{selected_depo}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv"
        
        st.download_button(
            label="📥 Bu Listeyi İndir (CSV)",
            data=csv_data,
            file_name=filename,
            mime="text/csv",
            width='stretch'
        )
    
    with col2:
        # Özet rapor
        if 'satici_kod' in display_df.columns:
            ozet_df = display_df.groupby(['satici_kod']).agg({
                alim_column: 'sum',
                'urun_kod': 'count'
            }).reset_index()
            
            if 'alim_koli' in display_df.columns:
                koli_ozet = display_df.groupby(['satici_kod'])['alim_koli'].sum().reset_index()
                ozet_df = ozet_df.merge(koli_ozet, on='satici_kod', how='left')
            
            ozet_df.columns = ['Tedarikçi'] + ['Toplam Adet', 'SKU Sayısı'] + (['Toplam Koli'] if 'alim_koli' in display_df.columns else [])
            
            csv_ozet = ozet_df.to_csv(index=False, encoding='utf-8-sig')
            
            st.download_button(
                label="📥 Özet Rapor (CSV)",
                data=csv_ozet,
                file_name=f"ozet_{selected_depo}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                width='stretch'
            )
    
    with col3:
        # Tüm depoları indir
        if selected_depo != 'Tümü':
            tum_csv = alim_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 Tüm Depolar (CSV)",
                data=tum_csv,
                file_name=f"tum_depolar_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                width='stretch'
            )



