import streamlit as st
import pandas as pd

# ============================================
# SAYFA YAPILANDIRMASI
# ============================================
st.set_page_config(
    page_title="Retail Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Hızlı Erişim Linkleri
st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Hızlı Erişim")

st.sidebar.page_link("pages/0_Veri_Yukleme.py", label="📤 Veri Yükleme", icon="📂")
st.sidebar.markdown("---")
st.sidebar.page_link("pages/1_Lost_Sales.py", label="📉 Lost Sales", icon="📊")
st.sidebar.page_link("pages/2_Sevkiyat.py", label="🚚 Sevkiyat Planlama", icon="📦")
st.sidebar.page_link("pages/3_Prepack_Optimization.py", label="📦 Prepack Optimizasyon", icon="📦")
st.sidebar.page_link("pages/4_PO.py", label="💵 Alım Sipariş (PO)", icon="🛒")

st.sidebar.markdown("---")
st.sidebar.info("""
**💡 İpucu:**
Modüllere sol menüden veya yukarıdaki hızlı erişim butonlarından ulaşabilirsiniz.
""")
