import streamlit as st
import pandas as pd
import numpy as np



# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Prepack Optimization",
    page_icon="📦",
    layout="wide"
)

# Basit sidebar navigasyon
st.sidebar.title("🔗 Navigasyon")

# Manuel butonlarla navigasyon - UNIQUE KEY'LER EKLENDİ
col1, col2, col3, col4 = st.sidebar.columns(4)
with col1:
    if st.button("🏠", help="Ana Sayfa", key="prepack_nav_home"):
        st.switch_page("app.py")
with col2:
    if st.button("📤", help="Veri Yükleme", key="prepack_nav_data"):
        st.switch_page("pages/1_Veri_Yukleme.py")
with col3:
    if st.button("📈", help="Lost Sales", key="prepack_nav_lost"):
        st.switch_page("pages/2_Lost_Sales.py")
with col4:
    if st.button("📦", help="Prepack Optimization", key="prepack_nav_prepack"):
        st.switch_page("pages/3_Prepack_Optimization.py")

# Sayfa içeriği - Sadece yapım aşamasında mesajı
st.title("📦 Prepack Optimization")
st.markdown("---")

st.info("🚧 **Yapım Aşamasında**")
st.write("Bu sayfa şu anda geliştirme aşamasındadır. Yakında kullanıma sunulacaktır.")

# Boşluk için
for _ in range(8):
    st.write("")
