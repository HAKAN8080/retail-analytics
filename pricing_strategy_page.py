"""
Akıllı Fiyatlama & İndirim Öneri Sistemi
Dinamik Fiyat Optimizasyonu
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.helpers import (
    format_number, format_currency, format_percentage,
    show_success, show_error, show_info, show_warning
)
from utils.constants import SEGMENT_COLORS, SEGMENT_EMOJI

# Segment bazlı fiyatlama stratejisi
PRICING_STRATEGY = {
    'HOT': {
        'action': 'PRICE_INCREASE',
        'min_rate': 5,
        'max_rate': 15,
        'recommended_rate': 10,
        'emoji': '📈',
        'color': '#4CAF50',
        'description': 'Talep yüksek! Fiyat artırarak kar maksimize et',
        'elasticity': -0.5  # Fiyat artışına düşük hassasiyet
    },
    'RISING_STAR': {
        'action': 'PRICE_INCREASE',
        'min_rate': 5,
        'max_rate': 15,
        'recommended_rate': 10,
        'emoji': '📈',
        'color': '#4CAF50',
        'description': 'Momentum yakalamış! Fiyat artırma fırsatı',
        'elasticity': -0.6
    },
    'STEADY': {
        'action': 'NO_CHANGE',
        'min_rate': 0,
        'max_rate': 0,
        'recommended_rate': 0,
        'emoji': '➡️',
        'color': '#2196F3',
        'description': 'Dengede, mevcut fiyatı koru',
        'elasticity': -1.0
    },
    'SLOW': {
        'action': 'DISCOUNT',
        'min_rate': -20,
        'max_rate': -40,
        'recommended_rate': -30,
        'emoji': '📉',
        'color': '#FF9800',
        'description': 'Satışları hızlandır, orta indirim uygula',
        'elasticity': -1.5
    },
    'DYING': {
        'action': 'AGGRESSIVE_DISCOUNT',
        'min_rate': -40,
        'max_rate': -70,
        'recommended_rate': -50,
        'emoji': '🔥',
        'color': '#F44336',
        'description': 'Acil stok eritme! Agresif indirim gerekli',
        'elasticity': -2.0
    }
}


def show_pricing_strategy_page():
    """Ana fiyatlama stratejisi sayfası"""
    
    st.markdown("## 🏷️ Akıllı Fiyatlama & İndirim Sistemi")
    
    if not st.session_state.get('data_loaded'):
        st.warning("⚠️ Lütfen önce veriyi yükleyin!")
        return
    
    df = st.session_state.df
    allocation_df = st.session_state.allocation_df
    
    # Fiyatlama analizini hesapla
    pricing_df = calculate_pricing_recommendations(df, allocation_df)
    
    # Özet KPI'lar
    show_pricing_summary(pricing_df)
    
    st.divider()
    
    # Ana tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🎯 Akıllı Öneriler",
        "🎮 Fiyat Simülatörü",
        "📅 Zamanlama",
        "📦 Paket Önerileri",
        "💹 ROI Analizi",
        "📊 Segment Stratejileri"
    ])
    
    with tab1:
        show_smart_recommendations_tab(pricing_df, df)
    
    with tab2:
        show_price_simulator_tab(df, allocation_df)
    
    with tab3:
        show_timing_tab(pricing_df, df)
    
    with tab4:
        show_bundle_recommendations_tab(df)
    
    with tab5:
        show_roi_analysis_tab(pricing_df, df)
    
    with tab6:
        show_segment_strategies_tab(pricing_df)


def calculate_pricing_recommendations(df, allocation_df):
    """Her ürün için fiyatlama önerisi hesapla"""
    
    pricing_list = []
    
    for idx, row in df.iterrows():
        segment = row['segment']
        strategy = PRICING_STRATEGY.get(segment, PRICING_STRATEGY['STEADY'])
        
        current_price = row['price']
        margin_pct = row.get('margin_pct', 40) / 100
        
        # Önerilen fiyat değişimi
        recommended_rate = strategy['recommended_rate'] / 100
        new_price = current_price * (1 + recommended_rate)
        price_change = new_price - current_price
        
        # Satış artış tahmini (elasticity ile)
        elasticity = strategy['elasticity']
        sales_change_pct = elasticity * recommended_rate * -1  # Negatif çünkü ters ilişki
        
        current_daily_sales = row['daily_sales_avg_7d']
        forecasted_new_sales = current_daily_sales * (1 + sales_change_pct)
        
        # Gelir ve kar etkisi
        current_revenue_monthly = current_price * current_daily_sales * 30
        new_revenue_monthly = new_price * forecasted_new_sales * 30
        revenue_impact = new_revenue_monthly - current_revenue_monthly
        
        # Kar etkisi (basitleştirilmiş)
        current_profit_monthly = current_revenue_monthly * margin_pct
        new_profit_monthly = new_revenue_monthly * margin_pct
        profit_impact = new_profit_monthly - current_profit_monthly
        
        # Stok temizleme süresi
        current_stock = row['total_stock']
        days_to_clear_current = current_stock / (current_daily_sales + 0.1)
        days_to_clear_new = current_stock / (forecasted_new_sales + 0.1)
        
        # Aciliyet skoru (stok + segment)
        urgency_score = 0
        if segment == 'DYING':
            urgency_score = 100
        elif segment == 'SLOW':
            urgency_score = 70
        elif days_to_clear_current > 90:
            urgency_score = 80
        elif days_to_clear_current > 60:
            urgency_score = 50
        else:
            urgency_score = 20
        
        pricing_list.append({
            'sku': row['sku'],
            'product_name': row['product_name'],
            'category': row['category'],
            'segment': segment,
            'action': strategy['action'],
            'current_price': current_price,
            'recommended_price': round(new_price, 2),
            'price_change': round(price_change, 2),
            'price_change_pct': round(recommended_rate * 100, 1),
            'current_daily_sales': round(current_daily_sales, 2),
            'forecasted_new_sales': round(forecasted_new_sales, 2),
            'sales_increase_pct': round(sales_change_pct * 100, 1),
            'current_revenue_monthly': round(current_revenue_monthly, 2),
            'new_revenue_monthly': round(new_revenue_monthly, 2),
            'revenue_impact': round(revenue_impact, 2),
            'profit_impact': round(profit_impact, 2),
            'days_to_clear_current': round(days_to_clear_current, 1),
            'days_to_clear_new': round(days_to_clear_new, 1),
            'stock_clearance_improvement': round(days_to_clear_current - days_to_clear_new, 1),
            'urgency_score': urgency_score,
            'total_stock': current_stock,
            'margin_pct': row.get('margin_pct', 40)
        })
    
    return pd.DataFrame(pricing_list)


def show_pricing_summary(pricing_df):
    """Fiyatlama özeti KPI kartları"""
    
    st.markdown("### 📊 Fiyatlama Özeti")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Fiyat artırımı önerileri
    price_increase_count = len(pricing_df[pricing_df['action'] == 'PRICE_INCREASE'])
    
    # İndirim önerileri
    discount_count = len(pricing_df[pricing_df['action'].isin(['DISCOUNT', 'AGGRESSIVE_DISCOUNT'])])
    
    # Toplam potansiyel kar artışı
    total_profit_impact = pricing_df['profit_impact'].sum()
    
    # Ortalama önerilen değişim
    avg_change = pricing_df['price_change_pct'].mean()
    
    # Acil aksiyon gereken
    urgent_count = len(pricing_df[pricing_df['urgency_score'] >= 80])
    
    with col1:
        st.metric(
            "📈 Fiyat Artırımı",
            price_increase_count,
            delta=f"+₺{pricing_df[pricing_df['action'] == 'PRICE_INCREASE']['profit_impact'].sum():,.0f}",
            help="HOT ve RISING_STAR ürünler"
        )
    
    with col2:
        st.metric(
            "📉 İndirim Önerisi",
            discount_count,
            delta=f"₺{pricing_df[pricing_df['action'].isin(['DISCOUNT', 'AGGRESSIVE_DISCOUNT'])]['profit_impact'].sum():,.0f}",
            help="SLOW ve DYING ürünler"
        )
    
    with col3:
        st.metric(
            "💰 Potansiyel Kar (Aylık)",
            format_currency(total_profit_impact),
            help="Tüm öneriler uygulanırsa aylık kar artışı"
        )
    
    with col4:
        st.metric(
            "📊 Ort. Fiyat Değişimi",
            f"%{avg_change:.1f}",
            help="Önerilen ortalama fiyat değişim oranı"
        )
    
    with col5:
        st.metric(
            "🚨 Acil Aksiyon",
            urgent_count,
            delta=f"-{urgent_count}",
            delta_color="inverse",
            help="Urgency score >= 80"
        )


def show_smart_recommendations_tab(pricing_df, df):
    """Akıllı öneriler tab'ı"""
    
    st.markdown("### 🎯 Akıllı Fiyatlama Önerileri")
    
    # Sub-tabs: Artırım, İndirim, Acil
    subtab1, subtab2, subtab3 = st.tabs(["📈 Fiyat Artırımı", "📉 İndirim", "🚨 Acil Aksiyon"])
    
    # FIYAT ARTIRIMI
    with subtab1:
        st.success("""
        **📈 Fiyat Artırım Stratejisi:**
        - HOT ve RISING_STAR segmentlerinde
        - Talep yüksek, fiyat hassasiyeti düşük
        - Önerilen artış: %10
        - Kar maksimizasyonu fırsatı
        """)
        
        price_increase_df = pricing_df[pricing_df['action'] == 'PRICE_INCREASE'].copy()
        
        if len(price_increase_df) == 0:
            st.info("✅ Şu anda fiyat artırımı önerilen ürün yok")
        else:
            # Filtreleme
            col1, col2 = st.columns(2)
            
            with col1:
                segments = price_increase_df['segment'].unique().tolist()
                selected_segments = st.multiselect(
                    "Segment Filtrele:",
                    segments,
                    default=segments,
                    key='price_inc_seg'
                )
            
            with col2:
                min_profit = st.number_input(
                    "Min Kar Artışı (₺):",
                    min_value=0,
                    value=0,
                    key='min_profit_inc'
                )
            
            filtered = price_increase_df[
                (price_increase_df['segment'].isin(selected_segments)) &
                (price_increase_df['profit_impact'] >= min_profit)
            ]
            
            # Kar potansiyeline göre sırala
            filtered = filtered.sort_values('profit_impact', ascending=False)
            
            st.dataframe(
                filtered[[
                    'sku', 'product_name', 'segment',
                    'current_price', 'recommended_price', 'price_change_pct',
                    'sales_increase_pct', 'profit_impact'
                ]].style.format({
                    'current_price': '₺{:.2f}',
                    'recommended_price': '₺{:.2f}',
                    'price_change_pct': '%{:.1f}',
                    'sales_increase_pct': '%{:.1f}',
                    'profit_impact': '₺{:,.2f}'
                }),
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # Özet
            total_profit_gain = filtered['profit_impact'].sum()
            st.success(f"💰 **Toplam Kar Artışı Potansiyeli:** {format_currency(total_profit_gain)} / ay")
            
            # CSV Export
            csv = filtered.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "📥 Fiyat Artırım Listesini İndir",
                csv,
                "fiyat_artirim_onerileri.csv",
                "text/csv"
            )
    
    # İNDİRİM
    with subtab2:
        st.warning("""
        **📉 İndirim Stratejisi:**
        - SLOW: %20-40 orta indirim
        - DYING: %40-70 agresif indirim
        - Stok temizleme ve satış hızlandırma
        """)
        
        discount_df = pricing_df[
            pricing_df['action'].isin(['DISCOUNT', 'AGGRESSIVE_DISCOUNT'])
        ].copy()
        
        if len(discount_df) == 0:
            st.info("✅ Şu anda indirim önerilen ürün yok")
        else:
            # İndirim tipi seçimi
            col1, col2, col3 = st.columns(3)
            
            with col1:
                discount_type = st.multiselect(
                    "İndirim Tipi:",
                    ['DISCOUNT', 'AGGRESSIVE_DISCOUNT'],
                    default=['DISCOUNT', 'AGGRESSIVE_DISCOUNT'],
                    key='discount_type_filter'
                )
            
            with col2:
                min_stock_days = st.number_input(
                    "Min Stok Günü:",
                    min_value=0,
                    value=30,
                    key='min_stock_days'
                )
            
            with col3:
                urgency_filter = st.selectbox(
                    "Aciliyet:",
                    ['Tümü', 'Sadece Acil (>= 80)'],
                    key='urgency_filter'
                )
            
            # Filtreleme
            filtered = discount_df[discount_df['action'].isin(discount_type)]
            filtered = filtered[filtered['days_to_clear_current'] >= min_stock_days]
            
            if urgency_filter == 'Sadece Acil (>= 80)':
                filtered = filtered[filtered['urgency_score'] >= 80]
            
            # Aciliyet skoruna göre sırala
            filtered = filtered.sort_values('urgency_score', ascending=False)
            
            st.dataframe(
                filtered[[
                    'sku', 'product_name', 'segment',
                    'current_price', 'recommended_price', 'price_change_pct',
                    'days_to_clear_current', 'days_to_clear_new',
                    'stock_clearance_improvement', 'urgency_score'
                ]].style.format({
                    'current_price': '₺{:.2f}',
                    'recommended_price': '₺{:.2f}',
                    'price_change_pct': '%{:.1f}',
                    'days_to_clear_current': '{:.0f}',
                    'days_to_clear_new': '{:.0f}',
                    'stock_clearance_improvement': '{:.0f}',
                    'urgency_score': '{:.0f}'
                }),
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # Özet
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_clearance_improvement = filtered['stock_clearance_improvement'].mean()
                st.metric("Ort. Stok Temizleme İyileşmesi", f"{avg_clearance_improvement:.0f} gün")
            with col2:
                total_stock_value = (filtered['total_stock'] * filtered['current_price']).sum()
                st.metric("Toplam Stok Değeri", format_currency(total_stock_value))
            with col3:
                expected_loss = (filtered['total_stock'] * filtered['price_change'].abs()).sum()
                st.metric("Beklenen Gelir Kaybı", format_currency(expected_loss))
            
            # CSV Export
            csv = filtered.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "📥 İndirim Listesini İndir",
                csv,
                "indirim_onerileri.csv",
                "text/csv"
            )
    
    # ACİL AKSİYON
    with subtab3:
        st.error("""
        **🚨 Acil Aksiyon Gereken Ürünler:**
        - Urgency score >= 80
        - Çok yüksek stok günü veya DYING segment
        - Hemen harekete geç!
        """)
        
        urgent_df = pricing_df[pricing_df['urgency_score'] >= 80].sort_values(
            'urgency_score', ascending=False
        )
        
        if len(urgent_df) == 0:
            st.success("✅ Acil aksiyon gereken ürün yok!")
        else:
            st.error(f"⚠️ {len(urgent_df)} ürün için ACİL FİYATLAMA AKSİYONU gerekiyor!")
            
            st.dataframe(
                urgent_df[[
                    'sku', 'product_name', 'segment', 'action',
                    'current_price', 'recommended_price', 'price_change_pct',
                    'days_to_clear_current', 'urgency_score'
                ]].style.format({
                    'current_price': '₺{:.2f}',
                    'recommended_price': '₺{:.2f}',
                    'price_change_pct': '%{:.1f}',
                    'days_to_clear_current': '{:.0f}',
                    'urgency_score': '{:.0f}'
                }),
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # CSV Export
            csv = urgent_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                "📥 Acil Aksiyon Listesini İndir",
                csv,
                "acil_fiyatlama_listesi.csv",
                "text/csv"
            )


def show_price_simulator_tab(df, allocation_df):
    """Fiyat simülatörü"""
    
    st.markdown("### 🎮 Fiyat Simülatörü")
    
    st.info("""
    **Simülatör Nasıl Çalışır:**
    - Bir ürün seçin
    - Yeni fiyat belirleyin
    - Elasticity modeli ile satış tahmini yapılır
    - Gelir ve kar etkisi hesaplanır
    """)
    
    # Ürün seçimi
    col1, col2 = st.columns([2, 1])
    
    with col1:
        sku_list = df['sku'].tolist()
        product_names = df['product_name'].tolist()
        options = [f"{sku} - {name}" for sku, name in zip(sku_list, product_names)]
        
        selected_option = st.selectbox(
            "Ürün Seçin:",
            options,
            key='sim_product'
        )
        
        selected_sku = selected_option.split(' - ')[0]
        product_info = df[df['sku'] == selected_sku].iloc[0]
    
    with col2:
        st.write("")
        st.write("")
        st.caption(f"**Segment:** {SEGMENT_EMOJI.get(product_info['segment'], '❓')} {product_info['segment']}")
        st.caption(f"**Mevcut Fiyat:** ₺{product_info['price']:.2f}")
    
    # Fiyat değişimi girişi
    col1, col2, col3 = st.columns(3)
    
    with col1:
        price_change_type = st.radio(
            "Fiyat Değişimi:",
            ['Yüzde (%)', 'Tutarsal (₺)'],
            key='price_change_type'
        )
    
    with col2:
        if price_change_type == 'Yüzde (%)':
            price_change_value = st.number_input(
                "Değişim Yüzdesi:",
                min_value=-70.0,
                max_value=50.0,
                value=PRICING_STRATEGY[product_info['segment']]['recommended_rate'],
                step=5.0,
                key='price_change_pct'
            )
            new_price = product_info['price'] * (1 + price_change_value / 100)
        else:
            price_change_value = st.number_input(
                "Değişim Tutarı (₺):",
                min_value=-product_info['price'] * 0.7,
                max_value=product_info['price'] * 0.5,
                value=0.0,
                step=1.0,
                key='price_change_amount'
            )
            new_price = product_info['price'] + price_change_value
    
    with col3:
        st.metric("Yeni Fiyat", f"₺{new_price:.2f}")
    
    # Simülasyon butonu
    if st.button("🎮 Simülasyonu Çalıştır", use_container_width=True, type="primary"):
        # Elasticity
        elasticity = PRICING_STRATEGY[product_info['segment']]['elasticity']
        
        price_change_pct = (new_price - product_info['price']) / product_info['price']
        sales_change_pct = elasticity * price_change_pct * -1
        
        current_daily_sales = product_info['daily_sales_avg_7d']
        new_daily_sales = current_daily_sales * (1 + sales_change_pct)
        
        # Gelir ve kar
        margin_pct = product_info.get('margin_pct', 40) / 100
        
        current_revenue_monthly = product_info['price'] * current_daily_sales * 30
        new_revenue_monthly = new_price * new_daily_sales * 30
        
        current_profit_monthly = current_revenue_monthly * margin_pct
        new_profit_monthly = new_revenue_monthly * margin_pct
        
        # Stok temizleme
        current_stock = product_info['total_stock']
        days_to_clear_current = current_stock / (current_daily_sales + 0.1)
        days_to_clear_new = current_stock / (new_daily_sales + 0.1)
        
        # Sonuçları göster
        st.success("✅ Simülasyon tamamlandı!")
        
        st.divider()
        
        # Karşılaştırma
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Mevcut Durum")
            st.metric("Fiyat", f"₺{product_info['price']:.2f}")
            st.metric("Günlük Satış", f"{current_daily_sales:.2f} adet")
            st.metric("Aylık Gelir", format_currency(current_revenue_monthly))
            st.metric("Aylık Kar", format_currency(current_profit_monthly))
            st.metric("Stok Temizleme", f"{days_to_clear_current:.0f} gün")
        
        with col2:
            st.markdown("#### 📊 Simülasyon Sonucu")
            st.metric(
                "Fiyat",
                f"₺{new_price:.2f}",
                delta=f"₺{new_price - product_info['price']:.2f}"
            )
            st.metric(
                "Günlük Satış",
                f"{new_daily_sales:.2f} adet",
                delta=f"{sales_change_pct * 100:+.1f}%"
            )
            st.metric(
                "Aylık Gelir",
                format_currency(new_revenue_monthly),
                delta=format_currency(new_revenue_monthly - current_revenue_monthly)
            )
            st.metric(
                "Aylık Kar",
                format_currency(new_profit_monthly),
                delta=format_currency(new_profit_monthly - current_profit_monthly)
            )
            st.metric(
                "Stok Temizleme",
                f"{days_to_clear_new:.0f} gün",
                delta=f"{days_to_clear_new - days_to_clear_current:+.0f} gün"
            )
        
        # Öneriler
        st.divider()
        
        if new_profit_monthly > current_profit_monthly:
            st.success(f"✅ **Kar artışı:** {format_currency(new_profit_monthly - current_profit_monthly)} / ay")
        elif new_profit_monthly < current_profit_monthly:
            st.error(f"⚠️ **Kar kaybı:** {format_currency(current_profit_monthly - new_profit_monthly)} / ay")
        else:
            st.info("➡️ **Kar değişmedi**")


def show_timing_tab(pricing_df, df):
    """Zamanlama önerileri"""
    
    st.markdown("### 📅 Fiyatlama Zamanlaması")
    
    st.info("""
    **Zamanlama Stratejisi:**
    - Acil ürünler → Hemen başlat
    - Orta öncelik → 1-2 hafta içinde
    - Düşük öncelik → Ay sonuna planla
    """)
    
    # Aciliyet bazlı gruplama
    immediate = pricing_df[pricing_df['urgency_score'] >= 80]
    soon = pricing_df[(pricing_df['urgency_score'] >= 50) & (pricing_df['urgency_score'] < 80)]
    planned = pricing_df[pricing_df['urgency_score'] < 50]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.error(f"**🚨 Hemen ({len(immediate)})**")
        st.caption("Urgency >= 80")
        if len(immediate) > 0:
            for _, row in immediate.head(5).iterrows():
                st.write(f"• {row['product_name'][:30]}")
    
    with col2:
        st.warning(f"**⚠️ Yakında ({len(soon)})**")
        st.caption("Urgency 50-79")
        if len(soon) > 0:
            for _, row in soon.head(5).iterrows():
                st.write(f"• {row['product_name'][:30]}")
    
    with col3:
        st.info(f"**📋 Planlı ({len(planned)})**")
        st.caption("Urgency < 50")
        if len(planned) > 0:
            for _, row in planned.head(5).iterrows():
                st.write(f"• {row['product_name'][:30]}")


def show_bundle_recommendations_tab(df):
    """Paket önerileri"""
    
    st.markdown("### 📦 Paket İndirim Önerileri")
    
    st.warning("🚧 Bu özellik yakında eklenecek!")
    
    st.info("""
    **Planlanan Özellikler:**
    - Aynı kategoriden paket önerileri
    - Cross-sell fırsatları
    - 2+1, 3+1 kampanya önerileri
    - Bundle kar analizi
    """)


def show_roi_analysis_tab(pricing_df, df):
    """ROI analizi"""
    
    st.markdown("### 💹 ROI & Kar/Zarar Analizi")
    
    # Genel özet
    total_profit_impact = pricing_df['profit_impact'].sum()
    total_revenue_impact = pricing_df['revenue_impact'].sum()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "💰 Toplam Kar Etkisi (Aylık)",
            format_currency(total_profit_impact),
            help="Tüm öneriler uygulanırsa aylık kar artışı"
        )
    
    with col2:
        st.metric(
            "📊 Toplam Gelir Etkisi (Aylık)",
            format_currency(total_revenue_impact),
            help="Tüm öneriler uygulanırsa aylık gelir değişimi"
        )
    
    # Segment bazlı kar analizi
    st.divider()
    
    segment_roi = pricing_df.groupby('segment').agg({
        'profit_impact': 'sum',
        'revenue_impact': 'sum',
        'sku': 'count'
    }).reset_index()
    
    segment_roi.columns = ['Segment', 'Kar Etkisi', 'Gelir Etkisi', 'Ürün Sayısı']
    
    st.markdown("### 📊 Segment Bazlı ROI")
    
    st.dataframe(
        segment_roi.style.format({
            'Kar Etkisi': '₺{:,.2f}',
            'Gelir Etkisi': '₺{:,.2f}',
            'Ürün Sayısı': '{:.0f}'
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # Grafik
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=segment_roi['Segment'],
        y=segment_roi['Kar Etkisi'],
        name='Kar Etkisi',
        marker_color='#4CAF50'
    ))
    
    fig.update_layout(
        title='Segment Bazlı Kar Etkisi',
        xaxis_title='Segment',
        yaxis_title='Aylık Kar Etkisi (₺)',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_segment_strategies_tab(pricing_df):
    """Segment stratejileri genel bakış"""
    
    st.markdown("### 📊 Segment Bazlı Fiyatlama Stratejileri")
    
    for segment, strategy in PRICING_STRATEGY.items():
        with st.expander(f"{SEGMENT_EMOJI.get(segment, '❓')} {segment} - {strategy['description']}", expanded=(segment in ['HOT', 'DYING'])):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Aksiyon:** {strategy['emoji']} {strategy['action']}")
                st.markdown(f"**Önerilen Oran:** {strategy['recommended_rate']:+}%")
                st.markdown(f"**Oran Aralığı:** {strategy['min_rate']:+}% - {strategy['max_rate']:+}%")
                st.markdown(f"**Elasticity:** {strategy['elasticity']}")
                
                # Segment verileri
                segment_data = pricing_df[pricing_df['segment'] == segment]
                
                if len(segment_data) > 0:
                    st.markdown(f"**Ürün Sayısı:** {len(segment_data)}")
                    st.markdown(f"**Toplam Kar Etkisi:** {format_currency(segment_data['profit_impact'].sum())} / ay")
            
            with col2:
                # Strateji göstergesi
                if strategy['action'] == 'PRICE_INCREASE':
                    st.success("📈 Fiyat Artır")
                elif strategy['action'] == 'NO_CHANGE':
                    st.info("➡️ Değiştirme")
                elif strategy['action'] == 'DISCOUNT':
                    st.warning("📉 İndirim")
                elif strategy['action'] == 'AGGRESSIVE_DISCOUNT':
                    st.error("🔥 Agresif İndirim")
