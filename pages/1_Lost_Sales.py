import streamlit as st
import pandas as pd

# Sayfa config
st.set_page_config(
    page_title="Lost Sales Analizi",
    page_icon="📉",
    layout="wide"
)

st.title("📉 Lost Sales Analizi")
st.markdown("---")

# Yapım aşamasında mesajı
st.info("🚧 **Bu sayfa yapım aşamasındadır.** 🚧")

st.markdown("""
### Yakında Eklenecek Özellikler:

- 📊 Satış kaybı analizi
- 📈 Stok yetersizliği raporları
- 🎯 Ürün ve mağaza bazında kayıp hesaplamaları
- 📉 Trend analizleri
- 💰 Gelir kaybı tahminleri

---

**Not:** Bu sayfa şu anda aktif değildir. Diğer sayfaları kullanabilirsiniz:
- 🏠 Ana Sayfa
- 💾 Veri Yükleme
- 📦 Sevkiyat Planlama
- 💵 Alım Sipariş (PO)
""")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if st.button("⬅️ Ana Sayfaya Dön", use_container_width=True):
        st.switch_page("app.py")

with col2:
    if st.button("➡️ Sevkiyat Planlamaya Git", use_container_width=True):
        st.switch_page("pages/2_Sevkiyat.py")
