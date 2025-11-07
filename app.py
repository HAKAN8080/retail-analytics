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
# ============================================
# ANA SAYFA
# ============================================
st.title("📊 Retail Analytics Platform")
st.markdown("---")
# ============================================
# ANA SAYFA
# ============================================
st.title("📊 Retail Analytics Platform")
st.markdown("---")

# ============================================
# HOŞ GELDİNİZ
# ============================================
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### 👋 Hoş Geldiniz! """)
    
    st.success("""
    **🚀 Hızlı Başlangıç:**
    1. Sol menüden bir modül seçin (Lost Sales, Sevkiyat, PO, Prepack)
    2. CSV dosyalarınızı yükleyin
    3. Parametreleri ayarlayın
    4. Analiz sonuçlarını görüntüleyin
    5. Raporları CSV formatında indirin
    """)

with col2:
    st.info("""
    ### 📚 Kullanım Kılavuzu""")

st.markdown("---")
