"""
🚀 E-Commerce Sevkiyat Optimizasyon Sistemi
Ana Streamlit Uygulaması
"""
import streamlit as st
import pandas as pd
from modules.data_loader import DataLoader
from modules.analytics_engine import AnalyticsEngine
from modules.allocation_optimizer import AllocationOptimizer
from modules.alert_manager import AlertManager
from modules.visualizations import Visualizations
from shipment_strategy_page import show_shipment_strategy_page
from settings_page import show_settings_page
from pricing_strategy_page import show_pricing_strategy_page
from utils.helpers import (
    format_number, format_currency, format_percentage,
    show_success, show_error, show_info
)
from utils.constants import KPI_TARGETS, SEGMENT_COLORS, SEGMENT_EMOJI

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Sevkiyat Optimizasyonu",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stAlert {
        padding: 1rem;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False

def load_and_analyze_data():
    """Veri yükle ve analiz et"""
    
    with st.spinner('🔄 Veri yükleniyor ve analiz ediliyor...'):
        # Data loader
        loader = DataLoader()
        df = loader.load_sample_data()
        
        if df is not None:
            # Custom parametreleri al (varsa)
            segment_params = st.session_state.get('custom_segment_params', None)
            transfer_lead_time = st.session_state.get('custom_transfer_lead_time', 5)
            
            # Analytics engine (seasonal forecasting ile)
            historical_path = 'data/historical_sales.csv'  # Opsiyonel
            analytics = AnalyticsEngine(df, segment_params=segment_params, historical_data_path=historical_path)
            df = analytics.calculate_all_metrics()
            df = analytics.segment_products()
            
            # Allocation optimizer
            optimizer = AllocationOptimizer(df, segment_params=segment_params, transfer_lead_time=transfer_lead_time)
            allocation_df = optimizer.generate_allocation_strategy()
            
            # Alert manager
            alert_mgr = AlertManager(df, allocation_df)
            alerts_df = alert_mgr.generate_all_alerts()
            
            # Session state'e kaydet
            st.session_state.df = df
            st.session_state.allocation_df = allocation_df
            st.session_state.alerts_df = alerts_df
            st.session_state.analytics = analytics
            st.session_state.optimizer = optimizer
            st.session_state.alert_mgr = alert_mgr
            st.session_state.data_loaded = True
            st.session_state.analyzed = True
            
            show_success("Analiz tamamlandı!")
            return True
        else:
            show_error("Veri yüklenemedi!")
            return False

def main():
    """Ana uygulama"""
    
    # Header
    st.markdown('<div class="main-header">📦 Sevkiyat Optimizasyonu</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/000000/rocket.png", width=80)
        st.title("📊 Menü")
        
        # Veri yükleme butonu
        if st.button("🔄 Veriyi Yükle ve Analiz Et", use_container_width=True):
            load_and_analyze_data()
        
        st.divider()
        
        # Menü
        page = st.radio(
            "Sayfalar",
            [
                "🏠 Ana Sayfa",
                "📊 Dashboard",
                "🔍 Ürün Analizi",
                "📦 Sevkiyat Stratejisi",
                "🏷️ Fiyatlama & İndirim",
                "🚨 Kritik Uyarılar",
                "⚙️ Ayarlar"
            ],
            label_visibility="collapsed"
        )
        
        # Veri durumu
        st.divider()
        if st.session_state.data_loaded:
            st.success("✅ Veri yüklü")
            st.caption(f"📦 {len(st.session_state.df)} ürün")
        else:
            st.warning("⚠️ Veri yüklenmedi")
            st.caption("Yukarıdaki butona tıklayın")
    
    # Ana içerik
    if page == "🏠 Ana Sayfa":
        show_home_page()
    elif page == "📊 Dashboard":
        if st.session_state.data_loaded:
            show_dashboard_page()
        else:
            st.warning("⚠️ Lütfen önce veriyi yükleyin!")
    elif page == "🔍 Ürün Analizi":
        if st.session_state.data_loaded:
            show_product_analysis_page()
        else:
            st.warning("⚠️ Lütfen önce veriyi yükleyin!")
    elif page == "📦 Sevkiyat Stratejisi":
        if st.session_state.data_loaded:
            show_shipment_strategy_page()
        else:
            st.warning("⚠️ Lütfen önce veriyi yükleyin!")
    elif page == "🏷️ Fiyatlama & İndirim":
        if st.session_state.data_loaded:
            show_pricing_strategy_page()
        else:
            st.warning("⚠️ Lütfen önce veriyi yükleyin!")
    elif page == "🚨 Kritik Uyarılar":
        if st.session_state.data_loaded:
            show_alerts_page()
        else:
            st.warning("⚠️ Lütfen önce veriyi yükleyin!")
    elif page == "⚙️ Ayarlar":
        show_settings_page()

def show_home_page():
    """Ana sayfa"""
    
    st.markdown("## 👋 Hoşgeldiniz!")
    
    st.markdown("""
    Bu sistem, e-ticaret operasyonlarınızda ürün sevkiyatını optimize etmek için geliştirilmiştir.
    
    ### 🎯 Özellikler:
    
    - **📊 Dashboard**: Genel görünüm ve KPI'lar
    - **🔍 Ürün Analizi**: Detaylı ürün bazlı analiz
    - **📦 Sevkiyat Stratejisi**: Optimal sevkiyat planları
    - **🏷️ Fiyatlama & İndirim**: Akıllı fiyatlama ve indirim önerileri (✨ YENİ!)
    - **🚨 Kritik Uyarılar**: Acil aksiyon gerektiren durumlar
    - **⚙️ Ayarlar**: Segment parametrelerini özelleştir
    
    ### 🚀 Başlamak için:
    
    1. Sol menüden **"Veriyi Yükle ve Analiz Et"** butonuna tıklayın
    2. Sistem otomatik olarak analizleri çalıştıracak
    3. Menüden istediğiniz sayfaya gidin
    
    ### ⭐ Yeni Özellik: Akıllı Fiyatlama & İndirim
    
    **Segment bazlı fiyatlama stratejisi:**
    - 🔥 HOT/⭐ RISING_STAR → **Fiyat artır** (%10)
    - ✅ STEADY → **Değiştirme**
    - 🐢 SLOW → **Orta indirim** (%20-40)
    - 💀 DYING → **Agresif indirim** (%40-70)
    
    **Özellikler:**
    - 💰 Dinamik fiyat optimizasyonu
    - 🎮 Fiyat simülatörü
    - 💹 ROI & kar/zarar analizi
    - 📅 Zamanlama önerileri
    """)
    
    # Quick stats (eğer veri yüklüyse)
    if st.session_state.data_loaded:
        st.divider()
        st.markdown("### 📈 Hızlı Özet")
        
        df = st.session_state.df
        allocation_df = st.session_state.allocation_df
        alerts_df = st.session_state.alerts_df
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Toplam Ürün",
                format_number(len(df)),
                help="Sistemdeki toplam ürün sayısı"
            )
        
        with col2:
            hot_count = len(df[df['segment'] == 'HOT'])
            st.metric(
                "🔥 HOT Ürünler",
                hot_count,
                help="Hızlı satan ürünler"
            )
        
        with col3:
            critical_count = len(alerts_df[alerts_df['level'] == 'CRITICAL'])
            st.metric(
                "🔴 Kritik Uyarı",
                critical_count,
                delta=None if critical_count == 0 else f"-{critical_count}",
                delta_color="inverse",
                help="Acil aksiyon gerektiren uyarılar"
            )
        
        with col4:
            avg_stock_days = df['days_of_stock'].mean()
            st.metric(
                "Ortalama Stok Günü",
                f"{avg_stock_days:.0f}",
                delta=f"{avg_stock_days - 30:.0f} gün (hedef 30)",
                delta_color="inverse" if avg_stock_days > 30 else "normal",
                help="Mevcut stok kaç güne yeter"
            )
    
    # Info boxes
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **💡 İpucu:**  
        Sistem ürünleri satış hızına göre 5 segmente ayırır:
        - 🔥 HOT (Patlayanlar)
        - ⭐ RISING STAR (Yükselenler)
        - ✅ STEADY (Düzenli)
        - 🐢 SLOW (Yavaş)
        - 💀 DYING (Ölenler)
        """)
    
    with col2:
        st.success("""
        **🎯 Hedefler:**  
        - %30 e-com büyüme
        - HOT ürünlerde %95 servis seviyesi
        - 35 günlük ideal stok devri
        - Kontrollü %10 maksimum markdown
        """)

def show_dashboard_page():
    """Dashboard sayfası"""
    
    st.markdown("## 📊 Executive Dashboard")
    
    df = st.session_state.df
    allocation_df = st.session_state.allocation_df
    analytics = st.session_state.analytics
    viz = Visualizations()
    
    # KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Toplam Ürün",
            format_number(len(df))
        )
    
    with col2:
        total_value = (df['total_stock'] * df['price']).sum()
        st.metric(
            "Stok Değeri",
            format_currency(total_value)
        )
    
    with col3:
        daily_forecast = allocation_df['forecasted_daily_sales'].sum()
        st.metric(
            "Günlük Satış Tahmini",
            format_number(daily_forecast, 0)
        )
    
    with col4:
        hot_count = len(df[df['segment'] == 'HOT'])
        st.metric(
            "🔥 HOT Ürünler",
            hot_count
        )
    
    with col5:
        dying_count = len(df[df['segment'] == 'DYING'])
        st.metric(
            "💀 DYING Ürünler",
            dying_count,
            delta=f"-{dying_count}" if dying_count > 0 else None,
            delta_color="inverse"
        )
    
    st.divider()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📈 Genel Görünüm", "📊 Segment Analizi", "🏪 Depo Durumu"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(
                viz.segment_pie_chart(df),
                use_container_width=True
            )
        
        with col2:
            st.plotly_chart(
                viz.velocity_histogram(df),
                use_container_width=True
            )
        
        st.plotly_chart(
            viz.stock_health_scatter(df),
            use_container_width=True
        )
        
        st.plotly_chart(
            viz.category_performance_bar(df),
            use_container_width=True
        )
    
    with tab2:
        segment_summary = analytics.get_segment_summary()
        
        st.markdown("### Segment Performansı")
        st.dataframe(
            segment_summary.style.format({
                'total_stock': '{:,.0f}',
                'stock_value': '₺{:,.2f}',
                'avg_velocity': '{:.2f}',
                'avg_trend': '{:.2f}',
                'total_daily_sales': '{:.1f}',
                'avg_days_of_stock': '{:.1f}',
                'avg_final_score': '{:.0f}'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔥 Top 10 Performans")
            top_df = analytics.get_top_performers(10)
            st.dataframe(top_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 📉 Bottom 10 Performans")
            bottom_df = analytics.get_bottom_performers(10)
            st.dataframe(bottom_df, use_container_width=True, hide_index=True)
    
    with tab3:
        st.plotly_chart(
            viz.depot_stacked_bar(df),
            use_container_width=True
        )
        
        st.plotly_chart(
            viz.transfer_needs_bar(allocation_df),
            use_container_width=True
        )
        
        # Depo özeti
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "🏢 Akyazı Stok",
                format_number(df['stock_akyazi'].sum())
            )
        
        with col2:
            st.metric(
                "🏭 Ana Depo Stok",
                format_number(df['stock_ana_depo'].sum())
            )
        
        with col3:
            st.metric(
                "🏪 OMS Stok",
                format_number(df['stock_oms_total'].sum())
            )

def show_product_analysis_page():
    """Ürün analizi sayfası (placeholder)"""
    st.markdown("## 🔍 Ürün Analizi")
    st.info("Bu sayfa yakında eklenecek...")

def show_alerts_page():
    """Kritik uyarılar sayfası"""
    st.markdown("## 🚨 Kritik Uyarılar")
    
    alerts_df = st.session_state.alerts_df
    
    if len(alerts_df) == 0:
        st.success("✅ Kritik durum yok! Her şey güzel.")
        return
    
    # Alert özeti
    alert_summary = st.session_state.alert_mgr.get_alert_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Toplam Uyarı", alert_summary['total'])
    with col2:
        st.metric("🔴 CRITICAL", alert_summary['critical'])
    with col3:
        st.metric("🟡 WARNING", alert_summary['warning'])
    with col4:
        st.metric("🔵 INFO", alert_summary['info'])
    
    st.divider()
    
    # Alert listesi
    for idx, alert in alerts_df.head(20).iterrows():
        level_emoji = {'CRITICAL': '🔴', 'WARNING': '🟡', 'INFO': '🔵'}.get(alert['level'], '⚪')
        
        with st.expander(f"{level_emoji} {alert['product_name']} - {alert['message']}", expanded=(idx < 3)):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Ürün:** {alert['product_name']}")
                st.markdown(f"**SKU:** {alert['sku']}")
                st.markdown(f"**Segment:** {SEGMENT_EMOJI.get(alert['segment'], '❓')} {alert['segment']}")
                st.markdown(f"**Mesaj:** {alert['message']}")
                st.markdown(f"**👉 Aksiyon:** {alert['action']}")
            
            with col2:
                st.metric("Stok Günü", f"{alert['days_of_stock']:.1f}")
                st.metric("Günlük Satış", f"{alert['forecasted_sales']:.1f}")

if __name__ == "__main__":
    main()
