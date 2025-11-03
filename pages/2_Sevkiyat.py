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


# ⬇️ BURAYI EKLEYİN ⬇️
# Segmentation parametrelerini başlat
if 'segmentation_params' not in st.session_state:
    st.session_state.segmentation_params = {
        'product_ranges': [(0, 2), (2, 4), (4, float('inf'))],
        'store_ranges': [(0, 2), (2, 4), (4, float('inf'))]
    }


# Session state başlatma
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
if 'segmentation_params' not in st.session_state:
    st.session_state.segmentation_params = {
        'product_ranges': [(0, 4), (5, 8), (9, 12), (12, 15), (15, 20), (20, float('inf'))],
        'store_ranges': [(0, 4), (5, 8), (9, 12), (12, 15), (15, 20), (20, float('inf'))]
    }
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
if 'siralama_data' not in st.session_state:
    st.session_state.siralama_data = None
if 'sevkiyat_sonuc' not in st.session_state:
    st.session_state.sevkiyat_sonuc = None
if 'yeni_urun_listesi' not in st.session_state:
    st.session_state.yeni_urun_listesi = None

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
# 🎲 HEDEF MATRİS
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
            """Segmentleri numerik değere göre sıralar: 0-4, 5-8, 9-12, 15-20, 20-inf"""
            def get_sort_key(seg):
                try:
                    # İlk sayıyı al (0-4 -> 0, 5-8 -> 5, 20-inf -> 20)
                    return int(seg.split('-')[0])
                except:
                    return 9999  # inf veya parse edilemeyen değerler en sona
            
            return sorted(segments, key=get_sort_key)
        
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
        
        # Matris seçimi ve parametreler
        st.subheader("🎯 Matris Parametreleri")
        
        # Segmentleri string olarak al ve SIRALA
        prod_segments_raw = [str(x) for x in urun_aggregated['urun_segment'].unique() if pd.notna(x)]
        store_segments_raw = [str(x) for x in magaza_aggregated['magaza_segment'].unique() if pd.notna(x)]
        
        prod_segments = sort_segments(prod_segments_raw)
        store_segments = sort_segments(store_segments_raw)
        
        st.info(f"**Ürün Segmentleri:** {', '.join(prod_segments)}")
        st.info(f"**Mağaza Segmentleri:** {', '.join(store_segments)}")
        
        # 1. ŞİŞME ORANI MATRİSİ
        st.markdown("### 1️⃣ Şişme Oranı Matrisi (Default: 0.5)")
        
        if st.session_state.sisme_orani is None or len(st.session_state.sisme_orani) == 0:
            sisme_data = pd.DataFrame(0.5, index=prod_segments, columns=store_segments)
        else:
            # Mevcut matrisi kontrol et ve eksikleri doldur
            sisme_data = st.session_state.sisme_orani.copy()
            
            # Eksik satırları ekle
            for seg in prod_segments:
                if seg not in sisme_data.index:
                    sisme_data.loc[seg] = 0.5
            
            # Eksik kolonları ekle
            for seg in store_segments:
                if seg not in sisme_data.columns:
                    sisme_data[seg] = 0.5
            
            # Sıralama - ÖNEMLİ!
            sisme_data = sisme_data.reindex(index=prod_segments, columns=store_segments, fill_value=0.5)
        
        edited_sisme = st.data_editor(
            sisme_data,
            width='content',
            column_config={col: st.column_config.NumberColumn(
                col, min_value=0.0, max_value=10.0, step=0.1, format="%.2f"
            ) for col in store_segments},
            key="sisme_matrix"
        )
        
        st.markdown("---")
        
        # 2. GENLEŞTİRME ORANI MATRİSİ
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
            
            # Sıralama - ÖNEMLİ!
            genlestirme_data = genlestirme_data.reindex(index=prod_segments, columns=store_segments, fill_value=1.0)
        
        edited_genlestirme = st.data_editor(
            genlestirme_data,
            width='content',
            column_config={col: st.column_config.NumberColumn(
                col, min_value=0.0, max_value=10.0, step=0.1, format="%.2f"
            ) for col in store_segments},
            key="genlestirme_matrix"
        )
        
        st.markdown("---")
        
        # 3. MIN ORAN MATRİSİ
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
            
            # Sıralama - ÖNEMLİ!
            min_oran_data = min_oran_data.reindex(index=prod_segments, columns=store_segments, fill_value=1.0)
        
        edited_min_oran = st.data_editor(
            min_oran_data,
            width='content',
            column_config={col: st.column_config.NumberColumn(
                col, min_value=0.0, max_value=10.0, step=0.1, format="%.2f"
            ) for col in store_segments},
            key="min_oran_matrix"
        )
        
        st.markdown("---")
        
        # 4. INITIAL MATRİSİ
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
            
            # Sıralama - ÖNEMLİ!
            initial_data = initial_data.reindex(index=prod_segments, columns=store_segments, fill_value=1.0)
        
        edited_initial = st.data_editor(
            initial_data,
            width='content',
            column_config={col: st.column_config.NumberColumn(
                col, min_value=0.0, max_value=10.0, step=0.1, format="%.2f"
            ) for col in store_segments},
            key="initial_matrix"
        )
        
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
# 📊 SIRALAMA
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
        urun_aggregated['urun_segment'] = pd.cut(
            urun_aggregated['stok_satis_orani'], 
            bins=[r[0] for r in product_ranges] + [product_ranges[-1][1]],
            labels=[f"{r[0]}-{r[1]}" for r in product_ranges],
            include_lowest=True
        )
        
        store_ranges = st.session_state.segmentation_params['store_ranges']
        magaza_aggregated['magaza_segment'] = pd.cut(
            magaza_aggregated['stok_satis_orani'],
            bins=[r[0] for r in store_ranges] + [store_ranges[-1][1]],
            labels=[f"{r[0]}-{r[1]}" for r in store_ranges],
            include_lowest=True
        )
        
        prod_segments = sorted([str(x) for x in urun_aggregated['urun_segment'].unique() if pd.notna(x)])
        store_segments = sorted([str(x) for x in magaza_aggregated['magaza_segment'].unique() if pd.notna(x)])
        
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
# 🚚 HESAPLAMA - DÜZELTİLMİŞ (TAMSAYI DÖNÜŞÜMÜ)
# ============================================
elif menu == "📐 Hesaplama":
    st.title("📐 Hesaplama")
    st.markdown("---")
    
    # Session state kontrolü - önceki sonuçları koru
    if 'sevkiyat_sonuc' not in st.session_state:
        st.session_state.sevkiyat_sonuc = None
    
    # Daha önce hesaplanmış sonuç varsa göster
    if st.session_state.sevkiyat_sonuc is not None:
        st.success("✅ Daha önce hesaplanmış sevkiyat sonuçları mevcut!")
        
        # Önceki sonuçları hızlıca göster
        result_final = st.session_state.sevkiyat_sonuc.copy()
        
        # Özet metrikler
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 Toplam İhtiyaç", f"{result_final['ihtiyac_miktari'].sum():,.0f}")
        with col2:
            st.metric("✅ Toplam Sevkiyat", f"{result_final['sevkiyat_miktari'].sum():,.0f}")
        with col3:
            st.metric("⚠️ Satış Kaybı", f"{result_final['stok_yoklugu_satis_kaybi'].sum():,.0f}")
        with col4:
            st.metric("🏪 Mağaza Sayısı", f"{result_final['magaza_kod'].nunique()}")
        
        st.info("Yeni hesaplama yapmak isterseniz aşağıdaki butonu kullanın.")
        st.markdown("---")
    
    required_data = {
        "Ürün Master": st.session_state.urun_master,
        "Mağaza Master": st.session_state.magaza_master,
        "Anlık Stok/Satış": st.session_state.anlik_stok_satis,
        "Depo Stok": st.session_state.depo_stok,
        "KPI": st.session_state.kpi
    }
    
    optional_data = {
        "Haftalık Trend": st.session_state.haftalik_trend,
        "Yasak Master": st.session_state.yasak_master
    }
    
    missing_data = [name for name, data in required_data.items() if data is None]
    optional_loaded = [name for name, data in optional_data.items() if data is not None]
    
    if missing_data:
        st.warning("⚠️ Tüm zorunlu verileri yükleyin!")
        st.error(f"**Eksik:** {', '.join(missing_data)}")
        st.info("""
        Zorunlu: Ürün Master, Mağaza Master, Depo Stok, Anlık Stok/Satış, KPI
        Opsiyonel: Segmentasyon, Matrisler, Sıralama, Haftalık Trend, Yasak
        """)
        if optional_loaded:
            st.success(f"✅ Yüklü opsiyonel: {', '.join(optional_loaded)}")
    else:
        if st.session_state.sevkiyat_sonuc is None:
            st.success("✅ Tüm zorunlu veriler hazır! Hesaplama yapabilirsiniz.")
        else:
            st.success("✅ Tüm zorunlu veriler hazır! Yeni hesaplama yapabilir veya mevcut sonuçları kullanabilirsiniz.")
        
        if optional_loaded:
            st.info(f"📌 Opsiyonel: {', '.join(optional_loaded)}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Toplam Ürün", st.session_state.anlik_stok_satis['urun_kod'].nunique())
        with col2:
            st.metric("Toplam Mağaza", st.session_state.anlik_stok_satis['magaza_kod'].nunique())
        with col3:
            st.metric("Depo Stok", f"{st.session_state.depo_stok['stok'].sum():,.0f}")
        with col4:
            yasak_count = len(st.session_state.yasak_master) if st.session_state.yasak_master is not None else 0
            st.metric("Yasak", yasak_count)
        
        st.markdown("---")
              
        if st.button("🚀 Sevkiyat Hesapla", type="primary", width='stretch', key="hesapla_btn"):
            start_time = time.time()
           
            with st.spinner("📊 Hesaplama yapılıyor..."):
                progress_bar = st.progress(0, text="Veri hazırlanıyor...")
                
                anlik_df = st.session_state.anlik_stok_satis.copy()
                magaza_df = st.session_state.magaza_master.copy()
                depo_df = st.session_state.depo_stok.copy()
                kpi_df = st.session_state.kpi.copy()
                
                # Default matrisler - DÜZELTİLMİŞ VERSİYON
                if 'sisme_orani' not in st.session_state or st.session_state.sisme_orani is None:
                    st.session_state.sisme_orani = pd.DataFrame(0.5, index=["0-4"], columns=["0-4"])
                if 'genlestirme_orani' not in st.session_state or st.session_state.genlestirme_orani is None:
                    st.session_state.genlestirme_orani = pd.DataFrame(1.0, index=["0-4"], columns=["0-4"])
                if 'min_orani' not in st.session_state or st.session_state.min_orani is None:
                    st.session_state.min_orani = pd.DataFrame(1.0, index=["0-4"], columns=["0-4"])
                if 'initial_matris' not in st.session_state or st.session_state.initial_matris is None:
                    st.session_state.initial_matris = pd.DataFrame(1.0, index=["0-4"], columns=["0-4"])
                progress_bar.progress(10, text="Yeni ürünler tespit ediliyor...")

                # YENİ ÜRÜN TESPİTİ
                depo_df_temp = depo_df.copy()
                depo_df_temp['urun_kod'] = depo_df_temp['urun_kod'].astype(str).apply(
                    lambda x: str(int(float(x))) if '.' in str(x) else str(x)
                )
                depo_toplam = depo_df_temp.groupby('urun_kod')['stok'].sum().reset_index()
                depo_toplam.columns = ['urun_kod', 'depo_stok_toplam']
                yeni_urun_adaylari = depo_toplam[depo_toplam['depo_stok_toplam'] > 300]['urun_kod'].tolist()
                
                toplam_magaza_sayisi = anlik_df['magaza_kod'].nunique()
                anlik_df['urun_kod'] = anlik_df['urun_kod'].astype(str)
                urun_magaza_stok = anlik_df[anlik_df['urun_kod'].isin(yeni_urun_adaylari)].copy()
                urun_magaza_stok = urun_magaza_stok[urun_magaza_stok['stok'] > 0]
                
                urun_stoklu_magaza = urun_magaza_stok.groupby('urun_kod')['magaza_kod'].nunique().reset_index()
                urun_stoklu_magaza.columns = ['urun_kod', 'stoklu_magaza_sayisi']
                urun_stoklu_magaza['magaza_oran'] = urun_stoklu_magaza['stoklu_magaza_sayisi'] / toplam_magaza_sayisi
                
                yeni_urunler = urun_stoklu_magaza[urun_stoklu_magaza['magaza_oran'] < 0.5].copy()
                yeni_urun_kodlari = yeni_urunler['urun_kod'].tolist()
                
                st.session_state.yeni_urun_listesi = yeni_urunler.merge(depo_toplam, on='urun_kod', how='left')
                
                progress_bar.progress(25, text="Segmentasyon yapılıyor...")
                
                # Segmentasyon
                urun_agg = anlik_df.groupby('urun_kod').agg({'stok': 'sum', 'satis': 'sum'}).reset_index()
                urun_agg['cover'] = urun_agg['stok'] / urun_agg['satis'].replace(0, 1)
                
                magaza_agg = anlik_df.groupby('magaza_kod').agg({'stok': 'sum', 'satis': 'sum'}).reset_index()
                magaza_agg['cover'] = magaza_agg['stok'] / magaza_agg['satis'].replace(0, 1)
                
                product_ranges = st.session_state.segmentation_params['product_ranges']
                store_ranges = st.session_state.segmentation_params['store_ranges']
                
                product_labels = [f"{int(r[0])}-{int(r[1]) if r[1] != float('inf') else 'inf'}" for r in product_ranges]
                store_labels = [f"{int(r[0])}-{int(r[1]) if r[1] != float('inf') else 'inf'}" for r in store_ranges]
                
                urun_agg['segment'] = pd.cut(
                    urun_agg['cover'],
                    bins=[r[0] for r in product_ranges] + [product_ranges[-1][1]],
                    labels=product_labels,
                    include_lowest=True
                )
                
                magaza_agg['segment'] = pd.cut(
                    magaza_agg['cover'],
                    bins=[r[0] for r in store_ranges] + [store_ranges[-1][1]],
                    labels=store_labels,
                    include_lowest=True
                )
                
                anlik_df = anlik_df.merge(urun_agg[['urun_kod', 'segment']], on='urun_kod', how='left').rename(columns={'segment': 'urun_segment'})
                anlik_df = anlik_df.merge(magaza_agg[['magaza_kod', 'segment']], on='magaza_kod', how='left').rename(columns={'segment': 'magaza_segment'})
                
                anlik_df['urun_segment'] = anlik_df['urun_segment'].astype(str)
                anlik_df['magaza_segment'] = anlik_df['magaza_segment'].astype(str)
                
                progress_bar.progress(40, text="KPI verileri hazırlanıyor...")
                
                # KPI
                default_fc = kpi_df['forward_cover'].mean()
                
                if st.session_state.urun_master is not None:
                    urun_master = st.session_state.urun_master[['urun_kod', 'mg']].copy()
                    urun_master['urun_kod'] = urun_master['urun_kod'].astype(str)
                    anlik_df['urun_kod'] = anlik_df['urun_kod'].astype(str)
                    urun_master['mg'] = urun_master['mg'].fillna(0).astype(float).astype(int).astype(str)
                    
                    anlik_df = anlik_df.merge(urun_master, on='urun_kod', how='left')
                    
                    kpi_data = kpi_df[['mg_id', 'min_deger', 'max_deger']].rename(columns={'mg_id': 'mg'})
                    kpi_data['mg'] = kpi_data['mg'].astype(str)
                    anlik_df['mg'] = anlik_df['mg'].astype(str)
                    
                    anlik_df = anlik_df.merge(kpi_data, on='mg', how='left')
                    anlik_df['min_deger'] = anlik_df['min_deger'].fillna(0)
                    anlik_df['max_deger'] = anlik_df['max_deger'].fillna(999999)
                else:
                    anlik_df['min_deger'] = 0
                    anlik_df['max_deger'] = 999999
                
                progress_bar.progress(55, text="Matris değerleri uygulanıyor...")
                
                # Matris değerleri
                def get_matrix_value(magaza_seg, urun_seg, matrix):
                    try:
                        return matrix.loc[urun_seg, magaza_seg]
                    except:
                        return 1.0
                
                anlik_df['genlestirme'] = anlik_df.apply(
                    lambda row: get_matrix_value(row['magaza_segment'], row['urun_segment'], st.session_state.genlestirme_orani), axis=1
                )
                anlik_df['sisme'] = anlik_df.apply(
                    lambda row: get_matrix_value(row['magaza_segment'], row['urun_segment'], st.session_state.sisme_orani), axis=1
                )
                anlik_df['min_oran'] = anlik_df.apply(
                    lambda row: get_matrix_value(row['magaza_segment'], row['urun_segment'], st.session_state.min_orani), axis=1
                )
                anlik_df['initial_katsayi'] = anlik_df.apply(
                    lambda row: get_matrix_value(row['magaza_segment'], row['urun_segment'], st.session_state.initial_matris), axis=1
                )
                
                progress_bar.progress(70, text="İhtiyaçlar hesaplanıyor...")
                
                # RPT, Initial, Min satırları oluştur
                anlik_rpt = anlik_df.copy()
                anlik_rpt['Durum'] = 'RPT'
                
                anlik_min = anlik_df.copy()
                anlik_min['Durum'] = 'Min'
                
                if len(yeni_urun_kodlari) > 0:
                    anlik_initial = anlik_df[anlik_df['urun_kod'].astype(str).isin(yeni_urun_kodlari)].copy()
                    anlik_initial['Durum'] = 'Initial'
                    anlik_df = pd.concat([anlik_rpt, anlik_initial, anlik_min], ignore_index=True)
                else:
                    anlik_df = pd.concat([anlik_rpt, anlik_min], ignore_index=True)
                
                # Sıralama
                if st.session_state.siralama_data is not None:
                    siralama_df = st.session_state.siralama_data.copy()
                else:
                    prod_segments = sorted([str(x) for x in urun_agg['segment'].unique() if pd.notna(x)])
                    store_segments = sorted([str(x) for x in magaza_agg['segment'].unique() if pd.notna(x)])
                    
                    siralama_rows = []
                    oncelik_counter = 1
                    for store_seg in store_segments:
                        for prod_seg in prod_segments:
                            siralama_rows.append({'Magaza_Cluster': store_seg, 'Urun_Cluster': prod_seg, 'Durum': 'RPT', 'Oncelik': oncelik_counter})
                            oncelik_counter += 1
                            siralama_rows.append({'Magaza_Cluster': store_seg, 'Urun_Cluster': prod_seg, 'Durum': 'Initial', 'Oncelik': oncelik_counter})
                            oncelik_counter += 1
                            siralama_rows.append({'Magaza_Cluster': store_seg, 'Urun_Cluster': prod_seg, 'Durum': 'Min', 'Oncelik': oncelik_counter})
                            oncelik_counter += 1
                    
                    siralama_df = pd.DataFrame(siralama_rows)
                
                anlik_df = anlik_df.merge(
                    siralama_df,
                    left_on=['magaza_segment', 'urun_segment', 'Durum'],
                    right_on=['Magaza_Cluster', 'Urun_Cluster', 'Durum'],
                    how='left'
                )
                
                # İhtiyaç hesapla
                anlik_df['ihtiyac_rpt'] = (default_fc * anlik_df['satis'] * anlik_df['genlestirme']) - (anlik_df['stok'] + anlik_df['yol'])
                anlik_df['ihtiyac_min'] = (anlik_df['min_oran'] * anlik_df['min_deger']) - (anlik_df['stok'] + anlik_df['yol'])
                anlik_df['ihtiyac_initial'] = (anlik_df['min_deger'] * anlik_df['initial_katsayi']) - (anlik_df['stok'] + anlik_df['yol'])
                
                anlik_df['ihtiyac'] = anlik_df.apply(
                    lambda row: (row['ihtiyac_rpt'] if row['Durum'] == 'RPT' 
                                else row['ihtiyac_min'] if row['Durum'] == 'Min'
                                else row['ihtiyac_initial']),
                    axis=1
                )
                
                anlik_df['ihtiyac'] = anlik_df['ihtiyac'].clip(lower=0)
                
                # max_deger kontrolü
                anlik_df['max_sevkiyat'] = anlik_df['max_deger'] - (anlik_df['stok'] + anlik_df['yol'])
                anlik_df['max_sevkiyat'] = anlik_df['max_sevkiyat'].clip(lower=0)
                anlik_df['ihtiyac'] = anlik_df.apply(
                    lambda row: min(row['ihtiyac'], row['max_sevkiyat']) if pd.notna(row['max_sevkiyat']) else row['ihtiyac'],
                    axis=1
                )
                
                progress_bar.progress(85, text="Yasak kontrolleri ve depo eşleştirme...")
                
                # Yasak kontrolü
                if st.session_state.yasak_master is not None:
                    yasak_df = st.session_state.yasak_master.copy()
                    yasak_df['urun_kod'] = yasak_df['urun_kod'].astype(str)
                    yasak_df['magaza_kod'] = yasak_df['magaza_kod'].astype(str)
                    anlik_df['urun_kod'] = anlik_df['urun_kod'].astype(str)
                    anlik_df['magaza_kod'] = anlik_df['magaza_kod'].astype(str)
                    
                    anlik_df = anlik_df.merge(yasak_df[['urun_kod', 'magaza_kod', 'yasak_durum']], on=['urun_kod', 'magaza_kod'], how='left')
                    anlik_df.loc[anlik_df['yasak_durum'] == 'Yasak', 'ihtiyac'] = 0
                
                # Depo eşleşmesi
                magaza_df['magaza_kod'] = magaza_df['magaza_kod'].astype(str)
                anlik_df['magaza_kod'] = anlik_df['magaza_kod'].astype(str)
                anlik_df = anlik_df.merge(magaza_df[['magaza_kod', 'depo_kod']], on='magaza_kod', how='left')
                
                progress_bar.progress(95, text="Depo stok kontrolleri yapılıyor...")
                
                # Önceliğe göre sırala
                result_df = anlik_df[anlik_df['ihtiyac'] > 0].copy()
                result_df_max = result_df.loc[result_df.groupby(['magaza_kod', 'urun_kod'])['ihtiyac'].idxmax()].copy()
                result_df_max = result_df_max.sort_values('Oncelik').reset_index(drop=True)

                # Depo stok kontrolü
                depo_stok_dict = {}
                for _, row in depo_df.iterrows():
                    depo_kod_str = str(row['depo_kod'])
                    urun_kod_raw = str(row['urun_kod'])
                    try:
                        if '.' in urun_kod_raw:
                            urun_kod_str = str(int(float(urun_kod_raw)))
                        else:
                            urun_kod_str = urun_kod_raw
                    except:
                        urun_kod_str = urun_kod_raw
                    
                    key = (depo_kod_str, urun_kod_str)
                    if key not in depo_stok_dict:
                        depo_stok_dict[key] = float(row['stok'])
                
                result_df_max['urun_kod_clean'] = result_df_max['urun_kod'].astype(str).apply(
                    lambda x: str(int(float(x))) if ('.' in str(x)) else str(x)
                )
                result_df_max['depo_kod_clean'] = result_df_max['depo_kod'].astype(str)
                
                # Sevkiyat hesapla
                sevkiyat_gercek = []
                for idx, row in result_df_max.iterrows():
                    depo_kod = str(row['depo_kod'])
                    urun_kod_raw = str(row['urun_kod'])
                    try:
                        if '.' in urun_kod_raw:
                            urun_kod = str(int(float(urun_kod_raw)))
                        else:
                            urun_kod = urun_kod_raw
                    except:
                        urun_kod = urun_kod_raw
                    
                    ihtiyac = float(row['ihtiyac'])
                    key = (depo_kod, urun_kod)
                    
                    if key in depo_stok_dict:
                        kalan_stok = depo_stok_dict[key]
                        if kalan_stok >= ihtiyac:
                            sevkiyat = ihtiyac
                            depo_stok_dict[key] -= ihtiyac
                        else:
                            sevkiyat = kalan_stok
                            depo_stok_dict[key] = 0
                    else:
                        sevkiyat = 0
                    
                    sevkiyat_gercek.append(sevkiyat)
                
                result_df_max['sevkiyat_gercek'] = sevkiyat_gercek
                result_df_max['stok_yoklugu_kaybi'] = result_df_max['ihtiyac'] - result_df_max['sevkiyat_gercek']
                result_df_max = result_df_max[result_df_max['ihtiyac'] > 0].copy()
                
                # Sonuç tablosu - TAMSAYI DÖNÜŞÜMÜ EKLENDİ
                result_final = result_df_max[[
                    'Oncelik', 'magaza_kod', 'urun_kod',
                    'magaza_segment', 'urun_segment', 'Durum',
                    'stok', 'yol', 'satis', 'ihtiyac', 'sevkiyat_gercek', 'depo_kod', 'stok_yoklugu_kaybi'
                ]].rename(columns={
                    'Oncelik': 'oncelik',
                    'Durum': 'durum',
                    'ihtiyac': 'ihtiyac_miktari',
                    'sevkiyat_gercek': 'sevkiyat_miktari',
                    'stok_yoklugu_kaybi': 'stok_yoklugu_satis_kaybi'
                })
                
                # TAMSAYI DÖNÜŞÜMÜ - ÜRÜN STOKLARI İÇİN
                integer_columns = ['stok', 'yol', 'satis', 'ihtiyac_miktari', 'sevkiyat_miktari', 'stok_yoklugu_satis_kaybi']
                for col in integer_columns:
                    if col in result_final.columns:
                        result_final[col] = result_final[col].round().astype(int)
                
                # Kolon sıralamasını düzenle
                result_final = result_final[[
                    'oncelik', 'magaza_kod', 'urun_kod',
                    'magaza_segment', 'urun_segment', 'durum',
                    'stok', 'yol', 'satis', 'ihtiyac_miktari', 'sevkiyat_miktari', 'depo_kod', 'stok_yoklugu_satis_kaybi'
                ]]
                
                result_final.insert(0, 'sira_no', range(1, len(result_final) + 1))
                
                # Hesaplama süresini hesapla
                end_time = time.time()
                calculation_time = end_time - start_time
                
                progress_bar.progress(100, text="Tamamlandı!")
                
                # SONUÇLARI SESSION STATE'E KAYDET
                st.session_state.sevkiyat_sonuc = result_final.copy()
                
                # Hesaplama tamamlandı mesajını göster
                st.success(f"✅ Hesaplama tamamlandı! ({calculation_time:.2f} saniye)")
            
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
