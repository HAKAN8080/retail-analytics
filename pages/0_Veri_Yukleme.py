import streamlit as st
import pandas as pd
import time
import io
import zipfile

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Veri Yükleme",
    page_icon="📤",
    layout="wide"
)

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
if 'po_yasak' not in st.session_state:
    st.session_state.po_yasak = None
if 'po_detay_kpi' not in st.session_state:
    st.session_state.po_detay_kpi = None

# ============================================
# ANA SAYFA
# ============================================
st.title("📤 Ortak Veri Yükleme Merkezi")
st.markdown("---")

st.info("""
**📋 Bu sayfadan yüklenen veriler tüm modüllerde kullanılır:**
- 🚚 Sevkiyat Planlama
- 💵 Alım Sipariş (PO)
- 📦 Prepack Optimizasyon
- 📉 Lost Sales Analizi
""")

st.markdown("---")

# Örnek CSV'ler
example_csvs = {
    'urun_master.csv': {
        'data': pd.DataFrame({
            'urun_kod': ['U001', 'U002', 'U003'],
            'urun_ad': ['Ürün A', 'Ürün B', 'Ürün C'],
            'satici_kod': ['S001', 'S002', 'S001'],
            'satici_ad': ['Satıcı 1', 'Satıcı 2', 'Satıcı 1'],
            'kategori_kod': ['K001', 'K002', 'K001'],
            'kategori_ad': ['Kategori 1', 'Kategori 2', 'Kategori 1'],
            'umg': ['UMG1', 'UMG2', 'UMG1'],
            'umg_ad': ['Üst Mal Grubu 1', 'Üst Mal Grubu 2', 'Üst Mal Grubu 1'],
            'mg': ['MG1', 'MG2', 'MG1'],
            'mg_ad': ['Mal Grubu 1', 'Mal Grubu 2', 'Mal Grubu 1'],
            'marka_kod': ['M001', 'M002', 'M001'],
            'marka_ad': ['Marka A', 'Marka B', 'Marka A'],
            'klasman_kod': ['K1', 'K2', 'K1'],
            'klasman_ad': ['Klasman A', 'Klasman B', 'Klasman A'],
            'nitelik': ['Nitelik 1', 'Nitelik 2', 'Nitelik 1'],
            'durum': ['Aktif', 'Aktif', 'Pasif'],
            'ithal': [1, 0, 1],
            'ithal_ad': ['İthal', 'Yerli', 'İthal'],
            'tanim': ['Tanım 1', 'Tanım 2', 'Tanım 3'],
            'koli_ici': [12, 24, 6],
            'paket_ici': [6, 12, 3],
            'olcu_birimi': ['Adet', 'Adet', 'Kg']
        }),
        'aciklama': 'Ürün bilgileri ve kategorileri',
        'icon': '📦'
    },
    'magaza_master.csv': {
        'data': pd.DataFrame({
            'magaza_kod': ['M001', 'M002', 'M003'],
            'magaza_ad': ['Mağaza A', 'Mağaza B', 'Mağaza C'],
            'il': ['İstanbul', 'Ankara', 'İzmir'],
            'bolge': ['Marmara', 'İç Anadolu', 'Ege'],
            'tip': ['Hipermarket', 'Süpermarket', 'Hipermarket'],
            'adres_kod': ['ADR001', 'ADR002', 'ADR003'],
            'sm': [5000, 3000, 4500],
            'bs': ['BS1', 'BS2', 'BS1'],
            'depo_kod': ['D001', 'D001', 'D002']
        }),
        'aciklama': 'Mağaza bilgileri ve özellikleri',
        'icon': '🏪'
    },
    'yasak.csv': {
        'data': pd.DataFrame({
            'urun_kod': ['U001', 'U002'],
            'magaza_kod': ['M002', 'M001'],
            'yasak_durum': [1, 1]
        }),
        'aciklama': 'Ürün-mağaza yasak eşleştirmeleri',
        'icon': '🚫'
    },
    'depo_stok.csv': {
        'data': pd.DataFrame({
            'depo_kod': ['D001', 'D001', 'D002'],
            'depo_ad': ['Depo Merkez', 'Depo Merkez', 'Depo Bölge'],
            'urun_kod': ['U001', 'U002', 'U001'],
            'stok': [1000, 1500, 800]
        }),
        'aciklama': 'Depo bazında stok miktarları',
        'icon': '📦'
    },
    'anlik_stok_satis.csv': {
        'data': pd.DataFrame({
            'magaza_kod': ['M001', 'M001', 'M002'],
            'urun_kod': ['U001', 'U002', 'U001'],
            'stok': [100, 150, 120],
            'yol': [20, 30, 25],
            'satis': [50, 40, 45],
            'ciro': [5000, 6000, 5500],
            'smm': [2.0, 3.75, 2.67]
        }),
        'aciklama': 'Mağaza-ürün bazında anlık durum',
        'icon': '📊'
    },
    'haftalik_trend.csv': {
        'data': pd.DataFrame({
            'klasman_kod': ['K1', 'K1', 'K2'],
            'marka_kod': ['M001', 'M001', 'M002'],
            'yil': [2025, 2025, 2025],
            'hafta': [40, 41, 40],
            'stok': [10000, 9500, 15000],
            'satis': [2000, 2100, 1800],
            'ciro': [200000, 210000, 270000],
            'smm': [5.0, 4.52, 8.33],
            'iftutar': [1000000, 950000, 1500000]
        }),
        'aciklama': 'Haftalık satış trend verileri',
        'icon': '📈'
    },
    'kpi.csv': {
        'data': pd.DataFrame({
            'mg_id': ['MG1', 'MG2', 'MG3'],
            'min_deger': [0, 100, 500],
            'max_deger': [99, 499, 999],
            'forward_cover': [1.5, 2.0, 2.5]
        }),
        'aciklama': 'Mal grubu bazında KPI hedefleri',
        'icon': '🎯'
    },
    'po_yasak.csv': {
        'data': pd.DataFrame({
            'urun_kodu': ['U001', 'U002', 'U003'],
            'yasak_durum': [1, 0, 1],
            'acik_siparis': [100, 0, 250]
        }),
        'aciklama': 'PO yasak ürünler ve açık siparişler',
        'icon': '🚫'
    },
    'po_detay_kpi.csv': {
        'data': pd.DataFrame({
            'marka_kod': ['M001', 'M002', 'M003'],
            'mg_kod': ['MG1', 'MG2', 'MG1'],
            'cover_hedef': [12.0, 15.0, 10.0],
            'bkar_hedef': [25.0, 30.0, 20.0]
        }),
        'aciklama': 'Marka-mal grubu KPI hedefleri',
        'icon': '🎯'
    }
}

# Örnek CSV'ler indirme bölümü
with st.expander("📥 Örnek CSV Dosyalarını İndir", expanded=False):
    st.info("Sistemde kullanılacak veri formatlarının örnek dosyalarını aşağıdan indirebilirsiniz.")
    
    # Tümünü İndir butonu
    col1, col2 = st.columns([3, 1])
    with col2:
        # ZIP dosyası oluştur
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, file_info in example_csvs.items():
                csv_data = file_info['data'].to_csv(index=False, encoding='utf-8-sig')
                zip_file.writestr(filename, csv_data)
        
        st.download_button(
            label="📦 Tümünü İndir (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="ornek_csv_dosyalari.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Tablo formatında gösterim
    table_data = []
    for filename, file_info in example_csvs.items():
        table_data.append({
            'Icon': file_info['icon'],
            'Dosya Adı': filename,
            'Açıklama': file_info['aciklama'],
            'Satır': len(file_info['data']),
            'Kolon': len(file_info['data'].columns)
        })
    
    table_df = pd.DataFrame(table_data)
    
    # Tabloyu göster
    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Icon": st.column_config.TextColumn("", width="small"),
            "Dosya Adı": st.column_config.TextColumn("Dosya Adı", width="medium"),
            "Açıklama": st.column_config.TextColumn("Açıklama", width="large"),
            "Satır": st.column_config.NumberColumn("Satır", width="small"),
            "Kolon": st.column_config.NumberColumn("Kolon", width="small")
        }
    )
    
    st.markdown("---")
    st.markdown("**📥 Tekli İndirme:**")
    
    # Grid düzeni için tekli indirme butonları
    cols = st.columns(3)
    for idx, (filename, file_info) in enumerate(example_csvs.items()):
        with cols[idx % 3]:
            st.download_button(
                label=f"{file_info['icon']} {filename}",
                data=file_info['data'].to_csv(index=False, encoding='utf-8-sig'),
                file_name=filename,
                mime="text/csv",
                key=f"download_{filename}",
                use_container_width=True
            )

st.markdown("---")

# Veri tanımları
data_definitions = {
    'urun_master': {
        'name': 'Ürün Master',
        'required': True,
        'columns': ['urun_kod', 'urun_ad', 'satici_kod', 'satici_ad', 'kategori_kod', 'kategori_ad', 
                   'umg', 'umg_ad', 'mg', 'mg_ad', 'marka_kod', 'marka_ad', 'klasman_kod', 'klasman_ad',
                   'nitelik', 'durum', 'ithal', 'ithal_ad', 'tanim', 'koli_ici', 'paket_ici', 'olcu_birimi'],
        'state_key': 'urun_master',
        'icon': '📦',
        'modules': ['Sevkiyat', 'PO', 'Prepack']
    },
    'magaza_master': {
        'name': 'Mağaza Master',
        'required': True,
        'columns': ['magaza_kod', 'magaza_ad', 'il', 'bolge', 'tip', 'adres_kod', 'sm', 'bs', 'depo_kod'],
        'state_key': 'magaza_master',
        'icon': '🏪',
        'modules': ['Sevkiyat', 'PO']
    },
    'depo_stok': {
        'name': 'Depo Stok',
        'required': True,
        'columns': ['depo_kod', 'depo_ad', 'urun_kod', 'stok'],
        'state_key': 'depo_stok',
        'icon': '📦',
        'modules': ['Sevkiyat', 'PO']
    },
    'anlik_stok_satis': {
        'name': 'Anlık Stok/Satış',
        'required': True,
        'columns': ['magaza_kod', 'urun_kod', 'stok', 'yol', 'satis', 'ciro', 'smm'],
        'state_key': 'anlik_stok_satis',
        'icon': '📊',
        'modules': ['Sevkiyat', 'PO']
    },
    'kpi': {
        'name': 'KPI',
        'required': True,
        'columns': ['mg_id', 'min_deger', 'max_deger', 'forward_cover'],
        'state_key': 'kpi',
        'icon': '🎯',
        'modules': ['Sevkiyat', 'PO']
    },
    'yasak_master': {
        'name': 'Yasak',
        'required': False,
        'columns': ['urun_kod', 'magaza_kod', 'yasak_durum'],
        'state_key': 'yasak_master',
        'icon': '🚫',
        'modules': ['Sevkiyat']
    },
    'haftalik_trend': {
        'name': 'Haftalık Trend',
        'required': False,
        'columns': ['klasman_kod', 'marka_kod', 'yil', 'hafta', 'stok', 'satis', 'ciro', 'smm', 'iftutar'],
        'state_key': 'haftalik_trend',
        'icon': '📈',
        'modules': ['Sevkiyat']
    },
    'po_yasak': {
        'name': 'PO Yasak',
        'required': False,
        'columns': ['urun_kodu', 'yasak_durum', 'acik_siparis'],
        'state_key': 'po_yasak',
        'icon': '🚫',
        'modules': ['PO']
    },
    'po_detay_kpi': {
        'name': 'PO Detay KPI',
        'required': False,
        'columns': ['marka_kod', 'mg_kod', 'cover_hedef', 'bkar_hedef'],
        'state_key': 'po_detay_kpi',
        'icon': '🎯',
        'modules': ['PO']
    }
}

# ÇOKLU DOSYA YÜKLEME bölümünü güncelle
st.subheader("📤 Çoklu Dosya Yükleme")

uploaded_files = st.file_uploader(
    "CSV dosyalarını seçin (birden fazla seçebilirsiniz)",
    type=['csv'],
    accept_multiple_files=True,
    key="multi_upload"
)

if uploaded_files:
    st.write(f"**{len(uploaded_files)} dosya seçildi**")
    
    # DEBUG: Seçilen dosyaları göster
    st.write("**DEBUG - Seçilen dosyalar:**", [file.name for file in uploaded_files])
    
    if st.button("🚀 Tüm Dosyaları Yükle", type="primary", use_container_width=True):
        upload_results = []
        
        for uploaded_file in uploaded_files:
            filename = uploaded_file.name.lower()
            st.write(f"**DEBUG - İşlenen dosya:** {uploaded_file.name}")
            
            # Dosya adından veri tipini bul
            matched_key = None
            for key, definition in data_definitions.items():
                # DEBUG: Her kontrolü göster
                check1 = key in filename
                check2 = definition['name'].lower().replace(' ', '_') in filename
                st.write(f"  DEBUG - {key}: '{key}' in '{filename}' = {check1}")
                st.write(f"  DEBUG - {key}: '{definition['name'].lower().replace(' ', '_')}' in '{filename}' = {check2}")
                
                if key in filename or definition['name'].lower().replace(' ', '_') in filename:
                    matched_key = key
                    st.write(f"  DEBUG - Eşleşme bulundu: {matched_key}")
                    break
            
            if not matched_key:
                st.write(f"  DEBUG - Eşleşme bulunamadı!")
                upload_results.append({
                    'Dosya': uploaded_file.name,
                    'Veri Tipi': '❓ Bilinmiyor',
                    'Durum': '❌ Eşleştirilemedi',
                    'Detay': 'Dosya adı tanımlı veri tiplerine uymuyor'
                })
                continue
            
            definition = data_definitions[matched_key]
            st.write(f"  DEBUG - Tanım: {definition['name']}")
            
            try:
                df = pd.read_csv(uploaded_file)
                st.write(f"  DEBUG - CSV okundu: {len(df)} satır, {len(df.columns)} kolon")
                st.write(f"  DEBUG - Kolonlar: {list(df.columns)}")
                
                # Kolon kontrolü
                existing_cols = set(df.columns)
                required_cols = set(definition['columns'])
                missing_cols = required_cols - existing_cols
                extra_cols = existing_cols - required_cols
                
                st.write(f"  DEBUG - Eksik kolonlar: {missing_cols}")
                st.write(f"  DEBUG - Fazla kolonlar: {extra_cols}")
                
                if missing_cols:
                    upload_results.append({
                        'Dosya': uploaded_file.name,
                        'Veri Tipi': f"{definition['icon']} {definition['name']}",
                        'Durum': '❌ Başarısız',
                        'Detay': f"Eksik kolonlar: {', '.join(list(missing_cols)[:3])}"
                    })
                else:
                    # Sadece gerekli kolonları al
                    df_clean = df[definition['columns']].copy()
                    st.session_state[definition['state_key']] = df_clean
                    
                    modules_str = ', '.join(definition['modules'])
                    detay = f"✅ {len(df_clean):,} satır → Kullanıldığı modüller: {modules_str}"
                    if extra_cols:
                        detay += f" (fazla kolonlar kaldırıldı)"
                    
                    upload_results.append({
                        'Dosya': uploaded_file.name,
                        'Veri Tipi': f"{definition['icon']} {definition['name']}",
                        'Durum': '✅ Başarılı',
                        'Detay': detay
                    })
                    
                    st.write(f"  DEBUG - Başarıyla yüklendi: {definition['state_key']}")
            
            except Exception as e:
                st.write(f"  DEBUG - HATA: {str(e)}")
                upload_results.append({
                    'Dosya': uploaded_file.name,
                    'Veri Tipi': f"{definition['icon']} {definition['name']}",
                    'Durum': '❌ Hata',
                    'Detay': str(e)
                })
        
        # Sonuçları göster
        st.markdown("---")
        st.subheader("📋 Yükleme Sonuçları")
        
        results_df = pd.DataFrame(upload_results)
        
        def highlight_upload_results(row):
            if '✅ Başarılı' in row['Durum']:
                return ['background-color: #d4edda'] * len(row)
            elif '❌' in row['Durum']:
                return ['background-color: #f8d7da'] * len(row)
            else:
                return ['background-color: #fff3cd'] * len(row)
        
        st.dataframe(
            results_df.style.apply(highlight_upload_results, axis=1),
            use_container_width=True,
            hide_index=True
        )
        
        success_count = sum(1 for r in upload_results if '✅ Başarılı' in r['Durum'])
        st.success(f"✅ {success_count} / {len(upload_results)} dosya başarıyla yüklendi!")
        
        time.sleep(1)
        st.rerun()


# VERİ DURUMU TABLOSU
st.subheader("📊 Veri Yükleme Durumu")

# Durum tablosunu oluştur
status_data = []
for key, definition in data_definitions.items():
    data = st.session_state.get(definition['state_key'])
    
    if data is not None and len(data) > 0:
        status = '✅ Yüklü'
        row_count = len(data)
        
        # Eksik kolon kontrolü
        existing_cols = set(data.columns)
        required_cols = set(definition['columns'])
        missing_cols = required_cols - existing_cols
        
        if missing_cols:
            kolon_durumu = f"⚠️ Eksik kolon var"
        else:
            kolon_durumu = '✅ Tam'
    else:
        status = '❌ Yüklenmedi'
        row_count = 0
        kolon_durumu = '-'
    
    # Beklenen kolonları liste olarak
    expected_cols_str = ', '.join(definition['columns'][:5])
    if len(definition['columns']) > 5:
        expected_cols_str += f"... (+{len(definition['columns'])-5})"
    
    # Kullanıldığı modüller
    modules_str = ', '.join(definition['modules'])
    
    status_data.append({
        'Veri': f"{definition['icon']} {definition['name']}",
        'Zorunlu': '🔴' if definition['required'] else '🟢',
        'Durum': status,
        'Satır': f"{row_count:,}" if row_count > 0 else '-',
        'Kolon': kolon_durumu,
        'Kullanıldığı Modüller': modules_str
    })

status_df = pd.DataFrame(status_data)

# Renk kodlaması
def highlight_status(row):
    if '✅ Yüklü' in row['Durum']:
        return ['background-color: #d4edda'] * len(row)
    elif '❌ Yüklenmedi' in row['Durum'] and '🔴' in row['Zorunlu']:
        return ['background-color: #f8d7da'] * len(row)
    else:
        return [''] * len(row)

st.dataframe(
    status_df.style.apply(highlight_status, axis=1),
    use_container_width=True,
    hide_index=True
)

# Bilgilendirme
st.info("""
**💡 Veri Yapısı:**
- 🔴 Zorunlu veriler mutlaka yüklenmeli | 🟢 Opsiyonel
- **Master'lar** diğer tablolara join için kullanılır
- Diğer CSV'lerde sadece **kod** kolonları, **ad** kolonları master'lardan gelir
- **Yasak**: yasak_durum = 1 (yasak), 0 veya yok (yasak değil)
""")

# Özet bilgiler
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_loaded = sum(1 for _, def_data in data_definitions.items() 
                      if st.session_state.get(def_data['state_key']) is not None 
                      and len(st.session_state.get(def_data['state_key'])) > 0)
    st.metric("📂 Yüklü", f"{total_loaded}/{len(data_definitions)}")

with col2:
    required_count = sum(1 for def_data in data_definitions.values() if def_data['required'])
    required_loaded = sum(1 for _, def_data in data_definitions.items() 
                         if def_data['required'] 
                         and st.session_state.get(def_data['state_key']) is not None
                         and len(st.session_state.get(def_data['state_key'])) > 0)
    st.metric("🔴 Zorunlu", f"{required_loaded}/{required_count}")

with col3:
    total_rows = sum(len(st.session_state.get(def_data['state_key'])) 
                    for def_data in data_definitions.values() 
                    if st.session_state.get(def_data['state_key']) is not None)
    st.metric("📊 Toplam Satır", f"{total_rows:,}")

with col4:
    if st.button("🗑️ Tümünü Sil", use_container_width=True):
        for def_data in data_definitions.values():
            st.session_state[def_data['state_key']] = None
        st.success("✅ Tüm veriler silindi!")
        time.sleep(0.5)
        st.rerun()

st.markdown("---")

# TEK DOSYA DETAYI
st.subheader("🔍 Detaylı Veri İncelemesi")

selected_data = st.selectbox(
    "İncelemek istediğiniz veriyi seçin:",
    options=[k for k in data_definitions.keys() if st.session_state.get(data_definitions[k]['state_key']) is not None],
    format_func=lambda x: f"{data_definitions[x]['icon']} {data_definitions[x]['name']}",
    key="detail_select"
) if any(st.session_state.get(data_definitions[k]['state_key']) is not None for k in data_definitions.keys()) else None

if selected_data:
    current_def = data_definitions[selected_data]
    data = st.session_state[current_def['state_key']]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Satır", f"{len(data):,}")
    with col2:
        st.metric("Kolon", len(data.columns))
    with col3:
        st.metric("Bellek", f"{data.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")
    
    st.write("**Kullanıldığı Modüller:**")
    modules_badges = " ".join([f"`{m}`" for m in current_def['modules']])
    st.markdown(modules_badges)
    
    st.write("**Beklenen Kolonlar:**")
    st.code(', '.join(current_def['columns']), language=None)
    
    st.dataframe(data.head(20), use_container_width=True, height=300)
else:
    st.info("Henüz yüklenmiş veri yok")

st.markdown("---")

# Başarı mesajı
if required_loaded == required_count and required_count > 0:
    st.success("""
    ✅ **Tüm zorunlu veriler yüklendi!**
    
    Artık şu modüllere geçebilirsiniz:
    - 🚚 Sevkiyat Planlama
    - 💵 Alım Sipariş (PO)
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➡️ Sevkiyat Modülüne Git", use_container_width=True):
            st.switch_page("pages/2_Sevkiyat.py")
    with col2:
        if st.button("➡️ Alım Sipariş Modülüne Git", use_container_width=True):
            st.switch_page("pages/4_PO.py")

