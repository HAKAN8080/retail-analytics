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


# CSV okuma fonksiyonu - virgül sorunu için özelleştirilmiş
def read_csv_safe(file):
    try:
        # Önce noktalı virgül ile dene
        df = pd.read_csv(
            file, 
            sep=';', 
            encoding='utf-8-sig',
            quoting=1,  # QUOTE_ALL: Tüm alanları tırnak içine al
            on_bad_lines='warn'
        )
        return df, ';'
    except:
        try:
            # Noktalı virgül çalışmazsa normal virgül dene
            file.seek(0)  # Dosyayı başa sar
            df = pd.read_csv(
                file, 
                sep=',', 
                encoding='utf-8-sig',
                quoting=1,
                on_bad_lines='warn'
            )
            return df, ','
        except Exception as e:
            raise Exception(f"CSV okuma hatası: {str(e)}")

# CSV yazma fonksiyonu
def write_csv_safe(df):
    return df.to_csv(
        index=False, 
        sep=';', 
        encoding='utf-8-sig',
        quoting=1  # Tüm alanları tırnak içine al
    )

# Örnek CSV'ler - GÜNCELLENEN URUN_MASTER
example_csvs = {
    'urun_master.csv': {
        'data': pd.DataFrame({
            'urun_kod': ['U001', 'U002', 'U003'],
            'satici_kod': ['S001', 'S002', 'S001'],
            'kategori_kod': ['K001', 'K002', 'K001'],
            'umg': ['UMG1', 'UMG2', 'UMG1'],
            'mg': ['MG1', 'MG2', 'MG1'],
            'marka_kod': ['M001', 'M002', 'M001'],
            'klasman_kod': ['K1', 'K2', 'K1'],
            'nitelik': ['Nitelik 1, özellik A', 'Nitelik 2, özellik B', 'Nitelik 1, özellik C'],
            'durum': ['Aktif', 'Aktif', 'Pasif'],
            'ithal': [1, 0, 1],
            'olcu_birimi': ['Adet', 'Adet', 'Kg'],
            'koli_ici': [12, 24, 6],
            'paket_ici': [6, 12, 3]
        }),
        'aciklama': 'Ürün bilgileri (sadeleştirilmiş)',
        'icon': '📦'
    },
    'magaza_master.csv': {
        'data': pd.DataFrame({
            'magaza_kod': ['M001', 'M002', 'M003'],
            'il': ['İstanbul', 'Ankara', 'İzmir'],
            'bolge': ['Marmara', 'İç Anadolu', 'Ege'],
            'tip': ['Hipermarket', 'Süpermarket', 'Hipermarket'],
            'adres_kod': ['ADR001', 'ADR002', 'ADR003'],
            'sm': [5000, 3000, 4500],
            'bs': ['BS1', 'BS2', 'BS1'],
            'depo_kod': ['D001', 'D001', 'D002']
        }),
        'aciklama': 'Mağaza bilgileri (sadeleştirilmiş)',
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
            'urun_kod': ['U001', 'U002', 'U001'],
            'stok': [1000, 1500, 800]
        }),
        'aciklama': 'Depo bazında stok miktarları (sadeleştirilmiş)',
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
                csv_data = write_csv_safe(file_info['data'])
                zip_file.writestr(filename, csv_data)
        
        st.download_button(
            label="📦 Tümünü İndir (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="ornek_csv_dosyalari.zip",
            mime="application/zip",
            type="primary",
            width='stretch'
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
        width='stretch',
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
                data=write_csv_safe(file_info['data']),
                file_name=filename,
                mime="text/csv",
                key=f"download_{filename}",
                width='stretch'
            )

st.markdown("---")

# Veri tanımları - GÜNCELLENEN URUN_MASTER
data_definitions = {
    'urun_master': {
        'name': 'Ürün Master',
        'required': True,
        'columns': ['urun_kod', 'satici_kod', 'kategori_kod', 'umg', 'mg', 'marka_kod', 
                   'klasman_kod', 'nitelik', 'durum', 'ithal', 'olcu_birimi', 'koli_ici', 'paket_ici'],
        'state_key': 'urun_master',
        'icon': '📦',
        'modules': ['Sevkiyat', 'PO', 'Prepack'],
        'description': '⚠️ Sadece kod alanları kullanılır, ad alanları artık gerekmemektedir'
    },
    'magaza_master': {
        'name': 'Mağaza Master',
        'required': True,
        'columns': ['magaza_kod', 'il', 'bolge', 'tip', 'adres_kod', 'sm', 'bs', 'depo_kod'],
        'state_key': 'magaza_master',
        'icon': '🏪',
        'modules': ['Sevkiyat', 'PO'],
        'description': '⚠️ Sadece kod alanları kullanılır, ad alanları kaldırıldı'
    },
    'depo_stok': {
        'name': 'Depo Stok',
        'required': True,
        'columns': ['depo_kod', 'urun_kod', 'stok'],
        'state_key': 'depo_stok',
        'icon': '📦',
        'modules': ['Sevkiyat', 'PO'],
        'description': '⚠️ Sadece kod alanları kullanılır, ad alanları kaldırıldı'
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

# ÇOKLU DOSYA YÜKLEME
st.subheader("📤 Çoklu Dosya Yükleme")

# Separator seçimi
col1, col2 = st.columns([2, 1])
with col2:
    separator_option = st.selectbox(
        "CSV Ayracı:",
        options=['Otomatik Algıla', 'Noktalı Virgül (;)', 'Virgül (,)', 'Tab (\\t)'],
        help="CSV dosyanızdaki alan ayracını seçin"
    )
    
    separator_map = {
        'Otomatik Algıla': 'auto',
        'Noktalı Virgül (;)': ';',
        'Virgül (,)': ',',
        'Tab (\\t)': '\t'
    }
    selected_separator = separator_map[separator_option]

uploaded_files = st.file_uploader(
    "CSV dosyalarını seçin (birden fazla seçebilirsiniz)",
    type=['csv'],
    accept_multiple_files=True,
    key="multi_upload"
)

if uploaded_files:
    st.write(f"**{len(uploaded_files)} dosya seçildi**")
    
    if st.button("🚀 Tüm Dosyaları Yükle", type="primary", width='stretch'):
        upload_results = []
        
        for uploaded_file in uploaded_files:
            filename = uploaded_file.name.lower()
            
            # Dosya adından veri tipini bul
            matched_key = None
            for key, definition in data_definitions.items():
                if key in filename or definition['name'].lower().replace(' ', '_') in filename:
                    matched_key = key
                    break
            
            if not matched_key:
                upload_results.append({
                    'Dosya': uploaded_file.name,
                    'Veri Tipi': '❓ Bilinmiyor',
                    'Durum': '❌ Eşleştirilemedi',
                    'Detay': 'Dosya adı tanımlı veri tiplerine uymuyor'
                })
                continue
            
            definition = data_definitions[matched_key]
            
            try:
                # CSV okuma - güvenli yöntem
                if selected_separator == 'auto':
                    df, used_sep = read_csv_safe(uploaded_file)
                    sep_info = f" (Kullanılan: '{used_sep}')"
                else:
                    df = pd.read_csv(
                        uploaded_file,
                        sep=selected_separator,
                        encoding='utf-8-sig',
                        quoting=1,
                        on_bad_lines='warn'
                    )
                    sep_info = ""
                
                # Kolon kontrolü
                existing_cols = set(df.columns)
                required_cols = set(definition['columns'])
                missing_cols = required_cols - existing_cols
                extra_cols = existing_cols - required_cols
                
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
                    
                    # String kolonlardaki fazla boşlukları temizle
                    string_columns = df_clean.select_dtypes(include=['object']).columns
                    for col in string_columns:
                        df_clean[col] = df_clean[col].str.strip() if df_clean[col].dtype == 'object' else df_clean[col]
                    
                    st.session_state[definition['state_key']] = df_clean
                    
                    modules_str = ', '.join(definition['modules'])
                    detay = f"✅ {len(df_clean):,} satır{sep_info} → Modüller: {modules_str}"
                    if extra_cols:
                        detay += f" (fazla kolonlar kaldırıldı)"
                    
                    upload_results.append({
                        'Dosya': uploaded_file.name,
                        'Veri Tipi': f"{definition['icon']} {definition['name']}",
                        'Durum': '✅ Başarılı',
                        'Detay': detay
                    })
            
            except Exception as e:
                upload_results.append({
                    'Dosya': uploaded_file.name,
                    'Veri Tipi': f"{definition['icon']} {definition['name']}",
                    'Durum': '❌ Hata',
                    'Detay': str(e)[:50]
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
            width='stretch',
            hide_index=True
        )
        
        success_count = sum(1 for r in upload_results if '✅ Başarılı' in r['Durum'])
        st.success(f"✅ {success_count} / {len(upload_results)} dosya başarıyla yüklendi!")
        
        time.sleep(1)
        st.rerun()

st.markdown("---")

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
    
    # Açıklama ekle
    description = definition.get('description', '')
    
    status_data.append({
        'Veri': f"{definition['icon']} {definition['name']}",
        'Zorunlu': '🔴' if definition['required'] else '🟢',
        'Durum': status,
        'Satır': f"{row_count:,}" if row_count > 0 else '-',
        'Kolon': kolon_durumu,
        'Kullanıldığı Modüller': modules_str,
        'Not': description
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
    width='stretch',
    hide_index=True
)


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
    if st.button("🗑️ Tümünü Sil", width='stretch'):
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
    
    # Açıklama varsa göster
    if 'description' in current_def and current_def['description']:
        st.info(current_def['description'])
    
    st.dataframe(data.head(20), width='stretch', height=300)
    
    # Veri kalitesi kontrolü
    with st.expander("📊 Veri Kalitesi Raporu"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Eksik Değerler:**")
            missing = data.isnull().sum()
            if missing.any():
                st.dataframe(missing[missing > 0].to_frame('Eksik Sayısı'))
            else:
                st.success("Eksik değer yok")
        
        with col2:
            st.write("**Veri Tipleri:**")
            dtypes = data.dtypes.to_frame('Veri Tipi')
            st.dataframe(dtypes)
        
        # String kolonlarda virgül kontrolü
        string_cols = data.select_dtypes(include=['object']).columns
        if len(string_cols) > 0:
            st.write("**String Kolonlarda Virgül Kontrolü:**")
            comma_check = {}
            for col in string_cols:
                comma_count = data[col].astype(str).str.contains(',').sum()
                if comma_count > 0:
                    comma_check[col] = comma_count
            
            if comma_check:
                st.warning(f"⚠️ Aşağıdaki kolonlarda virgül içeren değerler var:")
                for col, count in comma_check.items():
                    st.write(f"- {col}: {count} satır")
            else:
                st.success("✅ String kolonlarda virgül sorunu yok")
else:
    st.info("Henüz yüklenmiş veri yok")

st.markdown("---")

# CSV İhracat Bölümü
st.subheader("📤 Veri İhracat")

if any(st.session_state.get(data_definitions[k]['state_key']) is not None for k in data_definitions.keys()):
    export_data = st.selectbox(
        "İhraç etmek istediğiniz veriyi seçin:",
        options=[k for k in data_definitions.keys() if st.session_state.get(data_definitions[k]['state_key']) is not None],
        format_func=lambda x: f"{data_definitions[x]['icon']} {data_definitions[x]['name']}",
        key="export_select"
    )
    
    if export_data:
        export_def = data_definitions[export_data]
        export_df = st.session_state[export_def['state_key']]
        
        col1, col2 = st.columns(2)
        with col1:
            csv_data = write_csv_safe(export_df)
            st.download_button(
                label=f"📥 {export_def['name']}.csv İndir (Noktalı Virgül)",
                data=csv_data,
                file_name=f"{export_def['name'].lower().replace(' ', '_')}.csv",
                mime="text/csv",
                width='stretch'
            )
        
        with col2:
            csv_data_comma = export_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label=f"📥 {export_def['name']}.csv İndir (Virgül)",
                data=csv_data_comma,
                file_name=f"{export_def['name'].lower().replace(' ', '_')}_comma.csv",
                mime="text/csv",
                width='stretch'
            )
else:
    st.info("İhraç edilecek veri yok")

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
        if st.button("➡️ Sevkiyat Modülüne Git", width='stretch'):
            st.switch_page("pages/2_Sevkiyat.py")
    with col2:
        if st.button("➡️ Alım Sipariş Modülüne Git", width='stretch'):
            st.switch_page("pages/4_PO.py")




