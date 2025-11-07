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
# HOŞ GELDİNİZ
# ============================================
st.warning("""
    ### ⚠️ Büyük kararlar doğru algoritmalar ile alınır
     - Yapay zeka, ML destekli
    -  Güvenilir
    -  Hızlı
    """)
