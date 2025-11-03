import streamlit as st
import pandas as pd
import numpy as np

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

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Prepack Optimization",
    page_icon="📦",
    layout="wide"
)

# Basit sidebar navigasyon
st.sidebar.title("🔗 Navigasyon")

# Manuel butonlarla navigasyon
col1, col2, col3, col4 = st.sidebar.columns(4)

with col1:
    if st.button("🏠", help="Ana Sayfa"):
        st.switch_page("app.py")

with col2:
    if st.button("📤", help="Veri Yükleme"):
        st.switch_page("pages/1_Veri_Yukleme.py")

with col3:
    if st.button("📈", help="Lost Sales"):
        st.switch_page("pages/2_Lost_Sales.py")

with col4:
    if st.button("📦", help="Prepack Optimization"):
        st.switch_page("pages/3_Prepack_Optimization.py")

# Sayfa içeriği - Sadece yapım aşamasında mesajı
st.title("📦 Prepack Optimization")
st.markdown("---")

st.info("🚧 **Yapım Aşamasında**")
st.write("Bu sayfa şu anda geliştirme aşamasındadır. Yakında kullanıma sunulacaktır.")

# Boşluk için
for _ in range(8):
    st.write("")
