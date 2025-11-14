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
# SESSION STATE BAŞLATMA - TEK SEFERDE
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
        if st.button("➡️ Veri Yükleme Sayfasına Git", use_container_width=True):
            st.switch_page("pages/0_Veri_Yukleme.py")
    with col2:
        if st.button("➡️ Alım Sipariş Sayfasına Git", use_container_width=True):
            st.switch_page("pages/4_PO.py")
    
    st.markdown("---")
    
# ============================================
# 🫧 SEGMENTASYON AYARLARI - DÜZELTİLMİŞ
# ============================================
elif menu == "🫧 Segmentasyon":
    st.title("🫧 Segmentasyon")
    st.markdown("---")
    
    st.info("**Stok/Satış oranına göre** ürün ve mağazaları gruplandırma (Mağaza Stok / Toplam Satış)")
    
    if st.session_state.anlik_stok_satis is None:
        st.warning("⚠️ Önce 'Veri Yükleme' bölümünden anlık stok/satış verisini yükleyin!")
        st.stop()
    
    # Ürün bazında toplam stok/satış hesapla
    data = st.session_state.anlik_stok_satis.copy()
    
    # Ürün bazında gruplama
    urun_aggregated = data.groupby('urun_kod').agg({
        'stok': 'sum',
        'yol': 'sum',
        'satis': 'sum',
        'ciro': 'sum'
    }).reset_index()
    urun_aggregated['stok_satis_orani'] = urun_aggregated['stok'] / urun_aggregated['satis'].replace(0, 1)
    
    if st.session_state.urun_master is not None:
        urun_master = st.session_state.urun_master[['urun_kod', 'marka_kod']].copy()
        urun_master['urun_kod'] = urun_master['urun_kod'].astype(str)
        urun_aggregated['urun_kod'] = urun_aggregated['urun_kod'].astype(str)
        urun_aggregated = urun_aggregated.merge(urun_master, on='urun_kod', how='left')
    else:
        urun_aggregated['marka_kod'] = 'Bilinmiyor'
    
    # Mağaza bazında gruplama
    magaza_aggregated = data.groupby('magaza_kod').agg({
        'stok': 'sum',
        'yol': 'sum',
        'satis': 'sum',
        'ciro': 'sum'
    }).reset_index()
    magaza_aggregated['stok_satis_orani'] = magaza_aggregated['stok'] / magaza_aggregated['satis'].replace(0, 1)
    
    st.markdown("---")
    
    # Ürün segmentasyonu
    st.subheader("🏷️ Ürün Segmentasyonu")
    
    use_default_product = st.checkbox("Varsayılan aralıkları kullan (Ürün)", value=True, key="seg_use_default_product")
    
    if use_default_product:
        st.write("**Varsayılan Aralıklar**: 0-4, 5-8, 9-12, 12-15, 15-20, 20+")
        product_ranges = [(0, 4), (5, 8), (9, 12), (12, 15), (15, 20), (20, float('inf'))]
    else:
        st.write("Özel aralıklar tanımlayın:")
        num_ranges = st.number_input("Kaç aralık?", min_value=2, max_value=10, value=6, key="seg_num_ranges_product")
        
        product_ranges = []
        for i in range(num_ranges):
            col1, col2 = st.columns(2)
            with col1:
                min_val = st.number_input(f"Aralık {i+1} - Min", value=i*5, key=f"prod_min_{i}")
            with col2:
                max_val = st.number_input(f"Aralık {i+1} - Max", value=(i+1)*5 if i < num_ranges-1 else 999, key=f"prod_max_{i}")
            product_ranges.append((min_val, max_val))
    
    # Ürün segment labels
    product_labels = [f"{int(r[0])}-{int(r[1]) if r[1] != float('inf') else 'inf'}" for r in product_ranges]
    
    # Segmentasyon uygula
    temp_prod = urun_aggregated.copy()
    temp_prod['segment'] = pd.cut(
        temp_prod['stok_satis_orani'], 
        bins=[r[0] for r in product_ranges] + [product_ranges[-1][1]],
        labels=product_labels,
        include_lowest=True
    )
    
    st.write("**Ürün Dağılımı:**")
    segment_dist = temp_prod['segment'].value_counts().sort_index()
    col1, col2 = st.columns([1, 2])
    with col1:
        st.dataframe(segment_dist, width='content', height=200)
    with col2:
        st.bar_chart(segment_dist)
    
    st.markdown("---")
    
    # Mağaza segmentasyonu
    st.subheader("🏪 Mağaza Segmentasyonu")
    
    use_default_store = st.checkbox("Varsayılan aralıkları kullan (Mağaza)", value=True, key="seg_use_default_store")
    
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
    
    # Mağaza segment labels
    store_labels = [f"{int(r[0])}-{int(r[1]) if r[1] != float('inf') else 'inf'}" for r in store_ranges]
    
    # Segmentasyon uygula
    temp_store = magaza_aggregated.copy()
    temp_store['segment'] = pd.cut(
        temp_store['stok_satis_orani'], 
        bins=[r[0] for r in store_ranges] + [store_ranges[-1][1]],
        labels=store_labels,
        include_lowest=True
    )
    
    st.write("**Mağaza Dağılımı:**")
    segment_dist_store = temp_store['segment'].value_counts().sort_index()
    col1, col2 = st.columns([1, 2])
    with col1:
        st.dataframe(segment_dist_store, width='content', height=200)
    with col2:
        st.bar_chart(segment_dist_store)
    
    st.markdown("---")
    
    # Kaydet butonu
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("💾 Segmentasyonu Kaydet", type="primary"):
            st.session_state.segmentation_params = {
                'product_ranges': product_ranges,
                'store_ranges': store_ranges
            }
            st.session_state.prod_segments = product_labels
            st.session_state.store_segments = store_labels
            st.session_state.urun_segment_map = temp_prod.set_index('urun_kod')['segment'].to_dict()
            st.session_state.magaza_segment_map = temp_store.set_index('magaza_kod')['segment'].to_dict()
            st.success("✅ Ayarlar kaydedildi!")
    with col2:
        st.info("ℹ️ Kaydetmeseniz de default değerler kullanılacaktır.")
            
    st.markdown("---")
    
    # ============================================
    # DETAY VERİLERİNİ HAZIRLA (YENİ EKLENEN KISIM)
    # ============================================
    # Ürün detayı
    urun_detail = temp_prod.copy()
    if 'marka_kod' in urun_detail.columns:
        urun_detail = urun_detail[['urun_kod', 'marka_kod', 'stok', 'satis', 'stok_satis_orani', 'segment']]
        urun_detail.columns = ['Ürün Kodu', 'Marka Kodu', 'Toplam Stok', 'Toplam Satış', 'Stok/Satış Oranı', 'Segment']
    else:
        urun_detail = urun_detail[['urun_kod', 'stok', 'satis', 'stok_satis_orani', 'segment']]
        urun_detail.columns = ['Ürün Kodu', 'Toplam Stok', 'Toplam Satış', 'Stok/Satış Oranı', 'Segment']
    
    # Mağaza detayı
    magaza_detail = temp_store.copy()
    magaza_detail = magaza_detail[['magaza_kod', 'stok', 'satis', 'stok_satis_orani', 'segment']]
    magaza_detail.columns = ['Mağaza Kodu', 'Toplam Stok', 'Toplam Satış', 'Stok/Satış Oranı', 'Segment']
    
    # ============================================
    # HER İKİSİNİ BİRLİKTE İNDİR
    # ============================================
    st.subheader("📥 Tüm Segmentasyon Verilerini İndir")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Excel formatında (iki sheet)
        if st.button("📊 Excel İndir (Ürün + Mağaza)", key="seg_export_excel"):
            try:
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
        if st.button("📦 ZIP İndir (2 CSV)", key="seg_export_zip"):
            import zipfile
            from io import BytesIO
            
            zip_buffer = BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Ürün CSV
                urun_csv = urun_detail.to_csv(index=False, encoding='utf-8-sig')
                zip_file.writestr('urun_segmentasyon.csv', urun_csv)
                
                # Mağaza CSV
                magaza_csv = magaza_detail.to_csv(index=False, encoding='utf-8-sig')
                zip_file.writestr('magaza_segmentasyon.csv', magaza_csv)
            
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

# ============================================
# 🎲 HEDEF MATRİS - DÜZENLENEBİLİR VERSİYON (ADIM 2)
# ============================================
elif menu == "🎲 Hedef Matris":
    st.title("🎲 Hedef Matris Parametreleri")
    st.markdown("---")
    
    # Segmentleri kontrol et
    if (st.session_state.prod_segments is None or 
        st.session_state.store_segments is None):
        st.warning("⚠️ Önce 'Segmentasyon' bölümüne gidin ve segmentasyonu kaydedin!")
        st.stop()
    
    prod_segments = st.session_state.prod_segments  # Sütunlar
    store_segments = st.session_state.store_segments  # Satırlar
    
    st.info(f"📏 Matris Boyutu: {len(store_segments)} Mağaza Segment × {len(prod_segments)} Ürün Segment")
    st.success("✨ **Artık hücrelere tıklayarak değerleri düzenleyebilirsiniz!**")
    st.markdown("---")
    
    # ============================================
    # 1️⃣ ŞİŞME ORANI MATRİSİ
    # ============================================
    st.subheader("1️⃣ Şişme Oranı Matrisi")
    st.caption("📊 Default: 0.5 | Düzenlemek için hücreye çift tıklayın")
    
    # Matris oluştur veya yükle
    if st.session_state.sisme_orani is not None:
        sisme_df = st.session_state.sisme_orani.copy()
    else:
        sisme_df = pd.DataFrame(0.5, index=store_segments, columns=prod_segments)
    
    # Index'i kolon olarak ekle (data_editor için gerekli)
    sisme_display = sisme_df.reset_index()
    sisme_display.rename(columns={'index': 'Mağaza↓ / Ürün→'}, inplace=True)
    
    # Düzenlenebilir tablo
    edited_sisme = st.data_editor(
        sisme_display,
        key="editor_sisme_v1",
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=["Mağaza↓ / Ürün→"]  # İlk sütun düzenlenemez
    )
    
    st.markdown("---")
    
    # ============================================
    # 2️⃣ GENLEŞTİRME ORANI MATRİSİ
    # ============================================
    st.subheader("2️⃣ Genleştirme Oranı Matrisi")
    st.caption("📊 Default: 1.0 | Düzenlemek için hücreye çift tıklayın")
    
    if st.session_state.genlestirme_orani is not None:
        genles_df = st.session_state.genlestirme_orani.copy()
    else:
        genles_df = pd.DataFrame(1.0, index=store_segments, columns=prod_segments)
    
    genles_display = genles_df.reset_index()
    genles_display.rename(columns={'index': 'Mağaza↓ / Ürün→'}, inplace=True)
    
    edited_genles = st.data_editor(
        genles_display,
        key="editor_genles_v1",
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=["Mağaza↓ / Ürün→"]
    )
    
    st.markdown("---")
    
    # ============================================
    # 3️⃣ MIN ORAN MATRİSİ
    # ============================================
    st.subheader("3️⃣ Min Oran Matrisi")
    st.caption("📊 Default: 1.0 | Düzenlemek için hücreye çift tıklayın")
    
    if st.session_state.min_oran is not None:
        min_df = st.session_state.min_oran.copy()
    else:
        min_df = pd.DataFrame(1.0, index=store_segments, columns=prod_segments)
    
    min_display = min_df.reset_index()
    min_display.rename(columns={'index': 'Mağaza↓ / Ürün→'}, inplace=True)
    
    edited_min = st.data_editor(
        min_display,
        key="editor_min_v1",
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=["Mağaza↓ / Ürün→"]
    )
    
    st.markdown("---")
    
    # ============================================
    # 4️⃣ INITIAL MATRİS
    # ============================================
    st.subheader("4️⃣ Initial Matris")
    st.caption("📊 Default: 1.0 | Düzenlemek için hücreye çift tıklayın")
    
    if st.session_state.initial_matris is not None:
        initial_df = st.session_state.initial_matris.copy()
    else:
        initial_df = pd.DataFrame(1.0, index=store_segments, columns=prod_segments)
    
    initial_display = initial_df.reset_index()
    initial_display.rename(columns={'index': 'Mağaza↓ / Ürün→'}, inplace=True)
    
    edited_initial = st.data_editor(
        initial_display,
        key="editor_initial_v1",
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        disabled=["Mağaza↓ / Ürün→"]
    )
    
    st.markdown("---")
    
    # ============================================
    # KAYDET BUTONU
    # ============================================
    st.subheader("💾 Değişiklikleri Kaydet")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("💾 KAYDET", type="primary", use_container_width=True, key="save_matrices_btn"):
            try:
                # Düzenlenmiş dataframe'leri index'e çevir ve kaydet
                st.session_state.sisme_orani = edited_sisme.set_index('Mağaza↓ / Ürün→')
                st.session_state.genlestirme_orani = edited_genles.set_index('Mağaza↓ / Ürün→')
                st.session_state.min_oran = edited_min.set_index('Mağaza↓ / Ürün→')
                st.session_state.initial_matris = edited_initial.set_index('Mağaza↓ / Ürün→')
                
                st.success("✅ Tüm matrisler başarıyla kaydedildi!")
                st.balloons()
                
                # Doğrulama bilgisi
                st.info(f"""
                **Kaydedilen Boyutlar:**
                - Şişme Oranı: {st.session_state.sisme_orani.shape[0]} × {st.session_state.sisme_orani.shape[1]}
                - Genleştirme: {st.session_state.genlestirme_orani.shape[0]} × {st.session_state.genlestirme_orani.shape[1]}
                - Min Oran: {st.session_state.min_oran.shape[0]} × {st.session_state.min_oran.shape[1]}
                - Initial: {st.session_state.initial_matris.shape[0]} × {st.session_state.initial_matris.shape[1]}
                """)
                
            except Exception as e:
                st.error(f"❌ Kaydetme hatası: {str(e)}")
    
    with col2:
        st.info("💡 **İpucu:** Değerleri değiştirdikten sonra 'Kaydet' butonuna basın. Kaydedilmeyen değişiklikler kaybolur!")
    
    st.markdown("---")
    
    # ============================================
    # İNDİRME SEÇENEKLERİ (BONUS)
    # ============================================
    with st.expander("📥 Matrisleri Excel/CSV Olarak İndir"):
        st.write("**Kaydedilmiş matrisleri dışa aktarın:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Excel formatında (tüm matrisler tek dosyada)
            if st.button("📊 Excel İndir (Tüm Matrisler)", key="download_excel"):
                try:
                    from io import BytesIO
                    
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        if st.session_state.sisme_orani is not None:
                            st.session_state.sisme_orani.to_excel(writer, sheet_name='Şişme Oranı')
                        if st.session_state.genlestirme_orani is not None:
                            st.session_state.genlestirme_orani.to_excel(writer, sheet_name='Genleştirme')
                        if st.session_state.min_oran is not None:
                            st.session_state.min_oran.to_excel(writer, sheet_name='Min Oran')
                        if st.session_state.initial_matris is not None:
                            st.session_state.initial_matris.to_excel(writer, sheet_name='Initial')
                    
                    output.seek(0)
                    
                    st.download_button(
                        label="⬇️ Excel Dosyasını İndir",
                        data=output.getvalue(),
                        file_name="hedef_matrisler.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"Excel indirme hatası: {e}")
        
        with col2:
            # CSV formatında (ZIP içinde 4 dosya)
            if st.button("📦 CSV İndir (ZIP)", key="download_csv"):
                try:
                    import zipfile
                    from io import BytesIO
                    
                    zip_buffer = BytesIO()
                    
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        if st.session_state.sisme_orani is not None:
                            csv_data = st.session_state.sisme_orani.to_csv(encoding='utf-8-sig')
                            zip_file.writestr('sisme_orani.csv', csv_data)
                        
                        if st.session_state.genlestirme_orani is not None:
                            csv_data = st.session_state.genlestirme_orani.to_csv(encoding='utf-8-sig')
                            zip_file.writestr('genlestirme_orani.csv', csv_data)
                        
                        if st.session_state.min_oran is not None:
                            csv_data = st.session_state.min_oran.to_csv(encoding='utf-8-sig')
                            zip_file.writestr('min_oran.csv', csv_data)
                        
                        if st.session_state.initial_matris is not None:
                            csv_data = st.session_state.initial_matris.to_csv(encoding='utf-8-sig')
                            zip_file.writestr('initial_matris.csv', csv_data)
                    
                    zip_buffer.seek(0)
                    
                    st.download_button(
                        label="⬇️ ZIP Dosyasını İndir",
                        data=zip_buffer.getvalue(),
                        file_name="hedef_matrisler.zip",
                        mime="application/zip"
                    )
                except Exception as e:
                    st.error(f"CSV indirme hatası: {e}")



# ============================================
# 🔢 SIRALAMA - İHTİYAÇ ÖNCELİKLENDİRME
# ============================================
elif menu == "🔢 Sıralama":
    st.title("🔢 Sıralama Öncelikleri")
    st.markdown("---")
    
    # Session state başlatma
    if 'oncelik_siralama' not in st.session_state:
        st.session_state.oncelik_siralama = None
    
    # Segment kontrolü
    if st.session_state.prod_segments is None:
        st.warning("⚠️ Önce 'Segmentasyon' sayfasına gidin ve segmentasyonu kaydedin!")
        st.stop()
    
    prod_segments = st.session_state.prod_segments
    
    st.info(f"📊 Toplam {len(prod_segments)} ürün segmenti için öncelik sıralaması yapacaksınız")
    st.markdown("---")
    
    # Açıklama
    st.markdown("""
    ### 📋 Nasıl Çalışır?
    
    Her **ürün segmenti** için ihtiyaç türlerinin öncelik sırasını belirleyin:
    
    - **RPT (Replenishment):** Normal stok tamamlama
    - **Initial:** Yeni ürün ilk dağıtımı  
    - **Min:** Minimum stok garantisi
    
    **Örnek:**
    - Segment **0-4** için: `1. RPT → 2. Initial → 3. Min`
    - Segment **5-8** için: `1. Initial → 2. RPT → 3. Min`
    
    **Depo stok dağıtımı** bu sıraya göre yapılacak.
    """)
    
    st.markdown("---")
    
    # Mevcut sıralamayı yükle veya default oluştur
    if st.session_state.oncelik_siralama is not None:
        siralama_dict = st.session_state.oncelik_siralama
        st.success("✅ Kaydedilmiş sıralama yüklendi")
    else:
        # Default: RPT → Initial → Min
        siralama_dict = {segment: ['RPT', 'Initial', 'Min'] for segment in prod_segments}
        st.info("ℹ️ Default sıralama gösteriliyor (RPT → Initial → Min)")
    
    st.markdown("---")
    
    # Sıralama tablosu
    st.subheader("🎯 Öncelik Sıralaması")
    
    # Düzenlenebilir tablo oluştur
    siralama_data = []
    for segment in prod_segments:
        current_order = siralama_dict.get(segment, ['RPT', 'Initial', 'Min'])
        siralama_data.append({
            'Ürün Segmenti': segment,
            '1. Öncelik': current_order[0],
            '2. Öncelik': current_order[1],
            '3. Öncelik': current_order[2]
        })
    
    siralama_df = pd.DataFrame(siralama_data)
    
    # Data editor ile düzenleme
    st.write("**Sıralamayı Düzenleyin:**")
    st.caption("Her segment için öncelik sırasını değiştirin (dropdown'dan seçin)")
    
    edited_df = st.data_editor(
        siralama_df,
        column_config={
            "Ürün Segmenti": st.column_config.TextColumn(
                "Ürün Segmenti",
                disabled=True,
                width="medium"
            ),
            "1. Öncelik": st.column_config.SelectboxColumn(
                "1. Öncelik",
                options=['RPT', 'Initial', 'Min'],
                required=True,
                width="medium"
            ),
            "2. Öncelik": st.column_config.SelectboxColumn(
                "2. Öncelik",
                options=['RPT', 'Initial', 'Min'],
                required=True,
                width="medium"
            ),
            "3. Öncelik": st.column_config.SelectboxColumn(
                "3. Öncelik",
                options=['RPT', 'Initial', 'Min'],
                required=True,
                width="medium"
            )
        },
        hide_index=True,
        use_container_width=True,
        key="siralama_editor"
    )
    
    st.markdown("---")
    
    # Validasyon ve Kaydet
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if st.button("💾 KAYDET", type="primary", use_container_width=True):
            # Validasyon: Her satırda aynı değer tekrar etmemeli
            valid = True
            error_rows = []
            
            for idx, row in edited_df.iterrows():
                values = [row['1. Öncelik'], row['2. Öncelik'], row['3. Öncelik']]
                if len(values) != len(set(values)):
                    valid = False
                    error_rows.append(row['Ürün Segmenti'])
            
            if not valid:
                st.error(f"❌ Hata! Aynı öncelik tekrar ediyor: {', '.join(error_rows)}")
                st.warning("Her segment için RPT, Initial ve Min değerleri farklı olmalı!")
            else:
                # Dictionary formatında kaydet
                yeni_siralama = {}
                for _, row in edited_df.iterrows():
                    yeni_siralama[row['Ürün Segmenti']] = [
                        row['1. Öncelik'],
                        row['2. Öncelik'],
                        row['3. Öncelik']
                    ]
                
                st.session_state.oncelik_siralama = yeni_siralama
                st.success("✅ Sıralama kaydedildi!")
                st.balloons()
    
    with col2:
        st.info("💡 **İpucu:** Her satırda RPT, Initial ve Min farklı sırada olmalı")
    
    st.markdown("---")
    
    # Önizleme
    st.subheader("👁️ Kayıtlı Sıralama Önizlemesi")
    
    if st.session_state.oncelik_siralama is not None:
        import json
        preview_data = []
        for segment, order in st.session_state.oncelik_siralama.items():
            preview_data.append({
                'Segment': segment,
                'Sıralama': ' → '.join(order)
            })
        
        preview_df = pd.DataFrame(preview_data)
        st.dataframe(preview_df, use_container_width=True, hide_index=True, height=250)
        
        # JSON export
        with st.expander("📥 JSON Formatında İndir"):
            json_str = json.dumps(st.session_state.oncelik_siralama, indent=2, ensure_ascii=False)
            st.download_button(
                label="💾 JSON İndir",
                data=json_str,
                file_name="oncelik_siralama.json",
                mime="application/json"
            )
            st.code(json_str, language='json')
    else:
        st.warning("⚠️ Henüz kayıtlı sıralama yok")
    
    st.markdown("---")
    
    # Reset butonu
    if st.button("🔄 Default Sıralamaya Sıfırla"):
        st.session_state.oncelik_siralama = None
        st.success("✅ Sıfırlandı! Sayfa yenileniyor...")
        st.rerun()
    
    st.markdown("---")
    
    # Bilgilendirme
    st.info("""
    **ℹ️ Bu Sıralama Nerede Kullanılır?**
    
    **Hesaplama** bölümünde sevkiyat ihtiyaçları hesaplanırken:
    1. Tüm ürün-mağaza kombinasyonları için ihtiyaç hesaplanır (RPT/Initial/Min)
    2. Bu sıralama bilgisine göre öncelik atanır
    3. Depo stoku **bu öncelik sırasına göre dağıtılır**
    
    **Örnek:**
    - Segment 0-4 ürünü için önce **RPT** ihtiyaçları karşılanır
    - Sonra **Initial** (yeni ürün dağıtımı)
    - En son **Min** (minimum garantisi)
    
    **⚠️ Önemli:** Kaydet butonuna basmazsanız **default sıralama** (RPT → Initial → Min) kullanılır!
    """)
    
    st.markdown("---")
    
    # Kullanım Notu
    st.success("""
    ✅ **Hızlı Kullanım:**
    - Varsayılan sıralamayı kullanmak istiyorsanız → Hiçbir şey yapmanıza gerek yok!
    - Özel sıralama istiyorsanız → Tabloyu düzenleyin ve **Kaydet** butonuna basın
    """)



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
        # ⏱️ SÜRE ÖLÇÜMÜ BAŞLAT - BURAYA EKLE
        baslaangic_zamani = time.time()    
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
                    df['min_deger'] = 0.0
                    df['max_deger'] = 999999.0
                
                # ============================================
                # MATRİS DEĞERLERİ - SÜPER HIZLI VERSİYON (MERGE)
                # ============================================
                # Hesaplama bölümünde matris atama kısmını tamamen değiştirin
                
                # 5. MATRİS DEĞERLERİ - SÜPER HIZLI ATAMA
                # Önce kolonları default değerlerle oluştur
                df['genlestirme'] = 1.0
                df['sisme'] = 0.5
                df['min_oran'] = 1.0
                df['initial_katsayi'] = 1.0
                
                # Matris değerlerini segment bazında uygula - MERGE ile HIZLI VERSİYON
                try:
                    all_matrices_exist = all([
                        st.session_state.genlestirme_orani is not None,
                        st.session_state.sisme_orani is not None,
                        st.session_state.min_oran is not None,
                        st.session_state.initial_matris is not None
                    ])
                    
                    if all_matrices_exist:
                        st.info("🔄 Matris değerleri uygulanıyor (yüksek performans modu)...")
                        
                        # Segment'ları string'e çevir
                        df['urun_segment'] = df['urun_segment'].astype(str)
                        df['magaza_segment'] = df['magaza_segment'].astype(str)
                        
                        # 1. Genleştirme Oranı
                        genles_long = st.session_state.genlestirme_orani.stack().reset_index()
                        genles_long.columns = ['magaza_segment', 'urun_segment', 'genlestirme_mat']
                        genles_long['magaza_segment'] = genles_long['magaza_segment'].astype(str)
                        genles_long['urun_segment'] = genles_long['urun_segment'].astype(str)
                        
                        df = df.merge(
                            genles_long, 
                            on=['magaza_segment', 'urun_segment'], 
                            how='left'
                        )
                        df['genlestirme'] = df['genlestirme_mat'].fillna(df['genlestirme'])
                        df.drop('genlestirme_mat', axis=1, inplace=True)
                        
                        # 2. Şişme Oranı
                        sisme_long = st.session_state.sisme_orani.stack().reset_index()
                        sisme_long.columns = ['magaza_segment', 'urun_segment', 'sisme_mat']
                        sisme_long['magaza_segment'] = sisme_long['magaza_segment'].astype(str)
                        sisme_long['urun_segment'] = sisme_long['urun_segment'].astype(str)
                        
                        df = df.merge(
                            sisme_long, 
                            on=['magaza_segment', 'urun_segment'], 
                            how='left'
                        )
                        df['sisme'] = df['sisme_mat'].fillna(df['sisme'])
                        df.drop('sisme_mat', axis=1, inplace=True)
                        
                        # 3. Min Oran
                        min_long = st.session_state.min_oran.stack().reset_index()
                        min_long.columns = ['magaza_segment', 'urun_segment', 'min_oran_mat']
                        min_long['magaza_segment'] = min_long['magaza_segment'].astype(str)
                        min_long['urun_segment'] = min_long['urun_segment'].astype(str)
                        
                        df = df.merge(
                            min_long, 
                            on=['magaza_segment', 'urun_segment'], 
                            how='left'
                        )
                        df['min_oran'] = df['min_oran_mat'].fillna(df['min_oran'])
                        df.drop('min_oran_mat', axis=1, inplace=True)
                        
                        # 4. Initial Matris
                        initial_long = st.session_state.initial_matris.stack().reset_index()
                        initial_long.columns = ['magaza_segment', 'urun_segment', 'initial_mat']
                        initial_long['magaza_segment'] = initial_long['magaza_segment'].astype(str)
                        initial_long['urun_segment'] = initial_long['urun_segment'].astype(str)
                        
                        df = df.merge(
                            initial_long, 
                            on=['magaza_segment', 'urun_segment'], 
                            how='left'
                        )
                        df['initial_katsayi'] = df['initial_mat'].fillna(df['initial_katsayi'])
                        df.drop('initial_mat', axis=1, inplace=True)
                        
                        st.success("✅ Matris değerleri uygulandı (merge yöntemi - süper hızlı!)")
                    else:
                        st.info("ℹ️ Hedef matris değerleri tanımlı değil, default değerler kullanılıyor.")
                        
                except Exception as e:
                    st.warning(f"⚠️ Matris değer atama hatası (default değerler kullanılacak): {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())
                
                # ============================================
                # NEREDE KULLANILACAK?
                # ============================================
                # 2_Sevkiyat.py dosyasında, Hesaplama bölümünde:
                # "# 5. MATRİS DEĞERLERİ" yazan kısmı bulun
                # Tüm for loop kodunu silin
                # Bu yeni kodu yapıştırın
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
                    # 🆕 KRİTİK: FLOAT → INT DÖNÜŞÜMÜ
                    result['depo_kod'] = result['depo_kod'].fillna(0).astype(int)
                    result['depo_kod'] = result['depo_kod'].replace(0, 'DEPO_01')
                else:
                    result['depo_kod'] = 'DEPO_01'

                
                # 9. YASAK KONTROL
                if (st.session_state.yasak_master is not None and 
                    'urun_kod' in st.session_state.yasak_master.columns and
                    'magaza_kod' in st.session_state.yasak_master.columns):
                    
                    yasak = st.session_state.yasak_master.copy()
                    yasak['urun_kod'] = yasak['urun_kod'].astype(str)
                    yasak['magaza_kod'] = yasak['magaza_kod'].astype(str)
                    
                    if 'yasak_durum' in yasak.columns:
                        result = result.merge(
                            yasak[['urun_kod', 'magaza_kod', 'yasak_durum']], 
                            on=['urun_kod', 'magaza_kod'], 
                            how='left'
                        )
                        result.loc[result['yasak_durum'] == 'Yasak', 'ihtiyac'] = 0
                
                # 10. DEPO STOK DAĞITIMI

                result = result[result['ihtiyac'] > 0].copy()
                
                # 🆕 Depo stok veri tiplerini düzelt
                depo_df['depo_kod'] = depo_df['depo_kod'].astype(int)
                depo_df['urun_kod'] = depo_df['urun_kod'].astype(int)
                
                # 🆕 Result veri tiplerini düzelt
                result['depo_kod'] = pd.to_numeric(result['depo_kod'], errors='coerce').fillna(0).astype(int)
                result['urun_kod'] = result['urun_kod'].astype(int)
                
                # Depo stok sözlüğü
                depo_dict = {}
                for _, row in depo_df.iterrows():
                    depo_kod = int(row['depo_kod'])
                    urun_kod = int(row['urun_kod'])
                    key = (depo_kod, urun_kod)
                    depo_dict[key] = float(row['stok'])
                
                # Öncelik sıralaması
                result = result.sort_values(['Durum', 'ihtiyac'], ascending=[True, False])
                
                # Sevkiyat hesapla
                sevkiyat_list = []
                for _, row in result.iterrows():
                    depo_kod = int(row['depo_kod'])
                    urun_kod = int(row['urun_kod'])
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
                # ⏱️ SÜRE ÖLÇÜMÜ BİTİR
                st.session_state.sevkiyat_sonuc = final

                bitis_zamani = time.time()
                algoritma_suresi = bitis_zamani - baslaangic_zamani           
                st.success(f"✅ Hesaplama tamamlandı! {len(final):,} satır oluşturuldu.")
                st.markdown("---")

                # ============================================
                # 📊 ÖZET METRİKLER TABLOSU
                # ============================================
                st.subheader("📊 Hesaplama Özet Metrikleri")
                
                # Metrikleri hesapla
                toplam_magaza_stok = df['stok'].sum()
                toplam_yol = df['yol'].sum()
                toplam_depo_stok = depo_df['stok'].sum()
                toplam_satis = df['satis'].sum()
                toplam_ihtiyac = final['ihtiyac_miktari'].sum()
                toplam_sevkiyat = final['sevkiyat_miktari'].sum()
                performans = (toplam_sevkiyat / toplam_ihtiyac * 100) if toplam_ihtiyac > 0 else 0
                magaza_sayisi = df['magaza_kod'].nunique()
                urun_sayisi = df['urun_kod'].nunique()
                sevk_olan_urun_sayisi = final[final['sevkiyat_miktari'] > 0]['urun_kod'].nunique()
                
                # Özet tablosu oluştur
                ozet_data = {
                    'Metrik': [
                        '📦 Toplam Mağaza Stok',
                        '🚚 Toplam Yol',
                        '🏭 Toplam Depo Stok',
                        '💰 Toplam Satış',
                        '📋 Toplam İhtiyaç',
                        '✅ Toplam Sevkiyat',
                        '📈 Performans (%)',
                        '⏱️ Algoritma Süresi (sn)',
                        '🏪 Mağaza Sayısı',
                        '🏷️ Ürün Sayısı',
                        '📤 Sevk Olan Ürün Sayısı'
                    ],
                    'Değer': [
                        str(f"{toplam_magaza_stok:,.0f}"),
                        str(f"{toplam_yol:,.0f}"),
                        str(f"{toplam_depo_stok:,.0f}"),
                        str(f"{toplam_satis:,.0f}"),
                        str(f"{toplam_ihtiyac:,.0f}"),
                        str(f"{toplam_sevkiyat:,.0f}"),
                        str(f"{performans:.2f}%"),
                        str(f"{algoritma_suresi:.2f} saniye"),
                        str(f"{magaza_sayisi:,}"),
                        str(f"{urun_sayisi:,}"),
                        str(f"{sevk_olan_urun_sayisi:,}")
                    ]
                }              
                ozet_df = pd.DataFrame(ozet_data)
                
                # Tabloyu göster
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.dataframe(
                        ozet_df,
                        use_container_width=True,
                        hide_index=True,
                        height=450
                    )
                
                with col2:
                    # Önemli metrikler - büyük kartlar
                    st.metric(
                        "🎯 Genel Performans", 
                        f"{performans:.1f}%",
                        delta=f"{performans - 100:.1f}%" if performans < 100 else "Hedef Aşıldı!"
                    )
                    
                    st.metric(
                        "⚡ İşlem Süresi", 
                        f"{algoritma_suresi:.2f} sn"
                    )
                    
                    karsilama_orani = (toplam_sevkiyat / toplam_ihtiyac * 100) if toplam_ihtiyac > 0 else 0
                    st.metric(
                        "📊 Karşılama Oranı",
                        f"{karsilama_orani:.1f}%"
                    )
                    
                    # Stok durumu özeti
                    toplam_stok_sistemi = toplam_magaza_stok + toplam_yol + toplam_depo_stok
                    st.metric(
                        "💼 Toplam Sistem Stok",
                        f"{toplam_stok_sistemi:,.0f}"
                    )
                
                st.markdown("---")
                                
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    st.download_button(
                        label="📥 SAP Dosyası İndir (CSV)",
                        data=sap_data.to_csv(index=False, encoding='utf-8-sig'),
                        file_name="sap_sevkiyat_detay.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="hesaplama_download_sap_csv"
                    )
                
                with col2:
                    st.download_button(
                        label="📥 Tam Detay İndir (CSV)",
                        data=final.to_csv(index=False, encoding='utf-8-sig'),
                        file_name="sevkiyat_tam_detay.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="hesaplama_download_full_csv"
                    )
                
            except Exception as e:
                st.error(f"❌ Hesaplama hatası: {str(e)}")
                import traceback
                st.code(traceback.format_exc())


# ============================================
# 📈 RAPORLAR - TAMAMI DÜZELTİLMİŞ (DUPLICATE KEY HATASI ÇÖZÜLDÜ)
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
            kayip_kolon_adi = 'stok_yoklugu_satis_kaybi' if 'stok_yoklugu_satis_keybi' in result_df.columns else 'stok_yoklugu_kaybi'
            
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
        # ÜRÜN ANALİZİ - DÜZELTİLMİŞ (UNIQUE KEY'LER)
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
            
            # Filtreleme seçenekleri - UNIQUE KEY'LER
            col1, col2 = st.columns(2)
            with col1:
                min_sevkiyat = st.number_input("Min Sevkiyat Filtresi", 
                                             min_value=0, 
                                             value=0,
                                             help="Sadece bu değerden yüksek sevkiyatı olan ürünleri göster",
                                             key="min_sevkiyat_filter_urun")
            
            with col2:
                min_mağaza = st.number_input("Min Mağaza Sayısı", 
                                           min_value=0, 
                                           value=0,
                                           help="Sadece bu sayıdan fazla mağazada bulunan ürünleri göster",
                                           key="min_magaza_filter_urun")
            
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
                    st.dataframe(best_coverage, width='content', key="rapor_urun_best_coverage")
                
                st.subheader("⚠️ En Fazla Kayıp")
                if len(filtered_urun) > 0:
                    worst_loss = filtered_urun.nlargest(5, 'Satış Kaybı')[['Ürün Kodu', 'Satış Kaybı']]
                    st.dataframe(worst_loss, width='content', key="rapor_urun_worst_loss")
            
            st.markdown("---")
            
            # Grafikler - TOP 10 KALDIRILDI
            
            st.write("**Sevkiyat/İhtiyaç Oranı Dağılımı**")
            try:
                oran_dagilim = filtered_urun['Sevkiyat/İhtiyaç %'].value_counts(bins=10).sort_index()
                oran_dagilim_dict = {}
                for interval in oran_dagilim.index:
                    key_str = f"{int(interval.left)}-{int(interval.right)}%"
                    oran_dagilim_dict[key_str] = int(oran_dagilim[interval])
                
                if oran_dagilim_dict:
                    oran_dagilim_df = pd.DataFrame.from_dict(oran_dagilim_dict, orient='index', columns=['Adet'])
                    st.bar_chart(oran_dagilim_df)  # ✅ key parametresi kaldırıldı!
            except Exception as e:
                st.warning(f"Grafik oluşturulamadı: {str(e)}") 
                        
            st.markdown("---")
            
            # İndirme butonları - UNIQUE KEY'LER
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Tüm Ürün Analizi İndir (CSV)",
                    data=urun_sevkiyat.to_csv(index=False, encoding='utf-8-sig'),
                    file_name="urun_analizi_tum.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="download_all_urun"
                )
            with col2:
                st.download_button(
                    label="📥 Filtrelenmiş Ürünler İndir (CSV)",
                    data=filtered_urun.to_csv(index=False, encoding='utf-8-sig'),
                    file_name="urun_analizi_filtreli.csv",
                    mime="text/csv",
                    use_container_width=True,
                    key="download_filtered_urun"
                )

        # ============================================
        # MAĞAZA ANALİZİ - TAB2
        # ============================================
        with tab2:
            st.subheader("🏪 Mağaza Bazında Analiz")
            st.info("Mağaza analizi yakında eklenecek")

        # ============================================
        # SATIŞ KAYBI ANALİZİ - TAB3
        # ============================================
        with tab3:
            st.subheader("⚠️ Satış Kaybı Analizi")
            st.info("Satış kaybı analizi yakında eklenecek")

        # ============================================
        # İL BAZINDA HARİTA - DÜZELTİLMİŞ (UNIQUE KEY'LER)
        # ============================================
        with tab4:
            st.subheader("🗺️ İl Bazında Sevkiyat Haritası")
            
            # Plotly kontrolü
            try:
                import plotly.express as px
                import plotly.graph_objects as go
                PLOTLY_AVAILABLE = True
            except ImportError:
                st.error("Plotly kütüphanesi yüklü değil! requirements.txt dosyasına 'plotly' ekleyin.")
                PLOTLY_AVAILABLE = False
            
            if not PLOTLY_AVAILABLE:
                st.stop()
                
            if st.session_state.magaza_master is None:
                st.warning("⚠️ Mağaza Master verisi yüklenmemiş! Harita için il bilgisi gerekiyor.")
            else:
                # KOLON ADI DÜZELTMESİ
                sevkiyat_kolon = 'sevkiyat_miktari' if 'sevkiyat_miktari' in result_df.columns else 'sevkiyat_gercek'
                ihtiyac_kolon = 'ihtiyac_miktari' if 'ihtiyac_miktari' in result_df.columns else 'ihtiyac'
                
                # İl bazında verileri hazırla
                il_verileri = result_df.groupby('magaza_kod').agg({
                    sevkiyat_kolon: 'sum',
                    ihtiyac_kolon: 'sum'
                }).reset_index()
                
                # Mağaza master'dan il bilgilerini ekle - VERİ TİPİ DÜZELTMESİ
                magaza_master = st.session_state.magaza_master[['magaza_kod', 'il']].copy()
                magaza_master['magaza_kod'] = magaza_master['magaza_kod'].astype(str)
                il_verileri['magaza_kod'] = il_verileri['magaza_kod'].astype(str)
                
                il_verileri = il_verileri.merge(magaza_master, on='magaza_kod', how='left')
                
                # İl bazında toplamlar
                il_bazinda = il_verileri.groupby('il').agg({
                    sevkiyat_kolon: 'sum',
                    ihtiyac_kolon: 'sum',
                    'magaza_kod': 'nunique'
                }).reset_index()
                
                il_bazinda.columns = ['İl', 'Toplam Sevkiyat', 'Toplam İhtiyaç', 'Mağaza Sayısı']
                
                # Ortalama sevkiyat/mağaza hesapla
                il_bazinda['Ortalama Sevkiyat/Mağaza'] = (il_bazinda['Toplam Sevkiyat'] / il_bazinda['Mağaza Sayısı']).round(0)
                
                # Segmentlere ayır (4 segment)
                segmentler = pd.cut(
                    il_bazinda['Ortalama Sevkiyat/Mağaza'], 
                    bins=4,
                    labels=['Çok Düşük', 'Düşük', 'Orta', 'Yüksek']
                )
                il_bazinda['Performans Segmenti'] = segmentler
                
                # Türkiye il koordinatları
                turkiye_iller = {
                    'İstanbul': (41.0082, 28.9784), 'Ankara': (39.9334, 32.8597), 'İzmir': (38.4237, 27.1428),
                    'Bursa': (40.1885, 29.0610), 'Antalya': (36.8969, 30.7133), 'Adana': (37.0000, 35.3213),
                    'Konya': (37.8667, 32.4833), 'Gaziantep': (37.0662, 37.3833), 'Şanlıurfa': (37.1591, 38.7969),
                    'Mersin': (36.8000, 34.6333), 'Kocaeli': (40.8533, 29.8815), 'Diyarbakır': (37.9144, 40.2306),
                    'Hatay': (36.4018, 36.3498), 'Manisa': (38.6191, 27.4289), 'Kayseri': (38.7312, 35.4787),
                    'Samsun': (41.2928, 36.3313), 'Balıkesir': (39.6484, 27.8826), 'Kahramanmaraş': (37.5858, 36.9371),
                    'Van': (38.4891, 43.4080), 'Aydın': (37.8560, 27.8416), 'Tekirdağ': (40.9781, 27.5117),
                    'Denizli': (37.7765, 29.0864), 'Muğla': (37.2153, 28.3636), 'Eskişehir': (39.7767, 30.5206),
                    'Trabzon': (41.0015, 39.7178), 'Ordu': (40.9833, 37.8833), 'Afyonkarahisar': (38.7638, 30.5403),
                    'Sivas': (39.7477, 37.0179), 'Malatya': (38.3552, 38.3095), 'Erzurum': (39.9000, 41.2700),
                    'Elazığ': (38.6810, 39.2264), 'Batman': (37.8812, 41.1351), 'Kütahya': (39.4167, 29.9833),
                    'Çorum': (40.5506, 34.9556), 'Isparta': (37.7648, 30.5566), 'Osmaniye': (37.2130, 36.1763),
                    'Çanakkale': (40.1553, 26.4142), 'Giresun': (40.9128, 38.3895), 'Aksaray': (38.3687, 34.0370),
                    'Yozgat': (39.8200, 34.8044), 'Edirne': (41.6667, 26.5667), 'Düzce': (40.8433, 31.1565),
                    'Tokat': (40.3167, 36.5500), 'Kastamonu': (41.3767, 33.7765), 'Uşak': (38.6823, 29.4082),
                    'Kırklareli': (41.7333, 27.2167), 'Niğde': (37.9667, 34.6833), 'Rize': (41.0201, 40.5234),
                    'Amasya': (40.6500, 35.8333), 'Bolu': (40.7333, 31.6000), 'Nevşehir': (38.6939, 34.6857),
                    'Bilecik': (40.1500, 29.9833), 'Burdur': (37.7167, 30.2833), 'Kırıkkale': (39.8468, 33.5153),
                    'Karabük': (41.2000, 32.6333), 'Karaman': (37.1759, 33.2287), 'Kırşehir': (39.1500, 34.1667),
                    'Sinop': (42.0231, 35.1531), 'Hakkari': (37.5833, 43.7333), 'Iğdır': (39.9167, 44.0333),
                    'Yalova': (40.6500, 29.2667), 'Bartın': (41.6344, 32.3375), 'Ardahan': (41.1105, 42.7022),
                    'Bayburt': (40.2552, 40.2249), 'Kilis': (36.7164, 37.1156), 'Muş': (38.9462, 41.7539),
                    'Siirt': (37.9333, 41.9500), 'Tunceli': (39.1071, 39.5400), 'Şırnak': (37.5164, 42.4611),
                    'Bitlis': (38.4000, 42.1000), 'Artvin': (41.1667, 41.8333), 'Gümüşhane': (40.4603, 39.4814),
                    'Ağrı': (39.7191, 43.0513), 'Erzincan': (39.7500, 39.5000), 'Adıyaman': (37.7648, 38.2786),
                    'Zonguldak': (41.4564, 31.7987), 'Mardin': (37.3212, 40.7245), 'Sakarya': (40.6937, 30.4358)
                }
                
                # Koordinatları dataframe'e ekle
                il_bazinda['lat'] = il_bazinda['İl'].map(lambda x: turkiye_iller.get(x, (0, 0))[0])
                il_bazinda['lon'] = il_bazinda['İl'].map(lambda x: turkiye_iller.get(x, (0, 0))[1])
                
                # Koordinatı olmayan illeri filtrele
                il_bazinda = il_bazinda[il_bazinda['lat'] != 0]
                
                if len(il_bazinda) > 0:
                    # Renk skalası
                    renk_skalasi = {
                        'Çok Düşük': 'red',
                        'Düşük': 'orange', 
                        'Orta': 'yellow',
                        'Yüksek': 'green'
                    }
                    
                    # Interaktif harita oluştur
                    st.subheader("📍 İl Bazında Ortalama Sevkiyat Performansı")
                    
                    fig = px.scatter_mapbox(
                        il_bazinda,
                        lat="lat",
                        lon="lon", 
                        hover_name="İl",
                        hover_data={
                            'Ortalama Sevkiyat/Mağaza': True,
                            'Toplam Sevkiyat': True,
                            'Mağaza Sayısı': True,
                            'Performans Segmenti': True,
                            'lat': False,
                            'lon': False
                        },
                        color="Performans Segmenti",
                        color_discrete_map=renk_skalasi,
                        size="Ortalama Sevkiyat/Mağaza",
                        size_max=25,
                        zoom=4.5,
                        center={"lat": 39.0, "lon": 35.0},
                        height=600,
                        title="Türkiye İl Bazında Ortalama Sevkiyat/Mağaza Dağılımı"
                    )
                    
                    fig.update_layout(
                        mapbox_style="open-street-map",
                        margin={"r": 0, "t": 30, "l": 0, "b": 0}
                    )
                    
                    st.info("🔍 Haritayı mouse tekerleği ile zoom in/out yapabilir, sürükleyerek hareket ettirebilirsiniz.")
                    
                    st.plotly_chart(fig, use_container_width=True, key="turkey_map")
                    
                    # İl seçimi için dropdown - UNIQUE KEY
                    st.markdown("---")
                    st.subheader("🔍 İl Detayları")
                    
                    secilen_il = st.selectbox(
                        "Detayını görmek istediğiniz ili seçin:",
                        options=il_bazinda['İl'].sort_values().tolist(),
                        key="il_secim_dropdown"
                    )
                    
                    if secilen_il:
                        # Seçilen ilin detaylarını göster
                        il_detay = il_bazinda[il_bazinda['İl'] == secilen_il].iloc[0]
                        
                        # İl detayları metrikleri - GÜVENLİ VERSİYON

                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            try:
                                val = il_detay['Ortalama Sevkiyat/Mağaza']
                                val_str = f"{float(val):,.0f}" if pd.notna(val) and val != '' else "0"
                            except:
                                val_str = "0"
                            st.metric("Ortalama Sevkiyat/Mağaza", val_str)
                        
                        with col2:
                            try:
                                val = il_detay['Toplam Sevkiyat']
                                val_str = f"{float(val):,.0f}" if pd.notna(val) and val != '' else "0"
                            except:
                                val_str = "0"
                            st.metric("Toplam Sevkiyat", val_str)
                        
                        with col3:
                            try:
                                val = il_detay['Mağaza Sayısı']
                                val_str = f"{float(val):,.0f}" if pd.notna(val) and val != '' else "0"
                            except:
                                val_str = "0"
                            st.metric("Mağaza Sayısı", val_str)
                        
                        with col4:
                            try:
                                val = il_detay['Performans Segmenti']
                                val_str = str(val) if pd.notna(val) and val != '' else "Bilinmiyor"
                            except:
                                val_str = "Bilinmiyor"
                            st.metric("Performans", val_str)
                        
                        # Seçilen ildeki mağaza detayları - MAGAZA_AD OLMADAN
                        st.subheader(f"🏪 {secilen_il} İlindeki Mağaza Performansları")
                        
                        try:
                            # Mağaza bazında verileri hazırla
                            magaza_detay = result_df[result_df['magaza_kod'].isin(
                                magaza_master[magaza_master['il'] == secilen_il]['magaza_kod'].astype(str)
                            )]
                            
                            if len(magaza_detay) > 0:
                                magaza_ozet = magaza_detay.groupby('magaza_kod').agg({
                                    sevkiyat_kolon: 'sum',
                                    ihtiyac_kolon: 'sum',
                                    'urun_kod': 'nunique'
                                }).reset_index()
                                
                                # Kolon isimlerini düzenle
                                magaza_ozet.columns = ['Mağaza Kodu', 'Toplam Sevkiyat', 'Toplam İhtiyaç', 'Ürün Sayısı']
                                
                                # Gerçekleşme yüzdesi hesapla
                                magaza_ozet['Gerçekleşme %'] = np.where(
                                    magaza_ozet['Toplam İhtiyaç'] > 0,
                                    (magaza_ozet['Toplam Sevkiyat'] / magaza_ozet['Toplam İhtiyaç'] * 100),
                                    0
                                ).round(1)
                                
                                st.dataframe(
                                    magaza_ozet.style.format({
                                        'Toplam Sevkiyat': '{:,.0f}',
                                        'Toplam İhtiyaç': '{:,.0f}',
                                        'Ürün Sayısı': '{:.0f}',
                                        'Gerçekleşme %': '{:.1f}%'
                                    }),
                                    use_container_width=True,
                                    height=300,
                                    key="magaza_detay_table"
                                )
                            else:
                                st.info("Bu ilde mağaza verisi bulunamadı.")
                                
                        except Exception as e:
                            st.error(f"Mağaza detayları yüklenirken hata oluştu: {str(e)}")
                    
                    # Segment bazında özet
                    st.markdown("---")
                    st.subheader("📊 Performans Segmentleri Özeti")
                    
                    segment_ozet = il_bazinda.groupby('Performans Segmenti').agg({
                        'İl': 'count',
                        'Ortalama Sevkiyat/Mağaza': 'mean',
                        'Toplam Sevkiyat': 'sum'
                    }).reset_index()
                    
                    segment_ozet.columns = ['Performans Segmenti', 'İl Sayısı', 'Ort. Sevkiyat/Mağaza', 'Toplam Sevkiyat']
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.dataframe(
                            segment_ozet.style.format({
                                'İl Sayısı': '{:.0f}',
                                'Ort. Sevkiyat/Mağaza': '{:,.0f}',
                                'Toplam Sevkiyat': '{:,.0f}'
                            }),
                            use_container_width=True,
                            key="segment_ozet_table"
                        )
                    
                    with col2:
                        st.write("**Segment Dağılımı**")
                        segment_dagilim = segment_ozet.set_index('Performans Segmenti')[['İl Sayısı']]
                        fig = px.bar(
                            segment_dagilim,
                            title='Segment Dağılımı',
                            labels={'index': 'Segment', 'value': 'Adet'}
                        )
                        st.plotly_chart(fig, use_container_width=True, key="segment_dagilim_chart")                    
                    # İndirme butonu - UNIQUE KEY
                    st.download_button(
                        label="📥 İl Bazında Analiz İndir (CSV)",
                        data=il_bazinda.to_csv(index=False, encoding='utf-8-sig'),
                        file_name="il_bazinda_analiz.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="download_il_analiz"
                    )
                
                else:
                    st.warning("Harita için yeterli il verisi bulunamadı.")
# ============================================
# 💾 MASTER DATA OLUŞTURMA
# ============================================
elif menu == "💾 Master Data":
    st.title("💾 Master Data Oluşturma")
    st.markdown("---")
    
    st.warning("🚧 **Master Data modülü yakında yayında!** 🚧")
