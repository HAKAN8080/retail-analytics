import streamlit as st

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Prepack Optimization",
    page_icon="📦",
    layout="wide"
)

# Basit navigasyon
with st.sidebar:
    st.page_link("app.py", label="🏠 Ana Sayfa", icon="🏠")
    st.page_link("pages/1_Veri_Yukleme.py", label="📤 Veri Yükleme", icon="📂") 
    st.page_link("pages/2_Lost_Sales.py", label="📈 Lost Sales", icon="📈")
    st.page_link("pages/3_Prepack_Optimization.py", label="📦 Prepack Optimization", icon="📦")

# Sadece yapım aşamasında mesajı
st.title("📦 Prepack Optimization")
st.markdown("---")

st.info("🚧 **Yapım Aşamasında**")
st.write("Bu sayfa şu anda geliştirme aşamasındadır. Yakında kullanıma sunulacaktır.")

# İsteğe bağlı: Boşluk için biraz space
for _ in range(10):
    st.write("")


