import streamlit as st
import pandas as pd
import numpy as np
import time

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
    ["🏠 Ana Sayfa", "💵 Alım Sipariş Hesaplama", "📊 Alım Sipariş Raporları"]
)

# ============================================
# 🏠 ANA SAYFA
# ============================================
if menu == "🏠 Ana Sayfa":
    st.title("💵 Alım Sipariş (Purchase Order) Sistemi")
    st.markdown("---")
    
    # VERİ KONTROLÜ - ÖNEMLİ!
    required_data = {
        "Anlık Stok/Satış": st.session_state.anlik_stok_satis,
        "Depo Stok": st.session_state.depo_stok,
        "KPI": st.session_state.kpi
    }
    
    missing_data = [name for name, data in required_data.items() if data is None]
    
    if missing_data:
        st.error("❌ Gerekli veriler yüklenmemiş!")
        st.warning(f"**Eksik veriler:** {', '.join(missing_data)}")
        
        st.info("""
        **👉 Lütfen önce veri yükleme sayfasından CSV dosyalarınızı yükleyin.**
        
        Gerekli dosyalar:
        - Anlık Stok/Satış
        - Depo Stok
        - KPI
        - Ürün Master (opsiyonel ama önerilir)
        - Mağaza Master (opsiyonel ama önerilir)
        """)
        
        if st.button("➡️ Veri Yükleme Sayfasına Git", type="primary", use_container_width=True):
            st.switch_page("pages/0_Veri_Yukleme.py")
        
        st.stop()
    
    # Sevkiyat kontrolü (opsiyonel)
    if st.session_state.sevkiyat_sonuc is None:
        st.warning("""
        ⚠️ **Sevkiyat hesaplaması yapılmamış!**
        
        Alım sipariş hesaplaması için sevkiyat sonuçları kullanılır (min sevkiyat miktarı için).
        Sevkiyat yapmadan da devam edebilirsiniz, ancak sonuçlar daha az optimize olabilir.
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚚 Sevkiyat Hesaplamaya Git", use_container_width=True):
                st.switch_page("pages/2_Sevkiyat.py")
        with col2:
            st.info("veya aşağıdaki bilgileri okuyun")
    
    st.markdown("""
    ### 🎯 Alım Sipariş Sistemi Hakkında
    
    Bu sistem, depodan mağazalara yapılan sevkiyat sonrasında **tedarikçiden alınması gereken ürün miktarlarını** hesaplar.
    
    **Hesaplama Mantığı:**
    1. Cover < X olan ürünler (düşük stok seviyesi)
    2. Brüt Kar Marjı > %Y olan ürünler (karlı ürünler)
    3. Satış trendine göre genişletme katsayısı
    4. Forward cover hedefi
    5. Minimum sevkiyat miktarı
    
    **Formül:**
    ```
    Alım İhtiyacı = [(Satış × Genişletme × (Forward Cover + 2)] - [Stok + Yol + Depo Stok] + Min Sevkiyat
    ```
    """)
    
    st.markdown("---")
    
    st.markdown("### 📋 İşlem Adımları")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **1️⃣ Veri Hazırlığı** (Sevkiyat sayfasından)
        - Veri Yükleme
        - Segmentasyon
        - Sevkiyat Hesaplama
        """)
        
        st.success("""
        **2️⃣ Alım Sipariş Hesaplama**
        - Filtreleri ayarlama
        - Cover segment matrix
        - Hesaplama çalıştırma
        """)
    
    with col2:
        st.success("""
        **3️⃣ Sonuçları İnceleme**
        - Ürün bazında analiz
        - Segment analizi
        - Top performans raporları
        """)
        
        st.info("""
        **4️⃣ Export**
        - CSV indirme
        - Excel export
        - Tedarikçiye gönderim
        """)
    
    st.markdown("---")
    
    # Veri durumu kontrolü
    st.subheader("📊 Veri Durumu")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.session_state.anlik_stok_satis is not None:
            st.success("✅ Anlık Stok/Satış")
        else:
            st.error("❌ Anlık Stok/Satış")
    
    with col2:
        if st.session_state.depo_stok is not None:
            st.success("✅ Depo Stok")
        else:
            st.error("❌ Depo Stok")
    
    with col3:
        if st.session_state.kpi is not None:
            st.success("✅ KPI")
        else:
            st.error("❌ KPI")
    
    with col4:
        if st.session_state.sevkiyat_sonuc is not None:
            st.success("✅ Sevkiyat Hesabı")
        else:
            st.warning("⚠️ Sevkiyat Hesabı")
    
    st.markdown("---")
    
    if st.session_state.alim_siparis_sonuc is not None:
        st.success("✅ Alım sipariş hesaplaması mevcut!")
        
        result = st.session_state.alim_siparis_sonuc
        
        col1, col2, col3 = st.columns(3)
        with col1:
            toplam_alim = result['alim_siparis'].sum()
            st.metric("📦 Toplam Alım Sipariş", f"{toplam_alim:,.0f}")
        
        with col2:
            alim_sku = (result['alim_siparis'] > 0).sum()
            st.metric("🏷️ Alım Gereken SKU", f"{alim_sku}")
        
        with col3:
            if alim_sku > 0:
                ort_alim = toplam_alim / alim_sku
                st.metric("📊 Ort. Alım/SKU", f"{ort_alim:,.0f}")

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
        
        if st.button("➡️ Veri Yükleme Sayfasına Git", type="primary"):
            st.switch_page("pages/0_Veri_Yukleme.py")
        
        st.stop()
    
    # Depo stok kontrolü
    if len(st.session_state.depo_stok) == 0:
        st.error("❌ Depo Stok verisi boş! Lütfen depo_stok.csv dosyasını yükleyin.")
        st.stop()
    
    st.success("✅ Tüm gerekli veriler hazır!")
    
    st.markdown("---")
    
    # Filtreler
    st.subheader("🎯 Hesaplama Filtreleri")
    
    col1, col2 = st.columns(2)
    
    with col1:
        cover_threshold = st.number_input(
            "Cover < X için hesapla",
            min_value=0,
            max_value=100,
            value=12,
            step=1,
            help="Örnek: 12 girersek Cover < 12 olan ürünler hesaplanır"
        )
    
    with col2:
        margin_threshold = st.number_input(
            "Brüt Kar Marjı > % Y için hesapla",
            min_value=-100.0,
            max_value=100.0,
            value=10.0,
            step=0.5,
            help="Negatif değer girebilirsiniz. Örnek: 10 girersek Marj > %10 olanlar hesaplanır"
        )
    
    st.markdown("---")
    
    # 5. Matris - Cover Segment Katsayıları
    st.subheader("📊 Cover Segment Genişletme Katsayıları")
    
    # Segmentasyon parametrelerini al
    product_ranges = st.session_state.segmentation_params['product_ranges']
    
    # Cover segmentlerini oluştur
    cover_segments = [f"{int(r[0])}-{int(r[1]) if r[1] != float('inf') else 'inf'}" for r in product_ranges]
    
    # Segment sıralama fonksiyonu
    def sort_segments(segments):
        def get_sort_key(seg):
            try:
                return int(seg.split('-')[0])
            except:
                return 9999
        return sorted(segments, key=get_sort_key)
    
    cover_segments_sorted = sort_segments(cover_segments)
    
    if 'cover_segment_matrix' not in st.session_state or st.session_state.cover_segment_matrix is None:
        # Default katsayı tablosu
        st.session_state.cover_segment_matrix = pd.DataFrame({
            'cover_segment': cover_segments_sorted,
            'katsayi': [1.0] * len(cover_segments_sorted)
        })
    else:
        # Mevcut matrisi güncelle - yeni segmentler eklenmişse
        existing_df = st.session_state.cover_segment_matrix.copy()
        existing_segments = set(existing_df['cover_segment'].tolist())
        
        # Yeni segmentleri ekle
        for seg in cover_segments_sorted:
            if seg not in existing_segments:
                new_row = pd.DataFrame({'cover_segment': [seg], 'katsayi': [1.0]})
                existing_df = pd.concat([existing_df, new_row], ignore_index=True)
        
        # Sadece mevcut segmentleri tut
        existing_df = existing_df[existing_df['cover_segment'].isin(cover_segments_sorted)]
        
        # Sırala
        existing_df['sort_key'] = existing_df['cover_segment'].apply(
            lambda x: int(x.split('-')[0]) if x.split('-')[0].isdigit() else 9999
        )
        existing_df = existing_df.sort_values('sort_key').drop('sort_key', axis=1).reset_index(drop=True)
        
        st.session_state.cover_segment_matrix = existing_df
    
    edited_cover_matrix = st.data_editor(
        st.session_state.cover_segment_matrix,
        use_container_width=True,
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
    
    if st.button("🚀 Alım Sipariş Hesapla", type="primary", use_container_width=True):
        try:
            with st.spinner("📊 Hesaplama yapılıyor..."):
                
                # 1. VERİLERİ HAZIRLA
                anlik_df = st.session_state.anlik_stok_satis.copy()
                depo_df = st.session_state.depo_stok.copy()
                kpi_df = st.session_state.kpi.copy()
                cover_matrix = st.session_state.cover_segment_matrix.copy()
                
                st.write("**📊 Debug: Veri boyutları**")
                st.write(f"- Anlık Stok/Satış: {len(anlik_df):,} satır")
                st.write(f"- Depo Stok: {len(depo_df):,} satır")
                st.write(f"- KPI: {len(kpi_df)} satır")
                st.write(f"- Cover Segment Matrix: {len(cover_matrix)} segment")
                
                # Veri tiplerini düzelt
                anlik_df['urun_kod'] = anlik_df['urun_kod'].astype(str)
                depo_df['urun_kod'] = depo_df['urun_kod'].astype(str).apply(
                    lambda x: str(int(float(x))) if '.' in str(x) else str(x)
                )
                
                # 2. ÜRÜN BAZINDA TOPLAMA
                urun_toplam = anlik_df.groupby('urun_kod').agg({
                    'urun_kod': 'first',
                    'stok': 'sum',
                    'yol': 'sum',
                    'satis': 'sum',
                    'ciro': 'sum',
                    'smm': 'sum'
                }).reset_index(drop=True)
                
                st.write(f"**🏷️ Ürün bazında toplam:** {len(urun_toplam):,} ürün")
                
                # 3. DEPO STOK EKLE
                depo_toplam = depo_df.groupby('urun_kod')['stok'].sum().reset_index()
                depo_toplam.columns = ['urun_kod', 'depo_stok']
                
                st.write(f"**📦 Depo stok:** {len(depo_toplam):,} ürün, Toplam: {depo_toplam['depo_stok'].sum():,.0f}")
                
                urun_toplam = urun_toplam.merge(depo_toplam, on='urun_kod', how='left')
                urun_toplam['depo_stok'] = urun_toplam['depo_stok'].fillna(0)
                
                # 4. BRÜT KAR VE MARJ HESAPLA
                st.write("**💰 SMM ve Ciro kontrol (ilk 5 ürün):**")
                sample = urun_toplam[['urun_kod', 'satis', 'ciro', 'smm']].head(5)
                st.dataframe(sample)
                
                ortalama_smm = urun_toplam['smm'].mean()
                ortalama_ciro = urun_toplam['ciro'].mean()
                
                if ortalama_smm < ortalama_ciro * 0.1:
                    st.warning("⚠️ SMM birim maliyet olarak algılandı. Toplam maliyet = SMM × Satış")
                    urun_toplam['toplam_smm'] = urun_toplam['smm'] * urun_toplam['satis']
                else:
                    urun_toplam['toplam_smm'] = urun_toplam['smm']
                
                urun_toplam['brut_kar'] = urun_toplam['ciro'] - urun_toplam['toplam_smm']
                
                # Brüt kar marjı
                urun_toplam['brut_kar_marji'] = np.where(
                    urun_toplam['ciro'] > 0,
                    (urun_toplam['brut_kar'] / urun_toplam['ciro'] * 100),
                    0
                )
                
                # 5. COVER HESAPLA
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
                
                # 6. COVER SEGMENT ATAMASI
                product_ranges = st.session_state.segmentation_params['product_ranges']
                product_labels = [f"{int(r[0])}-{int(r[1]) if r[1] != float('inf') else 'inf'}" for r in product_ranges]
                
                urun_toplam['cover_segment'] = pd.cut(
                    urun_toplam['cover'],
                    bins=[r[0] for r in product_ranges] + [product_ranges[-1][1]],
                    labels=product_labels,
                    include_lowest=True
                )
                
                urun_toplam['cover_segment'] = urun_toplam['cover_segment'].astype(str)
                
                st.write(f"**🎯 Debug: Cover segment dağılımı:**")
                st.write(urun_toplam['cover_segment'].value_counts().sort_index())
                
                # 7. GENİŞLETME KATSAYISINI EKLE
                urun_toplam = urun_toplam.merge(
                    cover_matrix.rename(columns={'katsayi': 'genlestirme_katsayisi'}),
                    on='cover_segment',
                    how='left'
                )
                urun_toplam['genlestirme_katsayisi'] = urun_toplam['genlestirme_katsayisi'].fillna(1.0)
                
                # 8. FORWARD COVER VE MIN SEVK EKLE
                default_fc = kpi_df['forward_cover'].mean()
                urun_toplam['forward_cover'] = default_fc
                
                # Min sevk adeti
                if st.session_state.sevkiyat_sonuc is not None:
                    sevk_df = st.session_state.sevkiyat_sonuc.copy()
                    sevk_df['urun_kod'] = sevk_df['urun_kod'].astype(str)
                    
                    min_sevk = sevk_df.groupby('urun_kod')['sevkiyat_miktari'].sum().reset_index()
                    min_sevk.columns = ['urun_kod', 'min_sevk_adeti']
                    
                    urun_toplam = urun_toplam.merge(min_sevk, on='urun_kod', how='left')
                else:
                    urun_toplam['min_sevk_adeti'] = 0
                
                urun_toplam['min_sevk_adeti'] = urun_toplam['min_sevk_adeti'].fillna(0)
                
                # 9. FİLTRELERİ UYGULA
                urun_toplam['filtre_uygun'] = (
                    (urun_toplam['cover'] < cover_threshold) &
                    (urun_toplam['brut_kar_marji'] > margin_threshold)
                )
                
                filtre_sayisi = urun_toplam['filtre_uygun'].sum()
                st.write(f"**✅ Filtreye uygun ürün:** {filtre_sayisi}")
                st.write(f"   - Cover < {cover_threshold}: {(urun_toplam['cover'] < cover_threshold).sum()}")
                st.write(f"   - Brüt Kar Marjı > {margin_threshold}%: {(urun_toplam['brut_kar_marji'] > margin_threshold).sum()}")
                
                # 10. ALIM SİPARİŞ HESAPLA
                urun_toplam['talep'] = (
                    urun_toplam['satis'] * 
                    urun_toplam['genlestirme_katsayisi'] * 
                    (urun_toplam['forward_cover'] + 2)
                )
                
                urun_toplam['mevcut_stok'] = (
                    urun_toplam['stok'] + 
                    urun_toplam['yol'] + 
                    urun_toplam['depo_stok']
                )
                
                urun_toplam['alim_siparis_hesap'] = (
                    urun_toplam['talep'] - urun_toplam['mevcut_stok']
                )
                
                # Filtreye uygunsa ve pozitifse min_sevk ekle
                urun_toplam['alim_siparis'] = urun_toplam.apply(
                    lambda row: (
                        max(0, row['alim_siparis_hesap'] + row['min_sevk_adeti'])
                        if row['filtre_uygun'] and row['alim_siparis_hesap'] > 0
                        else 0
                    ),
                    axis=1
                )
                
                st.write(f"**📦 Alım sipariş > 0 olan ürün:** {(urun_toplam['alim_siparis'] > 0).sum()}")
                st.write(f"**📦 Toplam alım sipariş:** {urun_toplam['alim_siparis'].sum():,.0f}")
                
                # 11. SONUÇLARI HAZIRLA
                sonuc_df = urun_toplam[[
                    'urun_kod', 'cover_segment',
                    'stok', 'yol', 'depo_stok', 'satis',
                    'ciro', 'toplam_smm', 'brut_kar', 'brut_kar_marji',
                    'cover', 'genlestirme_katsayisi', 'forward_cover',
                    'min_sevk_adeti', 'filtre_uygun', 'alim_siparis'
                ]].copy()
                
                sonuc_df = sonuc_df.sort_values('alim_siparis', ascending=False).reset_index(drop=True)
                
                st.session_state.alim_siparis_sonuc = sonuc_df
                
                st.success("✅ Alım sipariş hesaplaması tamamlandı!")
                st.balloons()
                
                # SONUÇLAR
                st.markdown("---")
                st.subheader("📊 Alım Sipariş Sonuçları")
                
                # Metrikler
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    toplam_alim = sonuc_df['alim_siparis'].sum()
                    st.metric("📦 Toplam Alım Sipariş", f"{toplam_alim:,.0f}")
                
                with col2:
                    alim_sku = (sonuc_df['alim_siparis'] > 0).sum()
                    st.metric("🏷️ Alım Gereken SKU", f"{alim_sku}")
                
                with col3:
                    filtre_uygun = sonuc_df['filtre_uygun'].sum()
                    st.metric("✅ Filtreye Uygun", f"{filtre_uygun}")
                
                with col4:
                    if alim_sku > 0:
                        ort_alim = toplam_alim / alim_sku
                        st.metric("📊 Ort. Alım/SKU", f"{ort_alim:,.0f}")
                    else:
                        st.metric("📊 Ort. Alım/SKU", "0")
                
                st.markdown("---")
                
                # Cover Segment bazında özet
                st.subheader("🎯 Cover Segment Bazında Analiz")
                
                if (sonuc_df['alim_siparis'] > 0).sum() > 0:
                    cover_dist = sonuc_df[sonuc_df['alim_siparis'] > 0].groupby('cover_segment').agg({
                        'urun_kod': 'count',
                        'alim_siparis': 'sum'
                    }).reset_index()
                    cover_dist.columns = ['Cover Segment', 'Ürün Sayısı', 'Toplam Alım']
                    
                    # Sırala
                    cover_dist['sort_key'] = cover_dist['Cover Segment'].apply(
                        lambda x: int(x.split('-')[0]) if x.split('-')[0].isdigit() else 9999
                    )
                    cover_dist = cover_dist.sort_values('sort_key').drop('sort_key', axis=1)
                    
                    st.dataframe(cover_dist, use_container_width=True)
                
                st.markdown("---")
                
                # Detaylı tablo
                st.subheader("📋 Detaylı Alım Sipariş Tablosu")
                
                show_all = st.checkbox("Tüm ürünleri göster (alım sipariş=0 dahil)", value=False)
                
                if show_all:
                    display_df = sonuc_df
                else:
                    display_df = sonuc_df[sonuc_df['alim_siparis'] > 0]
                
                st.write(f"**Gösterilen ürün sayısı:** {len(display_df)}")
                
                if len(display_df) > 0:
                    st.dataframe(
                        display_df.style.format({
                            'stok': '{:,.0f}',
                            'yol': '{:,.0f}',
                            'depo_stok': '{:,.0f}',
                            'satis': '{:,.0f}',
                            'ciro': '{:,.2f}',
                            'toplam_smm': '{:,.2f}',
                            'brut_kar': '{:,.2f}',
                            'brut_kar_marji': '{:.2f}%',
                            'cover': '{:.2f}',
                            'genlestirme_katsayisi': '{:.2f}',
                            'forward_cover': '{:.2f}',
                            'min_sevk_adeti': '{:,.0f}',
                            'alim_siparis': '{:,.0f}'
                        }),
                        use_container_width=True,
                        height=500
                    )
                    
                    st.markdown("---")
                    
                    # Top 10
                    st.subheader("🏆 En Yüksek Alım Siparişli 10 Ürün")
                    
                    top_10 = display_df.nlargest(10, 'alim_siparis')[[
                        'urun_kod', 'cover_segment', 'cover',
                        'brut_kar_marji', 'satis', 'alim_siparis'
                    ]]
                    
                    st.dataframe(
                        top_10.style.format({
                            'cover': '{:.2f}',
                            'brut_kar_marji': '{:.2f}%',
                            'satis': '{:,.0f}',
                            'alim_siparis': '{:,.0f}'
                        }),
                        use_container_width=True
                    )
                else:
                    st.info("ℹ️ Filtreye uygun ürün bulunamadı. Filtre değerlerini ayarlayın.")
                
                st.markdown("---")
                
                # Export
                st.subheader("📥 Sonuçları Dışa Aktar")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📥 CSV İndir (Tümü)",
                        data=sonuc_df.to_csv(index=False, encoding='utf-8-sig'),
                        file_name="alim_siparis_tum.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    alim_var = sonuc_df[sonuc_df['alim_siparis'] > 0]
                    st.download_button(
                        label="📥 CSV İndir (Alım>0)",
                        data=alim_var.to_csv(index=False, encoding='utf-8-sig'),
                        file_name="alim_siparis_pozitif.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
        
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
    
    # Sadece alım sipariş > 0 olanlar
    alim_df = sonuc_df[sonuc_df['alim_siparis'] > 0].copy()
    
    if len(alim_df) == 0:
        st.info("ℹ️ Alım sipariş ihtiyacı olan ürün bulunamadı.")
        st.stop()
    
    # Genel özet
    st.subheader("📈 Genel Özet")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📦 Toplam Alım", f"{alim_df['alim_siparis'].sum():,.0f}")
    
    with col2:
        st.metric("🏷️ Ürün Sayısı", f"{len(alim_df)}")
    
    with col3:
        ort_alim = alim_df['alim_siparis'].mean()
        st.metric("📊 Ortalama Alım", f"{ort_alim:,.0f}")
    
    with col4:
        median_alim = alim_df['alim_siparis'].median()
        st.metric("📊 Medyan Alım", f"{median_alim:,.0f}")
    
    st.markdown("---")
    
    # Tab'lar
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Segment Analizi",
        "💰 Karlılık Analizi",
        "📊 Cover Analizi",
        "🏆 Top Ürünler"
    ])
    
    # ============================================
    # SEGMENT ANALİZİ
    # ============================================
    with tab1:
        st.subheader("🎯 Cover Segment Bazında Analiz")
        
        segment_analiz = alim_df.groupby('cover_segment').agg({
            'urun_kod': 'count',
            'alim_siparis': 'sum',
            'satis': 'sum',
            'brut_kar': 'sum'
        }).reset_index()
        
        segment_analiz.columns = ['Cover Segment', 'Ürün Sayısı', 'Toplam Alım', 'Toplam Satış', 'Toplam Brüt Kar']
        
        # Sırala
        segment_analiz['sort_key'] = segment_analiz['Cover Segment'].apply(
            lambda x: int(x.split('-')[0]) if x.split('-')[0].isdigit() else 9999
        )
        segment_analiz = segment_analiz.sort_values('sort_key').drop('sort_key', axis=1)
        
        # Yüzdelik hesaplamalar
        segment_analiz['Alım Payı %'] = (segment_analiz['Toplam Alım'] / segment_analiz['Toplam Alım'].sum() * 100).round(2)
        segment_analiz['Ürün Payı %'] = (segment_analiz['Ürün Sayısı'] / segment_analiz['Ürün Sayısı'].sum() * 100).round(2)
        
        st.dataframe(
            segment_analiz.style.format({
                'Ürün Sayısı': '{:.0f}',
                'Toplam Alım': '{:,.0f}',
                'Toplam Satış': '{:,.0f}',
                'Toplam Brüt Kar': '{:,.2f}',
                'Alım Payı %': '{:.1f}%',
                'Ürün Payı %': '{:.1f}%'
            }),
            use_container_width=True
        )
        
        st.markdown("---")
        
        # Grafikler
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Segment Bazında Alım Dağılımı**")
            segment_chart = segment_analiz.set_index('Cover Segment')[['Toplam Alım']]
            st.bar_chart(segment_chart)
        
        with col2:
            st.write("**Segment Bazında Ürün Dağılımı**")
            urun_chart = segment_analiz.set_index('Cover Segment')[['Ürün Sayısı']]
            st.bar_chart(urun_chart)
    
    # ============================================
    # KARLILIK ANALİZİ
    # ============================================
    with tab2:
        st.subheader("💰 Karlılık Analizi")
        
        # Marj aralıklarına göre gruplama
        alim_df['marj_kategori'] = pd.cut(
            alim_df['brut_kar_marji'],
            bins=[-np.inf, 0, 10, 20, 30, np.inf],
            labels=['Negatif', '%0-10', '%10-20', '%20-30', '%30+']
        )
        
        marj_analiz = alim_df.groupby('marj_kategori').agg({
            'urun_kod': 'count',
            'alim_siparis': 'sum',
            'brut_kar': 'sum'
        }).reset_index()
        
        marj_analiz.columns = ['Marj Kategorisi', 'Ürün Sayısı', 'Toplam Alım', 'Toplam Brüt Kar']
        
        st.dataframe(
            marj_analiz.style.format({
                'Ürün Sayısı': '{:.0f}',
                'Toplam Alım': '{:,.0f}',
                'Toplam Brüt Kar': '{:,.2f}'
            }),
            use_container_width=True
        )
        
        st.markdown("---")
        
        # En karlı 20 ürün
        st.subheader("🏆 En Yüksek Brüt Kara Sahip 20 Ürün")
        
        top_kar = alim_df.nlargest(20, 'brut_kar')[[
            'urun_kod', 'cover_segment', 'brut_kar', 'brut_kar_marji', 'alim_siparis'
        ]]
        
        st.dataframe(
            top_kar.style.format({
                'brut_kar': '{:,.2f}',
                'brut_kar_marji': '{:.2f}%',
                'alim_siparis': '{:,.0f}'
            }),
            use_container_width=True
        )
    
    # ============================================
    # COVER ANALİZİ
    # ============================================
    with tab3:
        st.subheader("📊 Cover Dağılımı Analizi")
        
        # Cover aralıklarına göre histogram
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("**Cover Dağılımı**")
            cover_hist = alim_df['cover'].value_counts(bins=20).sort_index()
            st.bar_chart(cover_hist)
        
        with col2:
            st.write("**Cover İstatistikleri**")
            st.metric("Ortalama Cover", f"{alim_df['cover'].mean():.2f}")
            st.metric("Medyan Cover", f"{alim_df['cover'].median():.2f}")
            st.metric("Min Cover", f"{alim_df['cover'].min():.2f}")
            st.metric("Max Cover", f"{alim_df['cover'].max():.2f}")
        
        st.markdown("---")
        
        # En düşük cover'a sahip ürünler
        st.subheader("⚠️ En Düşük Cover'a Sahip 20 Ürün (Acil Alım Gerekli)")
        
        low_cover = alim_df.nsmallest(20, 'cover')[[
            'urun_kod', 'cover', 'satis', 'stok', 'depo_stok', 'alim_siparis'
        ]]
        
        st.dataframe(
            low_cover.style.format({
                'cover': '{:.2f}',
                'satis': '{:,.0f}',
                'stok': '{:,.0f}',
                'depo_stok': '{:,.0f}',
                'alim_siparis': '{:,.0f}'
            }),
            use_container_width=True
        )
    
    # ============================================
    # TOP ÜRÜNLER
    # ============================================
    with tab4:
        st.subheader("🏆 Top Performans Ürünleri")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**En Yüksek Alım Miktarı - Top 15**")
            top_alim = alim_df.nlargest(15, 'alim_siparis')[[
                'urun_kod', 'cover_segment', 'alim_siparis', 'satis'
            ]]
            st.dataframe(
                top_alim.style.format({
                    'alim_siparis': '{:,.0f}',
                    'satis': '{:,.0f}'
                }),
                use_container_width=True
            )
        
        with col2:
            st.write("**En Yüksek Satış - Top 15**")
            top_satis = alim_df.nlargest(15, 'satis')[[
                'urun_kod', 'cover_segment', 'satis', 'alim_siparis'
            ]]
            st.dataframe(
                top_satis.style.format({
                    'satis': '{:,.0f}',
                    'alim_siparis': '{:,.0f}'
                }),
                use_container_width=True
            )
        
        st.markdown("---")
        
        # Ürün master varsa ek bilgiler
        if st.session_state.urun_master is not None:
            st.subheader("📦 Ürün Detayları")
            
            urun_master = st.session_state.urun_master.copy()
            urun_master['urun_kod'] = urun_master['urun_kod'].astype(str)
            
            alim_detay = alim_df.merge(
                urun_master[['urun_kod', 'urun_ad', 'marka_ad', 'mg_ad']],
                on='urun_kod',
                how='left'
            )
            
            # Marka bazında analiz
            st.write("**Marka Bazında Alım Dağılımı**")
            marka_analiz = alim_detay.groupby('marka_ad').agg({
                'urun_kod': 'count',
                'alim_siparis': 'sum'
            }).reset_index()
            marka_analiz.columns = ['Marka', 'Ürün Sayısı', 'Toplam Alım']
            marka_analiz = marka_analiz.sort_values('Toplam Alım', ascending=False).head(10)
            
            st.dataframe(
                marka_analiz.style.format({
                    'Ürün Sayısı': '{:.0f}',
                    'Toplam Alım': '{:,.0f}'
                }),
                use_container_width=True
            )
    
    st.markdown("---")
    
    # Export butonları
    st.subheader("📥 Raporları İndir")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="📥 Alım Sipariş Detayı",
            data=alim_df.to_csv(index=False, encoding='utf-8-sig'),
            file_name="alim_siparis_detay.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        st.download_button(
            label="📥 Segment Analizi",
            data=segment_analiz.to_csv(index=False, encoding='utf-8-sig'),
            file_name="segment_analizi.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col3:
        st.download_button(
            label="📥 Karlılık Analizi",
            data=marj_analiz.to_csv(index=False, encoding='utf-8-sig'),
            file_name="karlilik_analizi.csv",
            mime="text/csv",
            use_container_width=True
        )
