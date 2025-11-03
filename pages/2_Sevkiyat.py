import streamlit as st
import pandas as pd
import time
import numpy as np
import io

# Sayfa config
st.set_page_config(
    page_title="Retail Sevkiyat Planlama",
    page_icon="📦", 
    layout="wide"
)

# ============================================
# SESSION STATE BAŞLATMA - TEK SEFER
# ============================================

# Veri dosyaları
if 'urun_master' not in st.session_state:
    st.session_state.urun_master = None
if 'magaza_master' not in st.session_state:
    st.session_state.magaza_master = None
if 'yasak_master' not in st.session_state:
    st.session_state.yasak_master = None
if 'depo_stok' not in st.session_state:
    st.session_state.depo_stok = None
if 'anlik_stok_satis' not in st.session_state:
    st.session_state.anlik_stok_satis = None
if 'haftalik_trend' not in st.session_state:
    st.session_state.haftalik_trend = None
if 'kpi' not in st.session_state:
    st.session_state.kpi = None

# Segmentasyon parametreleri - TEK TANIMLA
if 'segmentation_params' not in st.session_state:
    st.session_state.segmentation_params = {
        'product_ranges': [(0, 4), (5, 8), (9, 12), (12, 15), (15, 20), (20, float('inf'))],
        'store_ranges': [(0, 4), (5, 8), (9, 12), (12, 15), (15, 20), (20, float('inf'))]
    }

# Matrisler
if 'initial_matris' not in st.session_state:
    st.session_state.initial_matris = None
if 'target_matrix' not in st.session_state:
    st.session_state.target_matrix = None
if 'sisme_orani' not in st.session_state:
    st.session_state.sisme_orani = None
if 'genlestirme_orani' not in st.session_state:
    st.session_state.genlestirme_orani = None
if 'min_oran' not in st.session_state:
    st.session_state.min_oran = None

# Diğer
if 'siralama_data' not in st.session_state:
    st.session_state.siralama_data = None
if 'sevkiyat_sonuc' not in st.session_state:
    st.session_state.sevkiyat_sonuc = None
if 'yeni_urun_listesi' not in st.session_state:
    st.session_state.yeni_urun_listesi = None

# Hedef Matris'ten gelen segmentler (otomatik kaydedilecek)
if 'urun_segment_map' not in st.session_state:
    st.session_state.urun_segment_map = None
if 'magaza_segment_map' not in st.session_state:
    st.session_state.magaza_segment_map = None
if 'prod_segments' not in st.session_state:
    st.session_state.prod_segments = None
if 'store_segments' not in st.session_state:
    st.session_state.store_segments = None

# Sidebar menü 
menu = st.sidebar.radio(
    "Menü",
    ["🏠 Ana Sayfa", "🫧 Segmentasyon", "🎲 Hedef Matris", 
     "🔢 Sıralama", "📐 Hesaplama", "📈 Raporlar", "💾 Master Data"]
)

# ============================================
# 🏠 ANA SAYFA
# ============================================
if menu == "🏠 Ana Sayfa":
    st.title("🌟 Sevkiyat Planlama Sistemi")
    st.markdown("---")
    
    st.info("""
    **📋 Veri Yükleme:** Sol menüden "Veri Yükleme" sayfasına gidin.
    **💵 Alım Sipariş:** Hesaplama sonrası "Alım Sipariş (PO)" sayfasına gidin.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➡️ Veri Yükleme Sayfasına Git", width='content'):
            st.switch_page("pages/0_Veri_Yukleme.py")
    with col2:
        if st.button("➡️ Alım Sipariş Sayfasına Git", width='content'):
            st.switch_page("pages/4_PO.py")
    
    st.markdown("---")
    
# ============================================
# 🎯 SEGMENTASYON AYARLARI
# ============================================
elif menu == "🫧 Segmentasyon":
    st.title("🫧 Segmentasyon")
    st.markdown("---")
    
    st.info("**Stok/Satış oranına göre** ürün ve mağazaları gruplandırma (Toplam Stok / Toplam Satış)")
    
    if st.session_state.anlik_stok_satis is None:
        st.warning("⚠️ Önce 'Veri Yükleme' bölümünden anlık stok/satış verisini yükleyin!")
        st.stop()
    
    # Ürün bazında toplam stok/satış hesapla
    data = st.session_state.anlik_stok_satis.copy()
    
    # Ürün bazında gruplama - SADECE MEVCUT KOLONLAR
    urun_aggregated = data.groupby('urun_kod').agg({
        'stok': 'sum',
        'yol': 'sum',
        'satis': 'sum',
        'ciro': 'sum'
    }).reset_index()
    urun_aggregated['stok_satis_orani'] = urun_aggregated['stok'] / urun_aggregated['satis'].replace(0, 1)
    urun_aggregated['cover'] = urun_aggregated['stok_satis_orani']
    
    # Ürün kodu ve marka bilgilerini ekle (eğer varsa)
    if st.session_state.urun_master is not None:
        # Sadece kod alanlarını kullan
        urun_master = st.session_state.urun_master[['urun_kod', 'marka_kod']].copy()
        urun_master['urun_kod'] = urun_master['urun_kod'].astype(str)
        urun_aggregated['urun_kod'] = urun_aggregated['urun_kod'].astype(str)
        urun_aggregated = urun_aggregated.merge(urun_master, on='urun_kod', how='left')
    else:
        urun_aggregated['marka_kod'] = 'Bilinmiyor'
    
    # Mağaza bazında gruplama - SADECE MEVCUT KOLONLAR
    magaza_aggregated = data.groupby('magaza_kod').agg({
        'stok': 'sum',
        'yol': 'sum',
        'satis': 'sum',
        'ciro': 'sum'
    }).reset_index()
    magaza_aggregated['stok_satis_orani'] = magaza_aggregated['stok'] / magaza_aggregated['satis'].replace(0, 1)
    magaza_aggregated['cover'] = magaza_aggregated['stok_satis_orani']
    
    st.markdown("---")
    
    # Ürün segmentasyonu
    st.subheader("🏷️ Ürün Segmentasyonu (Toplam Stok / Toplam Satış)")
    
    use_default_product = st.checkbox("Varsayılan aralıkları kullan (Ürün)", value=True)
    
    if use_default_product:
        st.write("**Varsayılan Aralıklar**: 0-4, 5-8, 9-12, 12-15, 15-20, 20+")
        product_ranges = [(0, 4), (5, 8), (9, 12), (12, 15), (15, 20), (20, float('inf'))]
    else:
        st.write("Özel aralıklar tanımlayın:")
        num_ranges = st.number_input("Kaç aralık?", min_value=2, max_value=10, value=6)
        
        product_ranges = []
        for i in range(num_ranges):
            col1, col2 = st.columns(2)
            with col1:
                min_val = st.number_input(f"Aralık {i+1} - Min", value=i*5, key=f"prod_min_{i}")
            with col2:
                max_val = st.number_input(f"Aralık {i+1} - Max", value=(i+1)*5 if i < num_ranges-1 else 999, key=f"prod_max_{i}")
            product_ranges.append((min_val, max_val))
    
    # Ürün segmentasyonunu uygula
    if urun_aggregated is not None and len(urun_aggregated) > 0:
        temp_prod = urun_aggregated.copy()
        
        # Segment labels
        product_labels = [f"{int(r[0])}-{int(r[1]) if r[1] != float('inf') else 'inf'}" for r in product_ranges]
        
        temp_prod['segment'] = pd.cut(
            temp_prod['stok_satis_orani'], 
            bins=[r[0] for r in product_ranges] + [product_ranges[-1][1]],
            labels=product_labels,
            include_lowest=True
        )
        
        st.write("**Ürün Dağılımı Önizleme:**")
        segment_dist = temp_prod['segment'].value_counts().sort_index()
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.dataframe(segment_dist, width='content', height=200)
        with col2:
            st.bar_chart(segment_dist)
        
        st.markdown("---")
        
        # DETAYLI ÜRÜN SEGMENTASYON TABLOSU
        st.subheader("📋 Detaylı Ürün Segmentasyon Tablosu")
        
        # Tabloyu hazırla - AD ALANLARI KALDIRILDI
        urun_detail = temp_prod[['urun_kod', 'marka_kod', 'segment', 
                                  'stok', 'yol', 'satis', 'ciro', 'stok_satis_orani']].copy()
        urun_detail = urun_detail.sort_values(['segment', 'stok_satis_orani'], ascending=[True, False])
        urun_detail.columns = ['Ürün Kodu', 'Marka Kodu', 'Segment', 
                               'Toplam Stok', 'Toplam Yol', 'Toplam Satış', 'Toplam Ciro', 'Stok/Satış Oranı']
        
        # Segment bazında filtreleme
        selected_segment_prod = st.multiselect(
            "Segment Seç (Filtre)",
            options=product_labels,
            default=product_labels,
            key="filter_prod_segment"
        )
        
        filtered_urun = urun_detail[urun_detail['Segment'].isin(selected_segment_prod)]
        
        st.write(f"**Toplam {len(filtered_urun)} ürün gösteriliyor**")
        st.dataframe(
            filtered_urun.style.format({
                'Toplam Stok': '{:,.0f}',
                'Toplam Yol': '{:,.0f}',
                'Toplam Satış': '{:,.0f}',
                'Toplam Ciro': '{:,.2f}',
                'Stok/Satış Oranı': '{:.2f}'
            }),
            width='content',
            height=400
        )
        
        # Segment bazında özet
        st.markdown("---")
        st.subheader("📊 Segment Bazında Ürün Özeti")
        
        segment_ozet = urun_detail.groupby('Segment').agg({
            'Ürün Kodu': 'count',
            'Toplam Stok': 'sum',
            'Toplam Satış': 'sum',
            'Toplam Ciro': 'sum',
            'Stok/Satış Oranı': 'mean'
        }).reset_index()
        segment_ozet.columns = ['Segment', 'Ürün Sayısı', 'Toplam Stok', 'Toplam Satış', 'Toplam Ciro', 'Ort. Cover']
        
        st.dataframe(
            segment_ozet.style.format({
                'Toplam Stok': '{:,.0f}',
                'Toplam Satış': '{:,.0f}',
                'Toplam Ciro': '{:,.2f}',
                'Ort. Cover': '{:.2f}'
            }),
            width='content'
        )
        
        # CSV İndir - ÜRÜN
        st.download_button(
            label="📥 Ürün Segmentasyon Detayı İndir (CSV)",
            data=urun_detail.to_csv(index=False, encoding='utf-8-sig'),
            file_name="urun_segmentasyon_detay.csv",
            mime="text/csv",
            key="download_urun_segment"
        )
    
    st.markdown("---")
    
    # Mağaza segmentasyonu
    st.subheader("🏪 Mağaza Segmentasyonu (Toplam Stok / Toplam Satış)")
    
    use_default_store = st.checkbox("Varsayılan aralıkları kullan (Mağaza)", value=True)
    
    if use_default_store:
        st.write("**Varsayılan Aralıklar**: 0-4, 5-8, 9-12, 12-15, 15-20, 20+")
        store_ranges = [(0, 4), (5, 8), (9, 12), (12, 15), (15, 20), (20, float('inf'))]
    else:
        st.write("Özel aralıklar tanımlayın:")
        num_ranges_store = st.number_input("Kaç aralık?", min_value=2, max_value=10, value=6, key="store_ranges")
        
        store_ranges = []
        for i in range(num_ranges_store):
            col1, col2 = st.columns(2)
            with col1:
                min_val = st.number_input(f"Aralık {i+1} - Min", value=i*5, key=f"store_min_{i}")
            with col2:
                max_val = st.number_input(f"Aralık {i+1} - Max", value=(i+1)*5 if i < num_ranges_store-1 else 999, key=f"store_max_{i}")
            store_ranges.append((min_val, max_val))
    
    # Mağaza segmentasyonunu uygula
    if magaza_aggregated is not None and len(magaza_aggregated) > 0:
        temp_store = magaza_aggregated.copy()
        
        # Segment labels
        store_labels = [f"{int(r[0])}-{int(r[1]) if r[1] != float('inf') else 'inf'}" for r in store_ranges]
        
        temp_store['segment'] = pd.cut(
            temp_store['stok_satis_orani'], 
            bins=[r[0] for r in store_ranges] + [store_ranges[-1][1]],
            labels=store_labels,
            include_lowest=True
        )
        
        st.write("**Mağaza Dağılımı Önizleme:**")
        segment_dist_store = temp_store['segment'].value_counts().sort_index()
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.dataframe(segment_dist_store, width='content', height=200)
        with col2:
            st.bar_chart(segment_dist_store)
        
        st.markdown("---")
        
        # DETAYLI MAĞAZA SEGMENTASYON TABLOSU
        st.subheader("📋 Detaylı Mağaza Segmentasyon Tablosu")
        
        # Tabloyu hazırla - AD ALANI KALDIRILDI
        magaza_detail = temp_store[['magaza_kod', 'segment', 
                                     'stok', 'yol', 'satis', 'ciro', 'stok_satis_orani']].copy()
        magaza_detail = magaza_detail.sort_values(['segment', 'stok_satis_orani'], ascending=[True, False])
        magaza_detail.columns = ['Mağaza Kodu', 'Segment', 
                                 'Toplam Stok', 'Toplam Yol', 'Toplam Satış', 'Toplam Ciro', 'Stok/Satış Oranı']
        
        # Segment bazında filtreleme
        selected_segment_store = st.multiselect(
            "Segment Seç (Filtre)",
            options=store_labels,
            default=store_labels,
            key="filter_store_segment"
        )
        
        filtered_magaza = magaza_detail[magaza_detail['Segment'].isin(selected_segment_store)]
        
        st.write(f"**Toplam {len(filtered_magaza)} mağaza gösteriliyor**")
        st.dataframe(
            filtered_magaza.style.format({
                'Toplam Stok': '{:,.0f}',
                'Toplam Yol': '{:,.0f}',
                'Toplam Satış': '{:,.0f}',
                'Toplam Ciro': '{:,.2f}',
                'Stok/Satış Oranı': '{:.2f}'
            }),
            width='content',
            height=400
        )
        
        # Segment bazında özet
        st.markdown("---")
        st.subheader("📊 Segment Bazında Mağaza Özeti")
        
        segment_ozet_magaza = magaza_detail.groupby('Segment').agg({
            'Mağaza Kodu': 'count',
            'Toplam Stok': 'sum',
            'Toplam Satış': 'sum',
            'Toplam Ciro': 'sum',
            'Stok/Satış Oranı': 'mean'
        }).reset_index()
        segment_ozet_magaza.columns = ['Segment', 'Mağaza Sayısı', 'Toplam Stok', 'Toplam Satış', 'Toplam Ciro', 'Ort. Cover']
        
        st.dataframe(
            segment_ozet_magaza.style.format({
                'Toplam Stok': '{:,.0f}',
                'Toplam Satış': '{:,.0f}',
                'Toplam Ciro': '{:,.2f}',
                'Ort. Cover': '{:.2f}'
            }),
            width='content'
        )
        
        # CSV İndir - MAĞAZA
        st.download_button(
            label="📥 Mağaza Segmentasyon Detayı İndir (CSV)",
            data=magaza_detail.to_csv(index=False, encoding='utf-8-sig'),
            file_name="magaza_segmentasyon_detay.csv",
            mime="text/csv",
            key="download_magaza_segment"
        )
    
    st.markdown("---")
    
    # Kaydet butonu
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("💾 Segmentasyonu Kaydet", type="primary"):
            st.session_state.segmentation_params = {
                'product_ranges': product_ranges,
                'store_ranges': store_ranges
            }
            st.success("✅ Ayarlar kaydedildi!")
    with col2:
        st.info("ℹ️ Kaydetmeseniz de default değerler kullanılacaktır.")
    
    st.markdown("---")
    
    # HER İKİSİNİ BİRLİKTE İNDİR
    st.subheader("📥 Tüm Segmentasyon Verilerini İndir")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Excel formatında (iki sheet)
        if st.button("📊 Excel İndir (Ürün + Mağaza)", width='content'):
            try:
                import io
                from io import BytesIO
                
                # Excel writer oluştur
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    urun_detail.to_excel(writer, sheet_name='Ürün Segmentasyon', index=False)
                    magaza_detail.to_excel(writer, sheet_name='Mağaza Segmentasyon', index=False)
                
                output.seek(0)
                
                st.download_button(
                    label="⬇️ Excel Dosyasını İndir",
                    data=output.getvalue(),
                    file_name="segmentasyon_tam_detay.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except ImportError:
                st.error("❌ Excel export için 'openpyxl' kütüphanesi gerekli. Lütfen yükleyin: pip install openpyxl")
    
    with col2:
        # ZIP formatında (iki CSV)
        if st.button("📦 ZIP İndir (2 CSV)", width='content'):
            import zipfile
            import io
            
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Ürün CSV
                urun_csv = urun_detail.to_csv(index=False, encoding='utf-8-sig')
                zip_file.writestr('urun_segmentasyon.csv', urun_csv.encode('utf-8-sig'))
                
                # Mağaza CSV
                magaza_csv = magaza_detail.to_csv(index=False, encoding='utf-8-sig')
                zip_file.writestr('magaza_segmentasyon.csv', magaza_csv.encode('utf-8-sig'))
            
            zip_buffer.seek(0)
            
            st.download_button(
                label="⬇️ ZIP Dosyasını İndir",
                data=zip_buffer.getvalue(),
                file_name="segmentasyon_detay.zip",
                mime="application/zip"
            ) 

# ============================================
# 🎲 HEDEF MATRİS - TAM DÜZELTİLMİŞ
# ============================================
elif menu == "🎲 Hedef Matris":
    st.title("🎲 Hedef Matris Parametreleri")
    st.markdown("---")
    
    if st.session_state.anlik_stok_satis is None:
        st.warning("⚠️ Önce 'Veri Yükleme' bölümünden anlık stok/satış verisini yükleyin!")
    else:
        # Segmentasyon yap
        data = st.session_state.anlik_stok_satis.copy()
        
        # Ürün bazında toplam stok/satış
        urun_aggregated = data.groupby('urun_kod').agg({
            'stok': 'sum',
            'satis': 'sum'
        }).reset_index()
        urun_aggregated['stok_satis_orani'] = urun_aggregated['stok'] / urun_aggregated['satis'].replace(0, 1)
        
        # Mağaza bazında toplam stok/satış
        magaza_aggregated = data.groupby('magaza_kod').agg({
            'stok': 'sum',
            'satis': 'sum'
        }).reset_index()
        magaza_aggregated['stok_satis_orani'] = magaza_aggregated['stok'] / magaza_aggregated['satis'].replace(0, 1)
        
        # Segmentasyon parametrelerini al
        product_ranges = st.session_state.segmentation_params['product_ranges']
        store_ranges = st.session_state.segmentation_params['store_ranges']
        
        # Ürün segmentasyonu
        product_labels = [f"{int(r[0])}-{int(r[1]) if r[1] != float('inf') else 'inf'}" for r in product_ranges]
        urun_aggregated['urun_segment'] = pd.cut(
            urun_aggregated['stok_satis_orani'], 
            bins=[r[0] for r in product_ranges] + [product_ranges[-1][1]],
            labels=product_labels,
            include_lowest=True
        )
        
        # Mağaza segmentasyonu
        store_labels = [f"{int(r[0])}-{int(r[1]) if r[1] != float('inf') else 'inf'}" for r in store_ranges]
        magaza_aggregated['magaza_segment'] = pd.cut(
            magaza_aggregated['stok_satis_orani'],
            bins=[r[0] for r in store_ranges] + [store_ranges[-1][1]],
            labels=store_labels,
            include_lowest=True
        )
        
        # Segment sıralama fonksiyonu
        def sort_segments(segments):
            def get_sort_key(seg):
                try:
                    return int(seg.split('-')[0])
                except:
                    return 9999
            return sorted(segments, key=get_sort_key)
        
        # Segmentleri hazırla
        prod_segments_raw = [str(x) for x in urun_aggregated['urun_segment'].unique() if pd.notna(x)]
        store_segments_raw = [str(x) for x in magaza_aggregated['magaza_segment'].unique() if pd.notna(x)]
        
        prod_segments = sort_segments(prod_segments_raw)
        store_segments = sort_segments(store_segments_raw)
        
        # OTOMATIK KAYDET
        st.session_state.prod_segments = prod_segments
        st.session_state.store_segments = store_segments
        st.session_state.urun_segment_map = urun_aggregated[['urun_kod', 'urun_segment']].set_index('urun_kod')['urun_segment'].to_dict()
        st.session_state.magaza_segment_map = magaza_aggregated[['magaza_kod', 'magaza_segment']].set_index('magaza_kod')['magaza_segment'].to_dict()
        
        # Segmentasyon sonuçları
        st.subheader("📊 Segmentasyon Sonuçları")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Ürün Dağılımı**")
            prod_dist = urun_aggregated['urun_segment'].value_counts().sort_index()
            st.dataframe(prod_dist, width='content')
        
        with col2:
            st.write("**Mağaza Dağılımı**")
            store_dist = magaza_aggregated['magaza_segment'].value_counts().sort_index()
            st.dataframe(store_dist, width='content')
        
        st.markdown("---")
        st.subheader("🎯 Matris Parametreleri")
        
        st.info(f"**Ürün Segmentleri:** {', '.join(prod_segments)}")
        st.info(f"**Mağaza Segmentleri:** {', '.join(store_segments)}")
        
        # ============================================
        # 1. ŞİŞME ORANI MATRİSİ
        # ============================================
        st.markdown("### 1️⃣ Şişme Oranı Matrisi (Default: 0.5)")
        
        if st.session_state.sisme_orani is None or len(st.session_state.sisme_orani) == 0:
            sisme_data = pd.DataFrame(0.5, index=prod_segments, columns=store_segments)
        else:
            sisme_data = st.session_state.sisme_orani.copy()
            for seg in prod_segments:
                if seg not in sisme_data.index:
                    sisme_data.loc[seg] = 0.5
            for seg in store_segments:
                if seg not in sisme_data.columns:
                    sisme_data[seg] = 0.5
            sisme_data = sisme_data.reindex(index=prod_segments, columns=store_segments, fill_value=0.5)
        
        # Satır başlıklarını göster
        sisme_display = sisme_data.reset_index()
        sisme_display.columns = ['Ürün Segmenti'] + list(sisme_data.columns)
        
        edited_sisme_temp = st.data_editor(
            sisme_display,
            width='content',
            column_config={col: st.column_config.NumberColumn(
                col, min_value=0.0, max_value=10.0, step=0.1, format="%.2f"
            ) for col in store_segments},
            key="sisme_matrix",
            hide_index=True
        )
        
        # GÜVENLİ DÖNÜŞÜM
        try:
            edited_df = pd.DataFrame(edited_sisme_temp)
            if 'Ürün Segmenti' in edited_df.columns:
                edited_sisme = edited_df.set_index('Ürün Segmenti')
            else:
                edited_sisme = edited_df.set_index(edited_df.columns[0])
        except:
            edited_sisme = sisme_data
        
        st.markdown("---")
        
        # ============================================
        # 2. GENLEŞTİRME ORANI MATRİSİ
        # ============================================
        st.markdown("### 2️⃣ Genleştirme Oranı Matrisi (Default: 1.0)")
        
        if st.session_state.genlestirme_orani is None or len(st.session_state.genlestirme_orani) == 0:
            genlestirme_data = pd.DataFrame(1.0, index=prod_segments, columns=store_segments)
        else:
            genlestirme_data = st.session_state.genlestirme_orani.copy()
            for seg in prod_segments:
                if seg not in genlestirme_data.index:
                    genlestirme_data.loc[seg] = 1.0
            for seg in store_segments:
                if seg not in genlestirme_data.columns:
                    genlestirme_data[seg] = 1.0
            genlestirme_data = genlestirme_data.reindex(index=prod_segments, columns=store_segments, fill_value=1.0)
        
        genlestirme_display = genlestirme_data.reset_index()
        genlestirme_display.columns = ['Ürün Segmenti'] + list(genlestirme_data.columns)
        
        edited_genlestirme_temp = st.data_editor(
            genlestirme_display,
            width='content',
            column_config={col: st.column_config.NumberColumn(
                col, min_value=0.0, max_value=10.0, step=0.1, format="%.2f"
            ) for col in store_segments},
            key="genlestirme_matrix",
            hide_index=True
        )
        
        try:
            edited_df = pd.DataFrame(edited_genlestirme_temp)
            if 'Ürün Segmenti' in edited_df.columns:
                edited_genlestirme = edited_df.set_index('Ürün Segmenti')
            else:
                edited_genlestirme = edited_df.set_index(edited_df.columns[0])
        except:
            edited_genlestirme = genlestirme_data
        
        st.markdown("---")
        
        # ============================================
        # 3. MIN ORAN MATRİSİ
        # ============================================
        st.markdown("### 3️⃣ Min Oran Matrisi (Default: 1.0)")
        
        if st.session_state.min_oran is None or len(st.session_state.min_oran) == 0:
            min_oran_data = pd.DataFrame(1.0, index=prod_segments, columns=store_segments)
        else:
            min_oran_data = st.session_state.min_oran.copy()
            for seg in prod_segments:
                if seg not in min_oran_data.index:
                    min_oran_data.loc[seg] = 1.0
            for seg in store_segments:
                if seg not in min_oran_data.columns:
                    min_oran_data[seg] = 1.0
            min_oran_data = min_oran_data.reindex(index=prod_segments, columns=store_segments, fill_value=1.0)
        
        min_oran_display = min_oran_data.reset_index()
        min_oran_display.columns = ['Ürün Segmenti'] + list(min_oran_data.columns)
        
        edited_min_oran_temp = st.data_editor(
            min_oran_display,
            width='content',
            column_config={col: st.column_config.NumberColumn(
                col, min_value=0.0, max_value=10.0, step=0.1, format="%.2f"
            ) for col in store_segments},
            key="min_oran_matrix",
            hide_index=True
        )
        
        try:
            edited_df = pd.DataFrame(edited_min_oran_temp)
            if 'Ürün Segmenti' in edited_df.columns:
                edited_min_oran = edited_df.set_index('Ürün Segmenti')
            else:
                edited_min_oran = edited_df.set_index(edited_df.columns[0])
        except:
            edited_min_oran = min_oran_data
        
        st.markdown("---")
        
        # ============================================
        # 4. INITIAL MATRİSİ
        # ============================================
        st.markdown("### 4️⃣ Initial Matris (Yeni Ürünler İçin - Default: 1.0)")
        
        if st.session_state.initial_matris is None or len(st.session_state.initial_matris) == 0:
            initial_data = pd.DataFrame(1.0, index=prod_segments, columns=store_segments)
        else:
            initial_data = st.session_state.initial_matris.copy()
            for seg in prod_segments:
                if seg not in initial_data.index:
                    initial_data.loc[seg] = 1.0
            for seg in store_segments:
                if seg not in initial_data.columns:
                    initial_data[seg] = 1.0
            initial_data = initial_data.reindex(index=prod_segments, columns=store_segments, fill_value=1.0)
        
        initial_display = initial_data.reset_index()
        initial_display.columns = ['Ürün Segmenti'] + list(initial_data.columns)
        
        edited_initial_temp = st.data_editor(
            initial_display,
            width='content',
            column_config={col: st.column_config.NumberColumn(
                col, min_value=0.0, max_value=10.0, step=0.1, format="%.2f"
            ) for col in store_segments},
            key="initial_matrix",
            hide_index=True
        )
        
        try:
            edited_df = pd.DataFrame(edited_initial_temp)
            if 'Ürün Segmenti' in edited_df.columns:
                edited_initial = edited_df.set_index('Ürün Segmenti')
            else:
                edited_initial = edited_df.set_index(edited_df.columns[0])
        except:
            edited_initial = initial_data
        
        st.markdown("---")
        
        # Kaydet butonu
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("💾 Tüm Matrisleri Kaydet", type="primary"):
                st.session_state.sisme_orani = edited_sisme
                st.session_state.genlestirme_orani = edited_genlestirme
                st.session_state.min_oran = edited_min_oran
                st.session_state.initial_matris = edited_initial
                st.success("✅ Tüm matrisler kaydedildi!")
        with col2:
            st.info("ℹ️ Kaydetmeseniz de default değerler kullanılacaktır.")

# ============================================
# 📊 SIRALAMA - DÜZELTİLMİŞ
# ============================================
elif menu == "🔢 Sıralama":
    st.title("🔢 Sıralama")
    st.markdown("---")
    
    if st.session_state.anlik_stok_satis is None:
        st.warning("⚠️ Önce 'Veri Yükleme' bölümünden anlık stok/satış verisini yükleyin!")
    else:
        st.info("Mağaza ve ürün cluster bazında sevkiyat önceliklerini belirleyin")
        
        # Segmentleri al
        data = st.session_state.anlik_stok_satis.copy()
        
        urun_aggregated = data.groupby('urun_kod').agg({'stok': 'sum', 'satis': 'sum'}).reset_index()
        urun_aggregated['stok_satis_orani'] = urun_aggregated['stok'] / urun_aggregated['satis'].replace(0, 1)
        
        magaza_aggregated = data.groupby('magaza_kod').agg({'stok': 'sum', 'satis': 'sum'}).reset_index()
        magaza_aggregated['stok_satis_orani'] = magaza_aggregated['stok'] / magaza_aggregated['satis'].replace(0, 1)
        
        product_ranges = st.session_state.segmentation_params['product_ranges']
        store_ranges = st.session_state.segmentation_params['store_ranges']
        
        # Segment labels
        product_labels = [f"{int(r[0])}-{int(r[1]) if r[1] != float('inf') else 'inf'}" for r in product_ranges]
        store_labels = [f"{int(r[0])}-{int(r[1]) if r[1] != float('inf') else 'inf'}" for r in store_ranges]
        
        # Ürün segmentasyonu
        urun_aggregated['urun_segment'] = pd.cut(
            urun_aggregated['stok_satis_orani'], 
            bins=[r[0] for r in product_ranges] + [product_ranges[-1][1]],
            labels=product_labels,
            include_lowest=True
        )
        
        # Mağaza segmentasyonu
        magaza_aggregated['magaza_segment'] = pd.cut(
            magaza_aggregated['stok_satis_orani'],
            bins=[r[0] for r in store_ranges] + [store_ranges[-1][1]],
            labels=store_labels,
            include_lowest=True
        )
        
        # ⬇️ BURADA DEĞİŞİKLİK - KOLON ADLARINI DÜZELT ⬇️
        prod_segments = sorted([str(x) for x in urun_aggregated['urun_segment'].unique() if pd.notna(x)])
        store_segments = sorted([str(x) for x in magaza_aggregated['magaza_segment'].unique() if pd.notna(x)])
        # ⬆️ 'segment' değil, 'urun_segment' ve 'magaza_segment' kullan ⬆️
        
        st.subheader("🎯 Öncelik Sıralaması")
        
        st.info("""
        **RPT:** Hızlı sevkiyat önceliği
        **Initial:** Yeni ürün önceliği
        **Min:** Minimum stok önceliği
        """)
        
        if st.session_state.siralama_data is not None:
            siralama_df = st.session_state.siralama_data
        else:
            def sort_segments(segments):
                def get_sort_key(seg):
                    try:
                        return int(seg.split('-')[0])
                    except:
                        return 999
                return sorted(segments, key=get_sort_key)
            
            sorted_store = sort_segments(store_segments)
            sorted_prod = sort_segments(prod_segments)
            
            siralama_rows = []
            oncelik = 1
            for store_seg in sorted_store:
                for prod_seg in sorted_prod:
                    siralama_rows.append({'Magaza_Cluster': store_seg, 'Urun_Cluster': prod_seg, 'Durum': 'RPT', 'Oncelik': oncelik})
                    oncelik += 1
                    siralama_rows.append({'Magaza_Cluster': store_seg, 'Urun_Cluster': prod_seg, 'Durum': 'Initial', 'Oncelik': oncelik})
                    oncelik += 1
                    siralama_rows.append({'Magaza_Cluster': store_seg, 'Urun_Cluster': prod_seg, 'Durum': 'Min', 'Oncelik': oncelik})
                    oncelik += 1
            
            siralama_df = pd.DataFrame(siralama_rows)
        
        st.markdown("---")
        st.subheader("📋 Tüm Kombinasyonlar")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🔄 Tabloyu Sıfırla", type="secondary"):
                st.session_state.siralama_data = None
                st.success("✅ Sıfırlandı!")
                st.rerun()
        
        edited_siralama = st.data_editor(
            siralama_df.sort_values('Oncelik').reset_index(drop=True),
            width='content',
            num_rows="dynamic",
            column_config={
                "Magaza_Cluster": st.column_config.SelectboxColumn("Mağaza Cluster", options=store_segments, required=True),
                "Urun_Cluster": st.column_config.SelectboxColumn("Ürün Cluster", options=prod_segments, required=True),
                "Durum": st.column_config.SelectboxColumn("Durum", options=["RPT", "Initial", "Min"], required=True),
                "Oncelik": st.column_config.NumberColumn("Öncelik", min_value=1, max_value=1000, step=1, format="%d")
            },
            hide_index=False,
            height=500
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("💾 Sıralamayı Kaydet", type="primary"):
                st.session_state.siralama_data = edited_siralama
                st.success("✅ Kaydedildi!")
        with col2:
            if st.button("🔄 Varsayılana Sıfırla"):
                st.session_state.siralama_data = None
                st.success("✅ Varsayılana sıfırlandı!")
                st.rerun()
        
        st.info("ℹ️ Kaydetmeseniz de default sıralama kullanılacaktır.")

# ============================================
# 🚚 HESAPLAMA 
# ============================================
# ============================================
# 🚚 HESAPLAMA - DÜZELTİLMİŞ VERSİYON
# ============================================
elif menu == "📐 Hesaplama":
    st.title("📐 Hesaplama")
    st.markdown("---")
    
    # Veri kontrolü
    required_data = {
        "Ürün Master": st.session_state.urun_master,
        "Mağaza Master": st.session_state.magaza_master,
        "Anlık Stok/Satış": st.session_state.anlik_stok_satis,
        "Depo Stok": st.session_state.depo_stok,
        "KPI": st.session_state.kpi
    }
    
    missing_data = [name for name, data in required_data.items() if data is None]
    
    if missing_data:
        st.warning("⚠️ Tüm zorunlu verileri yükleyin!")
        st.error(f"**Eksik:** {', '.join(missing_data)}")
        st.stop()
    
    st.success("✅ Tüm zorunlu veriler hazır!")
    
    if st.button("🚀 HESAPLA", type="primary", use_container_width=True):
        with st.spinner("Hesaplanıyor..."):
            try:
                # 1. VERİ HAZIRLA
                df = st.session_state.anlik_stok_satis.copy()
                df['urun_kod'] = df['urun_kod'].astype(str)
                df['magaza_kod'] = df['magaza_kod'].astype(str)
                
                depo_df = st.session_state.depo_stok.copy()
                depo_df['urun_kod'] = depo_df['urun_kod'].astype(str)
                
                magaza_df = st.session_state.magaza_master.copy()
                magaza_df['magaza_kod'] = magaza_df['magaza_kod'].astype(str)
                
                kpi_df = st.session_state.kpi.copy()
                
                # 2. YENİ ÜRÜNLER
                depo_sum = depo_df.groupby('urun_kod')['stok'].sum()
                yeni_adaylar = depo_sum[depo_sum > 300].index.tolist()
                
                urun_magaza_count = df[df['urun_kod'].isin(yeni_adaylar)].groupby('urun_kod')['magaza_kod'].nunique()
                total_magaza = df['magaza_kod'].nunique()
                yeni_urunler = urun_magaza_count[urun_magaza_count < total_magaza * 0.5].index.tolist()
                
                # 3. SEGMENTASYON
                if (st.session_state.urun_segment_map and st.session_state.magaza_segment_map):
                    df['urun_segment'] = df['urun_kod'].map(st.session_state.urun_segment_map).fillna('0-4')
                    df['magaza_segment'] = df['magaza_kod'].map(st.session_state.magaza_segment_map).fillna('0-4')
                else:
                    df['urun_segment'] = '0-4'
                    df['magaza_segment'] = '0-4'
                
                # 4. KPI - GÜVENLİ VERSİYON
                default_fc = kpi_df['forward_cover'].mean() if 'forward_cover' in kpi_df.columns else 7.0
                
                # ÖNCE min_deger VE max_deger KOLONLARINI GÜVENLİ ŞEKİLDE EKLE
                df['min_deger'] = 0.0
                df['max_deger'] = 999999.0
                
                # MG bilgisini ekle - GÜVENLİ VERSİYON
                if st.session_state.urun_master is not None and 'mg' in st.session_state.urun_master.columns:
                    try:
                        urun_m = st.session_state.urun_master[['urun_kod', 'mg']].copy()
                        urun_m['urun_kod'] = urun_m['urun_kod'].astype(str)
                        urun_m['mg'] = urun_m['mg'].fillna('0').astype(str)
                        
                        df = df.merge(urun_m, on='urun_kod', how='left')
                        df['mg'] = df['mg'].fillna('0')
                    except Exception as e:
                        st.warning(f"⚠️ MG birleştirme hatası: {e}")
                        df['mg'] = '0'
                else:
                    df['mg'] = '0'
                
                # KPI verilerini güvenli şekilde uygula
                try:
                    if not kpi_df.empty and 'mg_id' in kpi_df.columns:
                        kpi_lookup = {}
                        for _, row in kpi_df.iterrows():
                            mg_key = str(row['mg_id'])
                            min_val = row.get('min_deger', 0)
                            max_val = row.get('max_deger', 999999)
                            
                            kpi_lookup[mg_key] = {
                                'min': float(min_val) if pd.notna(min_val) else 0,
                                'max': float(max_val) if pd.notna(max_val) else 999999
                            }
                        
                        # MG bazında güncelle
                        for mg_val in df['mg'].unique():
                            if mg_val in kpi_lookup:
                                mask = df['mg'] == mg_val
                                df.loc[mask, 'min_deger'] = kpi_lookup[mg_val]['min']
                                df.loc[mask, 'max_deger'] = kpi_lookup[mg_val]['max']
                                
                except Exception as e:
                    st.warning(f"⚠️ KPI atama hatası: {e}")
                    # Hata durumunda default değerleri kullan
                    df['min_deger'] = 0.0
                    df['max_deger'] = 999999.0
                
                # 5. MATRİS DEĞERLERİ - GÜVENLİ ATAMA
                # Önce bu kolonları oluştur
                df['genlestirme'] = 1.0
                df['sisme'] = 0.5
                df['min_oran'] = 1.0
                df['initial_katsayi'] = 1.0
                
                # Matris değerlerini segment bazında uygula
                if (st.session_state.genlestirme_orani is not None and 
                    st.session_state.sisme_orani is not None and
                    st.session_state.min_oran is not None and
                    st.session_state.initial_matris is not None):
                    
                    try:
                        for idx, row in df.iterrows():
                            urun_seg = str(row['urun_segment'])
                            magaza_seg = str(row['magaza_segment'])
                            
                            if (urun_seg in st.session_state.genlestirme_orani.index and 
                                magaza_seg in st.session_state.genlestirme_orani.columns):
                                df.at[idx, 'genlestirme'] = st.session_state.genlestirme_orani.loc[urun_seg, magaza_seg]
                            
                            if (urun_seg in st.session_state.sisme_orani.index and 
                                magaza_seg in st.session_state.sisme_orani.columns):
                                df.at[idx, 'sisme'] = st.session_state.sisme_orani.loc[urun_seg, magaza_seg]
                            
                            if (urun_seg in st.session_state.min_oran.index and 
                                magaza_seg in st.session_state.min_oran.columns):
                                df.at[idx, 'min_oran'] = st.session_state.min_oran.loc[urun_seg, magaza_seg]
                            
                            if (urun_seg in st.session_state.initial_matris.index and 
                                magaza_seg in st.session_state.initial_matris.columns):
                                df.at[idx, 'initial_katsayi'] = st.session_state.initial_matris.loc[urun_seg, magaza_seg]
                                
                    except Exception as e:
                        st.warning(f"⚠️ Matris değer atama hatası: {e}")
                
                # 6. RPT/MIN/INITIAL DURUMLARI
                rpt = df.copy()
                rpt['Durum'] = 'RPT'
                
                min_df = df.copy()
                min_df['Durum'] = 'Min'
                
                if yeni_urunler:
                    initial = df[df['urun_kod'].isin(yeni_urunler)].copy()
                    initial['Durum'] = 'Initial'
                    result = pd.concat([rpt, initial, min_df], ignore_index=True)
                else:
                    result = pd.concat([rpt, min_df], ignore_index=True)
                
                # 7. İHTİYAÇ HESAPLA
                result['ihtiyac_rpt'] = (default_fc * result['satis'] * result['genlestirme']) - (result['stok'] + result['yol'])
                result['ihtiyac_min'] = (result['min_oran'] * result['min_deger']) - (result['stok'] + result['yol'])
                result['ihtiyac_initial'] = (result['min_deger'] * result['initial_katsayi']) - (result['stok'] + result['yol'])
                
                result['ihtiyac'] = 0.0
                result.loc[result['Durum'] == 'RPT', 'ihtiyac'] = result['ihtiyac_rpt']
                result.loc[result['Durum'] == 'Min', 'ihtiyac'] = result['ihtiyac_min']
                result.loc[result['Durum'] == 'Initial', 'ihtiyac'] = result['ihtiyac_initial']
                
                # Negatif ihtiyaçları 0 yap
                result['ihtiyac'] = result['ihtiyac'].clip(lower=0)
                
                # 8. DEPO EŞLEŞTİR
                if 'depo_kod' in magaza_df.columns:
                    result = result.merge(magaza_df[['magaza_kod', 'depo_kod']], on='magaza_kod', how='left')
                else:
                    result['depo_kod'] = 'DEPO_01'  # Fallback değer
                
                # 9. YASAK KONTROL
                if (st.session_state.yasak_master is not None and 
                    'urun_kod' in st.session_state.yasak_master.columns and
                    'magaza_kod' in st.session_state.yasak_master.columns):
                    
                    yasak = st.session_state.yasak_master.copy()
                    yasak['urun_kod'] = yasak['urun_kod'].astype(str)
                    yasak['magaza_kod'] = yasak['magaza_kod'].astype(str)
                    
                    # Sadece yasak_durum kolonu varsa kullan
                    if 'yasak_durum' in yasak.columns:
                        result = result.merge(
                            yasak[['urun_kod', 'magaza_kod', 'yasak_durum']], 
                            on=['urun_kod', 'magaza_kod'], 
                            how='left'
                        )
                        result.loc[result['yasak_durum'] == 'Yasak', 'ihtiyac'] = 0
                
                # 10. DEPO STOK DAĞITIMI
                result = result[result['ihtiyac'] > 0].copy()
                
                # Depo stok sözlüğü oluştur
                depo_dict = {}
                for _, row in depo_df.iterrows():
                    depo_kod = str(row.get('depo_kod', 'DEPO_01'))
                    urun_kod = str(row['urun_kod'])
                    key = (depo_kod, urun_kod)
                    depo_dict[key] = float(row['stok'])
                
                # Öncelik sıralaması
                if st.session_state.siralama_data is not None:
                    siralama_df = st.session_state.siralama_data.copy()
                    # Sıralama mantığı burada uygulanacak
                    # Basit sıralama için:
                    result = result.sort_values(['Durum', 'ihtiyac'], ascending=[True, False])
                else:
                    result = result.sort_values(['Durum', 'ihtiyac'], ascending=[True, False])
                
                # Sevkiyat hesapla
                sevkiyat_list = []
                for _, row in result.iterrows():
                    depo_kod = str(row.get('depo_kod', 'DEPO_01'))
                    urun_kod = str(row['urun_kod'])
                    key = (depo_kod, urun_kod)
                    ihtiyac = float(row['ihtiyac'])
                    
                    if key in depo_dict and depo_dict[key] > 0:
                        sevk = min(ihtiyac, depo_dict[key])
                        depo_dict[key] -= sevk
                        sevkiyat_list.append(sevk)
                    else:
                        sevkiyat_list.append(0.0)
                
                result['sevkiyat_miktari'] = sevkiyat_list
                result['stok_yoklugu_satis_kaybi'] = result['ihtiyac'] - result['sevkiyat_miktari']
                
                # 11. SONUÇ HAZIRLA
                final_columns = [
                    'magaza_kod', 'urun_kod', 'magaza_segment', 'urun_segment', 'Durum',
                    'stok', 'yol', 'satis', 'ihtiyac', 'sevkiyat_miktari', 'depo_kod', 'stok_yoklugu_satis_kaybi'
                ]
                
                # Sadece mevcut kolonları kullan
                available_columns = [col for col in final_columns if col in result.columns]
                final = result[available_columns].copy()
                
                final = final.rename(columns={
                    'Durum': 'durum',
                    'ihtiyac': 'ihtiyac_miktari'
                })
                
                # Integer dönüşüm
                for col in ['stok', 'yol', 'satis', 'ihtiyac_miktari', 'sevkiyat_miktari', 'stok_yoklugu_satis_kaybi']:
                    if col in final.columns:
                        final[col] = final[col].round().fillna(0).astype(int)
                
                # Sıra numaraları
                final.insert(0, 'sira_no', range(1, len(final) + 1))
                final.insert(1, 'oncelik', range(1, len(final) + 1))
                
                # KAYDET
                st.session_state.sevkiyat_sonuc = final
                
                st.success(f"✅ Hesaplama tamamlandı! {len(final):,} satır oluşturuldu.")
                
                # ÖZET
                col1, col2, col3 = st.columns(3)
                with col1:
                    ihtiyac_toplam = final['ihtiyac_miktari'].sum() if 'ihtiyac_miktari' in final.columns else 0
                    st.metric("Toplam İhtiyaç", f"{ihtiyac_toplam:,.0f}")
                with col2:
                    sevkiyat_toplam = final['sevkiyat_miktari'].sum() if 'sevkiyat_miktari' in final.columns else 0
                    st.metric("Toplam Sevkiyat", f"{sevkiyat_toplam:,.0f}")
                with col3:
                    kayip_toplam = final['stok_yoklugu_satis_kaybi'].sum() if 'stok_yoklugu_satis_kaybi' in final.columns else 0
                    st.metric("Satış Kaybı", f"{kayip_toplam:,.0f}")
                
            except Exception as e:
                st.error(f"❌ Hesaplama hatası: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

# ============================================
# 📈 RAPORLAR - TAMAMI DÜZELTİLMİŞ (GİRİNTİ SORUNU ÇÖZÜLDÜ)
# ============================================
elif menu == "📈 Raporlar":
    st.title("📈 Raporlar ve Analizler")
    st.markdown("---")
    
    # Hata ayıklama için session state kontrolü
    st.write("**🔍 Debug: Session State Kontrolü**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"Sevkiyat Sonucu: {'✅ Var' if st.session_state.sevkiyat_sonuc is not None else '❌ Yok'}")
        if st.session_state.sevkiyat_sonuc is not None:
            st.write(f"Satır: {len(st.session_state.sevkiyat_sonuc)}")
    
    with col2:
        st.write(f"Ürün Master: {'✅ Var' if st.session_state.urun_master is not None else '❌ Yok'}")
    
    with col3:
        st.write(f"Mağaza Master: {'✅ Var' if st.session_state.magaza_master is not None else '❌ Yok'}")
    
    if st.session_state.sevkiyat_sonuc is None:
        st.error("⚠️ Henüz hesaplama yapılmadı!")
        st.info("Lütfen önce 'Hesaplama' menüsünden hesaplama yapın.")
        
    else:
        result_df = st.session_state.sevkiyat_sonuc.copy()
        
        # Debug: Veri yapısını göster
        with st.expander("🔍 Veri Yapısı (Debug)", expanded=False):
            st.write("**Kolonlar:**", list(result_df.columns))
            st.write("**İlk 5 satır:**")
            st.dataframe(result_df.head(), width='content')
            st.write("**Temel İstatistikler:**")
            st.write(f"- Toplam satır: {len(result_df)}")
            
            # KOLON ADI DÜZELTMESİ
            sevkiyat_kolon_adi = 'sevkiyat_miktari' if 'sevkiyat_miktari' in result_df.columns else 'sevkiyat_gercek'
            ihtiyac_kolon_adi = 'ihtiyac_miktari' if 'ihtiyac_miktari' in result_df.columns else 'ihtiyac'
            kayip_kolon_adi = 'stok_yoklugu_satis_kaybi' if 'stok_yoklugu_satis_kaybi' in result_df.columns else 'stok_yoklugu_kaybi'
            
            if sevkiyat_kolon_adi in result_df.columns:
                st.write(f"- Sevkiyat miktarı > 0: {(result_df[sevkiyat_kolon_adi] > 0).sum()}")
            if ihtiyac_kolon_adi in result_df.columns:
                st.write(f"- İhtiyaç miktarı > 0: {(result_df[ihtiyac_kolon_adi] > 0).sum()}")
        
        tab1, tab2, tab3, tab4 = st.tabs([
            "📦 Ürün Analizi",
            "🏪 Mağaza Analizi", 
            "⚠️ Satış Kaybı Analizi",
            "🗺️ İl Bazında Harita"
        ])
        
        # ============================================
        # ÜRÜN ANALİZİ - DÜZELTİLMİŞ
        # ============================================
        with tab1:
            st.subheader("📦 Ürün Bazında Analiz")
            
            # KOLON ADI DÜZELTMESİ
            sevkiyat_kolon = 'sevkiyat_miktari' if 'sevkiyat_miktari' in result_df.columns else 'sevkiyat_gercek'
            ihtiyac_kolon = 'ihtiyac_miktari' if 'ihtiyac_miktari' in result_df.columns else 'ihtiyac'
            kayip_kolon = 'stok_yoklugu_satis_kaybi' if 'stok_yoklugu_satis_kaybi' in result_df.columns else 'stok_yoklugu_kaybi'
            
            # Ürün bazında toplamlar
            urun_sevkiyat = result_df.groupby('urun_kod').agg({
                ihtiyac_kolon: 'sum',
                sevkiyat_kolon: 'sum',
                kayip_kolon: 'sum',
                'magaza_kod': 'nunique'
            }).reset_index()

            urun_sevkiyat.columns = ['urun_kod', 'İhtiyaç', 'Sevkiyat', 'Satış Kaybı', 'Mağaza Sayısı']
            
            # Hesaplamalar
            urun_sevkiyat['Sevkiyat/İhtiyaç %'] = np.where(
                urun_sevkiyat['İhtiyaç'] > 0,
                (urun_sevkiyat['Sevkiyat'] / urun_sevkiyat['İhtiyaç'] * 100),
                0
            ).round(2)
            
            urun_sevkiyat['Kayıp Oranı %'] = np.where(
                urun_sevkiyat['İhtiyaç'] > 0,
                (urun_sevkiyat['Satış Kaybı'] / urun_sevkiyat['İhtiyaç'] * 100),
                0
            ).round(2)
            
            # Marka bilgilerini ekle (eğer varsa)
            if st.session_state.urun_master is not None:
                urun_detay = st.session_state.urun_master[['urun_kod', 'marka_kod']].copy()
                urun_detay['urun_kod'] = urun_detay['urun_kod'].astype(str)
                urun_sevkiyat['urun_kod'] = urun_sevkiyat['urun_kod'].astype(str)
                
                urun_sevkiyat = urun_sevkiyat.merge(urun_detay, on='urun_kod', how='left')
                
                # Kolon sıralaması
                urun_sevkiyat = urun_sevkiyat[[
                    'urun_kod', 'marka_kod', 
                    'İhtiyaç', 'Sevkiyat', 'Sevkiyat/İhtiyaç %', 
                    'Satış Kaybı', 'Kayıp Oranı %', 'Mağaza Sayısı'
                ]]
                
                urun_sevkiyat.columns = [
                    'Ürün Kodu', 'Marka Kodu', 
                    'İhtiyaç', 'Sevkiyat', 'Sevkiyat/İhtiyaç %',
                    'Satış Kaybı', 'Kayıp Oranı %', 'Mağaza Sayısı'
                ]
            else:
                # Ürün master yoksa sadece kodlarla çalış
                urun_sevkiyat.columns = [
                    'Ürün Kodu', 'İhtiyaç', 'Sevkiyat', 'Satış Kaybı', 'Mağaza Sayısı',
                    'Sevkiyat/İhtiyaç %', 'Kayıp Oranı %'
                ]
            
            # En yüksek sevkiyatlı 10 ürün
            top_10_urun = urun_sevkiyat.nlargest(10, 'Sevkiyat')
            
            # Metrikler
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Toplam Ürün", len(urun_sevkiyat))
            with col2:
                st.metric("Toplam İhtiyaç", f"{urun_sevkiyat['İhtiyaç'].sum():,.0f}")
            with col3:
                st.metric("Toplam Sevkiyat", f"{urun_sevkiyat['Sevkiyat'].sum():,.0f}")
            with col4:
                toplam_kayip = urun_sevkiyat['Satış Kaybı'].sum()
                st.metric("Toplam Kayıp", f"{toplam_kayip:,.0f}")
            
            st.markdown("---")
            
            # Filtreleme seçenekleri
            col1, col2 = st.columns(2)
            with col1:
                min_sevkiyat = st.number_input("Min Sevkiyat Filtresi", 
                                             min_value=0, 
                                             value=0,
                                             help="Sadece bu değerden yüksek sevkiyatı olan ürünleri göster")
            
            with col2:
                min_mağaza = st.number_input("Min Mağaza Sayısı", 
                                           min_value=0, 
                                           value=0,
                                           help="Sadece bu sayıdan fazla mağazada bulunan ürünleri göster")
            
            # Filtrele
            filtered_urun = urun_sevkiyat[
                (urun_sevkiyat['Sevkiyat'] >= min_sevkiyat) & 
                (urun_sevkiyat['Mağaza Sayısı'] >= min_mağaza)
            ]
            
            st.write(f"**Filtrelenmiş Ürün Sayısı:** {len(filtered_urun)}")
            
            # Tablolar
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📊 Ürün Performans Tablosu")
                st.dataframe(
                    filtered_urun.style.format({
                        'İhtiyaç': '{:,.0f}',
                        'Sevkiyat': '{:,.0f}',
                        'Sevkiyat/İhtiyaç %': '{:.1f}%',
                        'Satış Kaybı': '{:,.0f}',
                        'Kayıp Oranı %': '{:.1f}%',
                        'Mağaza Sayısı': '{:.0f}'
                    }),
                    width='content',
                    height=400
                )
            
            with col2:
                st.subheader("🏆 En İyi Performans")
                if len(filtered_urun) > 0:
                    best_coverage = filtered_urun.nlargest(5, 'Sevkiyat/İhtiyaç %')[['Ürün Kodu', 'Sevkiyat/İhtiyaç %']]
                    st.dataframe(best_coverage, width='content')
                
                st.subheader("⚠️ En Fazla Kayıp")
                if len(filtered_urun) > 0:
                    worst_loss = filtered_urun.nlargest(5, 'Satış Kaybı')[['Ürün Kodu', 'Satış Kaybı']]
                    st.dataframe(worst_loss, width='content')
            
            st.markdown("---")
            
            # Grafikler
            col1, col2 = st.columns(2)
            
            with col1:
                if len(top_10_urun) > 0:
                    st.write("**Top 10 Ürün - Sevkiyat Miktarı**")
                    grafik_df = top_10_urun.set_index('Ürün Kodu')[['Sevkiyat']]
                    st.bar_chart(grafik_df)
            
            with col2:
                if len(filtered_urun) > 0:
                    st.write("**Sevkiyat/İhtiyaç Oranı Dağılımı**")
                    oran_dagilim = filtered_urun['Sevkiyat/İhtiyaç %'].value_counts(bins=10).sort_index()
                    # Grafik etiketlerini düzelt
                    oran_dagilim.index = [f"%{int(interval.left)}-%{int(interval.right)}" for interval in oran_dagilim.index]
                    st.bar_chart(oran_dagilim)
            
            st.markdown("---")
            
            # İndirme butonları
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Tüm Ürün Analizi İndir (CSV)",
                    data=urun_sevkiyat.to_csv(index=False, encoding='utf-8-sig'),
                    file_name="urun_analizi_tum.csv",
                    mime="text/csv",
                    width='content'
                )
            with col2:
                st.download_button(
                    label="📥 Filtrelenmiş Ürünler İndir (CSV)",
                    data=filtered_urun.to_csv(index=False, encoding='utf-8-sig'),
                    file_name="urun_analizi_filtreli.csv",
                    mime="text/csv",
                    width='content'
                )

# ============================================
# 💾 MASTER DATA OLUŞTURMA
# ============================================
elif menu == "💾 Master Data":
    st.title("💾 Master Data Oluşturma")
    st.markdown("---")
    
    st.warning("🚧 **Master Data modülü yakında yayında!** 🚧")
