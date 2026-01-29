"""
Ulusal Akıllı Su ve Sulama İstihbarat Platformu
National Smart Water & Irrigation Intelligence Platform
Premium SaaS Platform for Farmers, Municipalities, and Policy Makers
"""
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from pathlib import Path
from typing import Dict, List
import geopandas as gpd
import numpy as np
from branca.colormap import LinearColormap
from components import (
    render_metric_card,
    render_insight_box,
    render_status_badge,
    render_section_header,
    get_user_type_config,
    format_water_amount,
    get_irrigation_recommendation_text,
    render_ai_decision_engine,
    render_impact_story,
    render_decision_confidence_indicator,
    render_regional_intelligence_layer,
    render_platform_header,
    render_section_divider,
    render_key_metrics_bar,
    render_drought_risk_card,
    render_water_basin_card,
)
from utils import (
    fetch_weather_data,
    calculate_et0,
    calculate_water_need,
    analyze_hourly_irrigation,
    get_confidence_level,
    format_time,
    generate_ai_irrigation_strategy,
    calculate_decision_confidence,
    get_regional_intelligence,
    enhance_ai_strategy_with_regional_data,
    get_regional_risk_assessment,
    get_drought_risk_from_geojson,
    get_watershed_for_location,
)

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Ulusal Su İstihbarat Platformu | SinerjiX",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== PREMIUM STYLING ====================
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Root Variables - Premium Color Palette */
    :root {
        --primary-color: #059669;
        --primary-light: #10B981;
        --primary-dark: #047857;
        --secondary-color: #0EA5E9;
        --secondary-dark: #0284C7;
        --accent-color: #8B5CF6;
        --success-color: #10B981;
        --warning-color: #F59E0B;
        --danger-color: #EF4444;
        --info-color: #06B6D4;
        --text-primary: #0F172A;
        --text-secondary: #475569;
        --text-muted: #94A3B8;
        --bg-primary: #FFFFFF;
        --bg-secondary: #F8FAFC;
        --bg-tertiary: #F1F5F9;
        --border-color: #E2E8F0;
        --border-light: #F1F5F9;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        --radius-sm: 8px;
        --radius: 12px;
        --radius-lg: 16px;
        --radius-xl: 24px;
    }
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        letter-spacing: -0.01em;
    }
    
    .main {
        background: linear-gradient(180deg, #F0FDF4 0%, #F8FAFC 30%, #FFFFFF 100%);
        padding: 0;
    }
    
    .block-container {
        padding: 1rem 2rem 3rem 2rem;
        max-width: 1400px;
        margin-left: 0 !important;
    }
    
    /* Ensure main content doesn't overlap sidebar */
    .main .block-container {
        margin-left: 0 !important;
    }
    
    /* Fix main content area when sidebar is visible */
    [data-testid="stAppViewContainer"] {
        margin-left: 0 !important;
    }
    
    /* Ensure sidebar space is reserved */
    [data-testid="stAppViewContainer"] > div:first-child {
        margin-left: 0 !important;
    }
    
    /* Premium Typography */
    h1 {
        font-weight: 800;
        letter-spacing: -0.03em;
        line-height: 1.1;
        color: var(--text-primary);
    }
    
    h2 {
        font-weight: 700;
        letter-spacing: -0.02em;
        line-height: 1.2;
        color: var(--text-primary);
    }
    
    h3 {
        font-weight: 600;
        letter-spacing: -0.015em;
        line-height: 1.3;
        color: var(--text-primary);
    }
    
    p {
        line-height: 1.7;
        color: var(--text-secondary);
    }
    
    /* Section Spacing */
    .section-spacer {
        margin-top: 3rem;
        margin-bottom: 1.5rem;
    }
    
    .section-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, var(--border-color) 20%, var(--border-color) 80%, transparent 100%);
        margin: 3rem 0;
    }
    
    /* Sidebar Styling - Premium Dark Theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%) !important;
        border-right: none !important;
        min-width: 320px !important;
        width: 320px !important;
        max-width: 360px !important;
    }
    
    /* Ensure sidebar is visible and properly sized */
    [data-testid="stSidebar"] > div:first-child {
        width: 320px !important;
        min-width: 320px !important;
    }
    
    /* Fix sidebar content width */
    [data-testid="stSidebar"] .css-1d391kg {
        width: 320px !important;
        min-width: 320px !important;
    }
    
    /* Ensure sidebar doesn't collapse */
    [data-testid="stSidebar"][aria-expanded="true"] {
        width: 320px !important;
        min-width: 320px !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #F1F5F9 !important;
    }
    
    [data-testid="stSidebar"] .sidebar-content {
        padding: 1.5rem !important;
        width: 100% !important;
    }
    
    /* Force sidebar to be visible and properly sized */
    [data-testid="stSidebar"] {
        display: block !important;
        visibility: visible !important;
        opacity: 1 !important;
        transform: translateX(0) !important;
        position: relative !important;
        z-index: 999 !important;
    }
    
    /* Sidebar inner container */
    [data-testid="stSidebar"] > div {
        width: 320px !important;
        min-width: 320px !important;
        max-width: 360px !important;
        display: block !important;
    }
    
    /* Sidebar viewport */
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"][aria-expanded="true"] {
        width: 320px !important;
        min-width: 320px !important;
        max-width: 360px !important;
        display: block !important;
        visibility: visible !important;
    }
    
    /* Ensure sidebar content is visible */
    [data-testid="stSidebar"] [class*="css-"] {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    /* Fix sidebar collapse button if it exists */
    [data-testid="stSidebar"] button[aria-label*="Close"],
    [data-testid="stSidebar"] button[aria-label*="close"] {
        display: none !important;
    }
    
    /* Logo styling – tooltip SVG aşağıda override ediliyor */
    [data-testid="stSidebar"] svg {
        width: 120px !important;
        height: 120px !important;
        max-width: 100%;
        display: block;
        margin: 0 auto 1rem auto;
        filter: brightness(1.1);
    }
    
    /* Ayrım: çizgi (kutu değil) */
    .sidebar-section {
        margin-bottom: 0;
        padding: 0.75rem 0 1rem 0;
        background: transparent;
        border: none;
        border-bottom: 1px solid rgba(255, 255, 255, 0.12);
    }
    
    .sidebar-section:last-of-type {
        border-bottom: none;
    }
    
    .sidebar-section-title {
        font-size: 0.7rem;
        font-weight: 700;
        color: #94A3B8 !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.5rem;
    }
    
    /* Premium Metric Cards */
    .metric-card {
        background: var(--bg-primary);
        border-radius: var(--radius-lg);
        padding: 1.75rem;
        box-shadow: var(--shadow-md);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid var(--border-light);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl);
    }
    
    .metric-card:hover::before {
        opacity: 1;
    }
    
    .metric-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .metric-icon {
        font-size: 1.75rem;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
    }
    
    .metric-label {
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .metric-value {
        font-size: 2.25rem;
        font-weight: 800;
        color: var(--text-primary);
        line-height: 1.1;
        letter-spacing: -0.02em;
    }
    
    .metric-subtitle {
        font-size: 0.8125rem;
        color: var(--text-muted);
        margin-top: 0.5rem;
    }
    
    /* Premium Section Headers */
    .section-header {
        margin-bottom: 2rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--border-color);
        position: relative;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 80px;
        height: 2px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    }
    
    .section-title {
        font-size: 1.875rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .section-subtitle {
        font-size: 1rem;
        color: var(--text-secondary);
        margin-top: 0.5rem;
        margin-bottom: 0;
    }
    
    /* Premium Insight Boxes */
    .insight-box {
        background: var(--bg-primary);
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-sm);
        border-left: 4px solid;
        position: relative;
    }
    
    .insight-info { 
        border-left-color: var(--info-color); 
        background: linear-gradient(90deg, #ECFEFF 0%, var(--bg-primary) 15%);
    }
    .insight-success { 
        border-left-color: var(--success-color); 
        background: linear-gradient(90deg, #ECFDF5 0%, var(--bg-primary) 15%);
    }
    .insight-warning { 
        border-left-color: var(--warning-color); 
        background: linear-gradient(90deg, #FFFBEB 0%, var(--bg-primary) 15%);
    }
    .insight-danger { 
        border-left-color: var(--danger-color); 
        background: linear-gradient(90deg, #FEF2F2 0%, var(--bg-primary) 15%);
    }
    
    .insight-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
    }
    
    .insight-icon {
        font-size: 1.5rem;
    }
    
    .insight-title {
        font-size: 1.125rem;
        font-weight: 700;
        color: var(--text-primary);
    }
    
    .insight-message {
        font-size: 0.9375rem;
        color: var(--text-secondary);
        line-height: 1.7;
    }
    
    /* Premium Status Badges */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        padding: 0.375rem 0.875rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .badge-success {
        background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
        color: #065F46;
        border: 1px solid #6EE7B7;
    }
    
    .badge-warning {
        background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
        color: #92400E;
        border: 1px solid #FCD34D;
    }
    
    .badge-danger {
        background: linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%);
        color: #991B1B;
        border: 1px solid #FCA5A5;
    }
    
    .badge-info {
        background: linear-gradient(135deg, #CFFAFE 0%, #A5F3FC 100%);
        color: #164E63;
        border: 1px solid #67E8F9;
    }
    
    .badge-neutral {
        background: linear-gradient(135deg, #F1F5F9 0%, #E2E8F0 100%);
        color: #475569;
        border: 1px solid #CBD5E1;
    }
    
    /* Premium Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        border-radius: var(--radius);
        padding: 0.875rem 2rem;
        font-weight: 700;
        font-size: 0.9375rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 14px 0 rgba(5, 150, 105, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px 0 rgba(5, 150, 105, 0.5);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Meteoroloji ve Su İhtiyacı Verilerini Getir — buton metni beyaz */
    .stButton > button,
    .stButton > button *,
    .stButton > button p,
    .stButton > button span {
        color: white !important;
    }
    
    /* Radio Button Styling */
    [data-testid="stRadio"] {
        margin-bottom: 0.5rem;
    }
    
    [data-testid="stRadio"] label {
        padding: 0.75rem 1rem;
        border-radius: var(--radius);
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
        font-size: 0.9375rem;
        font-weight: 500;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="stRadio"] label:hover {
        background: rgba(255, 255, 255, 0.1);
    }
    
    /* Number Input Styling */
    [data-testid="stNumberInput"] {
        margin-bottom: 1rem;
    }
    
    [data-testid="stNumberInput"] label {
        font-weight: 600;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
    }
    
    [data-testid="stNumberInput"] input {
        font-size: 0.9rem;
        padding: 0.625rem 0.75rem;
        border-radius: 8px;
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        color: #0F172A !important;
    }
    
    /* Text Input Styling */
    [data-testid="stTextInput"] input {
        font-size: 0.9rem;
        padding: 0.625rem 0.75rem;
        border-radius: 8px;
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        color: #0F172A !important;
    }
    
    [data-testid="stTextInput"] label {
        font-weight: 600;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
    }
    
    /* Selectbox Styling */
    [data-testid="stSelectbox"] {
        margin-bottom: 1rem;
    }
    
    [data-testid="stSelectbox"] label {
        font-weight: 600;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
    }
    
    [data-testid="stSelectbox"] > div > div {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px;
    }
    
    [data-testid="stSelectbox"] > div > div > div {
        color: #0F172A !important;
    }
    
    /* Yardım ikonu – küçük, beyaz */
    [data-testid="stSidebar"] .stTooltipIcon,
    [data-testid="stSidebar"] [data-testid="stTooltipIcon"] {
        width: 16px !important;
        height: 16px !important;
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stTooltipIcon"] svg {
        width: 14px !important;
        height: 14px !important;
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }
    
    /* Sidebar input overrides – beyaz kutu, okunaklı yazı */
    [data-testid="stSidebar"] input {
        background: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #E2E8F0 !important;
    }
    
    [data-testid="stSidebar"] input::placeholder {
        color: #64748B !important;
    }
    
    /* Bahçende ne yetiştiriyorsun / Selectbox – beyaz kutu, okunaklı */
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px;
        color: #0F172A !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div div,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div span,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div p {
        color: #0F172A !important;
    }
    
    /* Premium Data Tables */
    .dataframe {
        border-radius: var(--radius-lg) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    /* Map Container */
    .folium-container {
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--border-color);
    }
    
    /* Hero Gradient Backgrounds */
    .hero-gradient-green {
        background: linear-gradient(135deg, #059669 0%, #047857 50%, #065F46 100%);
    }
    
    .hero-gradient-blue {
        background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 50%, #0369A1 100%);
    }
    
    .hero-gradient-purple {
        background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 50%, #6D28D9 100%);
    }
    
    /* Glassmorphism Effects */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: var(--radius-lg);
    }
    
    /* Animation Keyframes */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    .animate-fadeInUp {
        animation: fadeInUp 0.5s ease-out forwards;
    }
    
    .animate-pulse {
        animation: pulse 2s ease-in-out infinite;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-tertiary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    # Brand - Logo
    try:
        with open("assets/logo3.svg", "r", encoding="utf-8") as f:
            logo_svg = f.read()
        st.markdown(logo_svg, unsafe_allow_html=True)
    except:
        st.markdown("# 🌍 SinerjiX")
    
    # Platform Title
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.1);">
        <p style="font-size: 0.75rem; color: #94A3B8 !important; text-transform: uppercase; letter-spacing: 0.1em; margin: 0;">
            Ulusal Akıllı Su Platformu
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Platform Mode Selector
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">Platform Modu</div>', unsafe_allow_html=True)
    
    platform_mode = st.radio(
        "Platform Modu",
        [
            "👩‍🌾 Bireysel / Çiftçi Modu",
            "🏛 Kamu / Belediye Modu"
        ],
        label_visibility="collapsed",
        key="platform_mode"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Farmer Mode Settings
    if platform_mode == "👩‍🌾 Bireysel / Çiftçi Modu":
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-section-title">Kullanıcı Profili</div>', unsafe_allow_html=True)
        
        user_type = st.radio(
            "Kullanım Türü",
            [
                "🪴 Ev Bahçesi",
                "🌱 Küçük Ölçekli Üretim",
                "🚜 Ticari Tarım",
                "🏭 Büyük Tarım Alanı"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        config = get_user_type_config(user_type)
        
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-section-title">Alan Bilgileri</div>', unsafe_allow_html=True)
        
        area = st.number_input(
            config["area_label"],
            value=config["area_default"],
            min_value=1.0,
            step=10.0,
            help=config["area_help"]
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown(f'<div class="sidebar-section-title">{config["plant_label"]}</div>', unsafe_allow_html=True)
        
        plant = st.selectbox(
            "Bitki Türü",
            config["plants"],
            label_visibility="collapsed"
        )
        
        kc = config["kc_map"][plant]
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Public Mode Settings: Model seçimi
    else:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-section-title">Model Seçimi</div>', unsafe_allow_html=True)
        
        public_model_choice = st.radio(
            "İnceleme",
            [
                "🌾 Model 1: Tarımsal Su Stresi",
                "🏙️ Model 2: Kentsel Su Stresi",
                "🌿 Model 3: Ekosistem Su Direnci",
            ],
            label_visibility="collapsed",
            key="public_model_choice",
        )
        public_selected_model = (
            1 if "Model 1" in public_model_choice else
            2 if "Model 2" in public_model_choice else
            3
        )
        st.session_state.public_selected_model = public_selected_model
    
    # Footer (üstten boşluk: Model seçimine yapışmasın)
    st.markdown("""
    <div style="position: absolute; bottom: 1rem; left: 1.5rem; right: 1.5rem; text-align: center; padding-top: 1.5rem;">
        <p style="font-size: 0.6875rem; color: #64748B !important; margin: 0;">
            SinerjiX © 2026 | v2.0
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==================== MAIN CONTENT ====================

# Platform Header
render_platform_header(platform_mode)

# Impact Story - Hero Section
render_impact_story(platform_mode)

# ==================== FARMER MODE CONTENT ====================
if platform_mode == "👩‍🌾 Bireysel / Çiftçi Modu":
    
    render_section_divider()
    render_section_header(
        "📍 Konum Seçimi",
        "Sulama analizi için alan konumunu haritadan seçin",
        step_number=1,
        step_title="DURUM"
    )
    
    DEFAULT_LAT = 37.8746
    DEFAULT_LON = 32.4932
    
    m = folium.Map(
        location=[DEFAULT_LAT, DEFAULT_LON],
        zoom_start=9,
        tiles='OpenStreetMap'
    )
    
    map_data = st_folium(m, height=400, width=None)
    
    lat, lon = DEFAULT_LAT, DEFAULT_LON
    
    if map_data and map_data.get("last_clicked"):
        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%); 
                padding: 1rem 1.5rem; border-radius: 12px; margin: 1rem 0;
                border: 1px solid #A7F3D0;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <span style="font-size: 1.5rem;">📍</span>
            <div>
                <div style="font-weight: 600; color: #065F46;">Seçilen Konum</div>
                <div style="color: #047857; font-size: 0.9375rem;">{lat:.4f}, {lon:.4f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Fetch Data Button
    if st.button("🌦 Meteoroloji ve Su İhtiyacı Verilerini Getir", use_container_width=True, type="primary", key="farmer_fetch_weather"):
        with st.spinner("Veriler alınıyor..."):
            weather, forecast = fetch_weather_data(lat, lon)
            
            if weather and forecast:
                temp = weather["main"]["temp"]
                humidity = weather["main"]["humidity"]
                wind = weather["wind"]["speed"]
                city = weather["name"]
                
                et0 = calculate_et0(temp, humidity, wind)
                water_need = calculate_water_need(et0, area, kc)
                
                st.session_state.weather_data = {
                    "temp": temp,
                    "humidity": humidity,
                    "wind": wind,
                    "city": city,
                    "et0": et0,
                    "water_need": water_need,
                    "forecast": forecast,
                    "lat": lat,
                    "lon": lon
                }
                
                st.success("Veriler alındı.")
                st.rerun()
            else:
                st.error("Veriler alınamadı. Lütfen tekrar deneyin.")
    
    # Display Data if Available
    if "weather_data" in st.session_state:
        data = st.session_state.weather_data
        lat = data.get("lat", DEFAULT_LAT)
        lon = data.get("lon", DEFAULT_LON)
        
        df, best_hour, best_score, rain_expected = analyze_hourly_irrigation(data['forecast'])
        
        drought = get_drought_risk_from_geojson(lat, lon)
        geojson_category = drought["drought_category"] if drought.get("data_available") else None
        
        basin = get_watershed_for_location(lat, lon)
        basin_water_stressed = bool(
            basin.get("data_available") and basin.get("water_stress_label") == "Yüksek"
        )
        
        strategy_data = generate_ai_irrigation_strategy(
            platform_mode=platform_mode,
            et0=data['et0'],
            water_need=data['water_need'],
            area=area,
            humidity=data['humidity'],
            temp=data['temp'],
            wind=data['wind'],
            rain_expected=rain_expected,
            user_type=user_type,
            geojson_drought_category=geojson_category,
            basin_water_stressed=basin_water_stressed,
        )
        
        render_key_metrics_bar(
            temp=data['temp'],
            humidity=data['humidity'],
            wind=data['wind'],
            water_need=data['water_need'],
            et0=data['et0'],
            city=data['city'],
            user_type=user_type,
            platform_mode=platform_mode
        )
        
        dc1, dc2 = st.columns([1, 1])
        with dc1:
            render_drought_risk_card(drought)
        with dc2:
            render_water_basin_card(basin)
        
        render_section_divider()
        render_section_header(
            "📊 Veri Analizi",
            "Saatlik meteoroloji ve sulama uygunluk analizi",
            step_number=2,
            step_title="ANALİZ"
        )
        
        # Analysis content in columns
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 📈 Saatlik Tahmin Verileri")
            styled_df = df.copy()
            styled_df["Sıcaklık (°C)"] = styled_df["Sıcaklık (°C)"].apply(lambda x: f"{x:.1f}")
            styled_df["Nem (%)"] = styled_df["Nem (%)"].apply(lambda x: f"{x:.0f}")
            styled_df["Rüzgar (m/s)"] = styled_df["Rüzgar (m/s)"].apply(lambda x: f"{x:.1f}")
            styled_df["Uygunluk Skoru"] = styled_df["Uygunluk Skoru"].apply(lambda x: f"{x:.2f}")
            
            st.dataframe(styled_df, use_container_width=True, height=300)
        
        with col2:
            st.markdown("#### 📉 Meteorolojik Trend")
            chart_data = df.set_index("Saat")[["Sıcaklık (°C)", "Nem (%)", "Rüzgar (m/s)"]]
            st.line_chart(chart_data, height=300)
        
        # Regional Intelligence Layer
        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
        regional_intelligence = get_regional_intelligence(
            lat=data.get('lat', DEFAULT_LAT),
            lon=data.get('lon', DEFAULT_LON),
            region_name=data.get('city', '')
        )
        regional_intelligence["watershed"] = basin
        
        risk_assessment = get_regional_risk_assessment(
            lat=data.get('lat', DEFAULT_LAT),
            lon=data.get('lon', DEFAULT_LON),
            et0=data['et0'],
            regional_intelligence=regional_intelligence
        )
        
        render_regional_intelligence_layer(
            regional_intelligence=regional_intelligence,
            risk_assessment=risk_assessment,
            platform_mode=platform_mode
        )
        
        # Enhance strategy with regional data
        strategy_data = enhance_ai_strategy_with_regional_data(
            base_strategy=strategy_data,
            regional_intelligence=regional_intelligence
        )
        
        render_section_divider()
        render_section_header(
            "🎯 Stratejik Karar Desteği",
            "Veri odaklı sulama önerileri ve politika danışmanlığı",
            step_number=3,
            step_title="ÖNERİ"
        )
        
        # Decision Confidence
        confidence_score = calculate_decision_confidence(
            et0=data['et0'],
            forecast_count=len(df),
            strategy_type=strategy_data.get("strategy_type", "recommended"),
            rain_expected=rain_expected,
            weather_risk=strategy_data.get("weather_risk", "low")
        )
        
        render_decision_confidence_indicator(
            confidence_score=confidence_score,
            et0=data['et0'],
            forecast_count=len(df),
            strategy_type=strategy_data.get("strategy_type", "recommended")
        )
        
        # AI Decision Engine (ana karar en üstte, detaylar expander'da)
        render_ai_decision_engine(strategy_data)
        
        # Sulama önerildiyse "Sulamayı Başlat" butonu
        if strategy_data.get("strategy_type") != "water_saving":
            if st.button("🚿 Sulamayı Başlat", use_container_width=True, type="primary"):
                st.session_state.show_water_animation = True
                st.success("Sulama simülasyonu başlatıldı.")
        
        render_section_divider()
    else:
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%); 
                    border-radius: 20px; box-shadow: 0 10px 40px -10px rgba(0, 0, 0, 0.08); margin: 2rem 0;
                    border: 1px solid #E2E8F0;">
            <div style="font-size: 4rem; margin-bottom: 1.25rem;">🌱</div>
            <h2 style="color: #0F172A; margin-bottom: 0.75rem; font-size: 1.75rem; font-weight: 800;">Konum Seçin</h2>
            <p style="color: #64748B; font-size: 1rem; line-height: 1.7; max-width: 560px; margin: 0 auto 1.5rem auto;">
                Sulama analizi için haritadan konum seçin ve <strong>Meteoroloji ve Su İhtiyacı Verilerini Getir</strong> ile verileri yükleyin.
            </p>
            <div style="display: inline-flex; align-items: center; gap: 0.5rem; background: #ECFDF5; 
                        padding: 0.6rem 1.25rem; border-radius: 8px; color: #065F46; font-weight: 600; font-size: 0.9rem;">
                <span>📍</span>
                <span>Haritada bir noktaya tıklayarak konum seçin</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ==================== PUBLIC MODE CONTENT ====================
else:
    # Yeni Su Stresi İstihbarat Modelleri Dashboard'u
    try:
        # Yeni dashboard'un fonksiyonlarını import et
        import sys
        import importlib.util
        water_stress_path = Path(__file__).parent / "water_stress_helpers.py"
        if water_stress_path.exists():
            spec = importlib.util.spec_from_file_location("water_stress_helpers", water_stress_path)
            water_stress = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(water_stress)
            
            # Fonksiyonları al
            load_model1_results = water_stress.load_model1_results
            load_model2_results = water_stress.load_model2_results
            load_model3_results = water_stress.load_model3_results
            make_water_stress_map = water_stress.make_water_stress_map
            make_urban_water_stress_map = water_stress.make_urban_water_stress_map
            make_ecosystem_resilience_map = water_stress.make_ecosystem_resilience_map
            _compute_automated_insights = water_stress._compute_automated_insights
            _compute_urban_insights = water_stress._compute_urban_insights
            _compute_ecosystem_insights = water_stress._compute_ecosystem_insights
            
            WATER_STRESS_AVAILABLE = True
        else:
            WATER_STRESS_AVAILABLE = False
    except Exception as e:
        WATER_STRESS_AVAILABLE = False
        st.warning(f"Su Stresi Modelleri yüklenemedi: {e}")
    
    if WATER_STRESS_AVAILABLE:
        # Yeni Su Stresi Modelleri Dashboard'u
        render_section_divider()
        render_section_header(
            "🌊 Su Stresi İstihbarat Modelleri",
            "Tarımsal, kentsel ve ekosistem su stresi analiz modelleri",
            step_number=1,
            step_title="ANALİZ"
        )
        
        # Seçilen modele göre tek görünüm (sidebar'daki Model Seçimi)
        selected_model = st.session_state.get("public_selected_model", 1)
        root_dir = Path(__file__).resolve().parent.parent / "deneme"
        geojson_path_str = st.session_state.get("public_geojson_path") or str(
            root_dir / "outputs" / (
                "model1_water_stress.geojson" if selected_model == 1 else
                "model2_urban_water_stress.geojson" if selected_model == 2 else
                "model3_ecosystem_resilience.geojson"
            )
        )
        
        if selected_model == 1:
            st.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)
            st.markdown("### 🌾 Model 1: Tarımsal Su Stresi İstihbaratı")
            st.markdown("Tarımsal bölgeler için su stresi skorunu hesaplar.")
            
            try:
                gdf = load_model1_results(geojson_path_str)
                if not gdf.empty:
                    score_col = "final_water_stress_score"
                    if score_col in gdf.columns:
                        # Harita ve tablo
                        map_col, table_col = st.columns((2, 1))
                        
                        with map_col:
                            st.markdown("#### Su Stresi Haritası")
                            m = make_water_stress_map(gdf)
                            st_folium(m, width="100%", height=600)
                        
                        with table_col:
                            st.markdown("#### En Yüksek Riskli 10 Tarımsal Bölge")
                            top10 = gdf[[score_col, "drought_norm", "groundwater_norm", "agricultural_area_pressure"]].copy()
                            top10 = top10.sort_values(score_col, ascending=False).head(10)
                            if "geometry" in top10.columns:
                                top10 = pd.DataFrame(top10.drop(columns="geometry"))
                            st.dataframe(top10.reset_index(drop=True), use_container_width=True)
                        
                        # Otomatik içgörüler
                        st.markdown("---")
                        st.markdown("#### Otomatik İçgörüler")
                        insights = _compute_automated_insights(gdf, score_col=score_col)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            render_metric_card(
                                "🔴",
                                "Yüksek Risk",
                                f"{insights['high_risk_share_pct']:.1f}%",
                                "En üst %5",
                                color="danger"
                            )
                        with col2:
                            render_metric_card(
                                "🟡",
                                "Orta Risk",
                                f"{insights['medium_risk_share_pct']:.1f}%",
                                "%40–70 bandı",
                                color="warning"
                            )
                        with col3:
                            render_metric_card(
                                "🟢",
                                "Düşük Risk",
                                f"{insights['low_risk_share_pct']:.1f}%",
                                "%40 altı",
                                color="success"
                            )
                        
                        cluster_insights = insights.get("cluster_insights") or []
                        if cluster_insights:
                            st.markdown("**Riskin mekansal desenleri:**")
                            for line in cluster_insights:
                                render_insight_box("📍", line, icon="📍", type="info")
                        
                        recommended_actions = insights.get("recommended_actions") or []
                        if recommended_actions:
                            st.markdown("**Önerilen eylemler:**")
                            for action in recommended_actions:
                                render_insight_box("💡", action, icon="💡", type="success")
                    else:
                        st.error(f"Beklenen '{score_col}' sütunu veride bulunamadı.")
                else:
                    st.warning("Yüklenen GeoJSON dosyası hiçbir özellik içermiyor.")
            except FileNotFoundError as e:
                st.error(str(e))
                st.info("GeoJSON çıktısını oluşturmak için önce Model 1'i çalıştırın.")
            except Exception as e:
                st.error(f"GeoJSON yüklenemedi: {e}")
        
        elif selected_model == 2:
            st.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)
            st.markdown("### 🏙️ Model 2: Kentsel Su Stresi İstihbaratı")
            st.markdown("Şehir düzeyinde su stresi analizi.")
            
            try:
                gdf = load_model2_results(geojson_path_str)
                if not gdf.empty:
                    score_col = "urban_water_stress_score"
                    if score_col in gdf.columns:
                        # Filter out zero scores for better visualization
                        gdf_non_zero = gdf[gdf[score_col] > 0].copy() if (gdf[score_col] > 0).any() else gdf.copy()
                        
                        map_col, table_col = st.columns((2, 1))
                        with map_col:
                            st.markdown("#### Kentsel Su Stresi Haritası")
                            try:
                                if not gdf.empty and gdf.geometry.notna().any():
                                    m = make_urban_water_stress_map(gdf)
                                    st_folium(m, width="100%", height=600)
                                else:
                                    st.warning("Harita için geçerli geometri verisi bulunamadı.")
                            except Exception as map_error:
                                st.error(f"Harita oluşturulamadı: {map_error}")
                                import traceback
                                st.code(traceback.format_exc())
                                # Fallback: show basic map
                                try:
                                    bounds = gdf.total_bounds
                                    center_lat = (bounds[1] + bounds[3]) / 2
                                    center_lon = (bounds[0] + bounds[2]) / 2
                                    m = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles="cartodbpositron")
                                    st_folium(m, width="100%", height=600)
                                except:
                                    st.error("Harita gösterilemedi.")
                        with table_col:
                            st.markdown("#### En Yüksek Stresli 10 Şehir")
                            # Find city name column
                            city_name_col = None
                            for col_name in ["name", "city_name", "city", "NAME", "CITY_NAME", "CITY", "kentAtlasiDegeri"]:
                                if col_name in gdf.columns:
                                    city_name_col = col_name
                                    break
                            
                            display_cols = [score_col, "total_population", "estimated_water_supply"]
                            if city_name_col:
                                display_cols.insert(0, city_name_col)
                            
                            top10 = gdf[display_cols].copy()
                            # Check if all scores are zero
                            if (gdf[score_col] == 0).all():
                                st.warning("⚠️ Tüm şehirlerin su stresi skoru 0. Bu, veri eksikliği veya model hesaplama sorunu olabilir. Lütfen Model 2'yi tekrar çalıştırın.")
                            top10 = top10.sort_values(score_col, ascending=False).head(10)
                            if "geometry" in top10.columns:
                                top10 = pd.DataFrame(top10.drop(columns="geometry"))
                            
                            # Format columns
                            if "total_population" in top10.columns:
                                top10["total_population"] = top10["total_population"].apply(
                                    lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
                                )
                            if "estimated_water_supply" in top10.columns:
                                top10["estimated_water_supply"] = top10["estimated_water_supply"].apply(
                                    lambda x: f"{x:.2f}" if pd.notna(x) else "N/A"
                                )
                            if score_col in top10.columns:
                                top10[score_col] = top10[score_col].apply(
                                    lambda x: f"{x:.3f}" if pd.notna(x) else "N/A"
                                )
                            
                            rename_dict = {
                                score_col: "Su Stresi Skoru",
                                "total_population": "Nüfus",
                                "estimated_water_supply": "Su Arzı",
                            }
                            if city_name_col:
                                rename_dict[city_name_col] = "Şehir Adı"
                            top10 = top10.rename(columns=rename_dict)
                            st.dataframe(top10.reset_index(drop=True), use_container_width=True)
                        
                        st.markdown("---")
                        st.markdown("#### Otomatik Kentsel İçgörüler")
                        if _compute_urban_insights:
                            insights = _compute_urban_insights(gdf, score_col=score_col)
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                render_metric_card("🔴", "Yüksek Risk", f"{insights['high_risk_share_pct']:.1f}%", "En üst %20", color="danger")
                            with col2:
                                render_metric_card("🟡", "Orta Risk", f"{insights['medium_risk_share_pct']:.1f}%", "%40–80 bandı", color="warning")
                            with col3:
                                render_metric_card("🟢", "Düşük Risk", f"{insights['low_risk_share_pct']:.1f}%", "En alt %40", color="success")
                            
                            pattern_insights = insights.get("pattern_insights") or []
                            if pattern_insights:
                                st.markdown("**Riskin mekansal desenleri:**")
                                for line in pattern_insights:
                                    render_insight_box("📊", line, icon="📊", type="info")
                            
                            recommended_actions = insights.get("recommended_actions") or []
                            if recommended_actions:
                                st.markdown("**Önerilen eylemler:**")
                                for action in recommended_actions:
                                    render_insight_box("💡", action, icon="💡", type="success")
                    else:
                        st.error(f"Beklenen '{score_col}' sütunu veride bulunamadı.")
                else:
                    st.warning("Yüklenen GeoJSON dosyası hiçbir özellik içermiyor.")
            except FileNotFoundError as e:
                st.error(str(e))
                st.info("GeoJSON çıktısını oluşturmak için önce Model 2'yi çalıştırın.")
            except Exception as e:
                st.error(f"Model 2 yüklenemedi: {e}")
        
        else:
            st.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)
            st.markdown("### 🌿 Model 3: Ekosistem Su Direnci İstihbaratı")
            st.markdown("Korunan alanlar için su kırılganlığı analizi.")
            
            try:
                gdf = load_model3_results(geojson_path_str)
                if not gdf.empty:
                    score_col = "ecosystem_water_sensitivity_score"
                    if score_col in gdf.columns:
                        map_col, table_col = st.columns((2, 1))
                        with map_col:
                            st.markdown("#### Ekosistem Su Hassasiyeti Haritası")
                            try:
                                if not gdf.empty and gdf.geometry.notna().any():
                                    m = make_ecosystem_resilience_map(gdf)
                                    st_folium(m, width="100%", height=600)
                                else:
                                    st.warning("Harita için geçerli geometri verisi bulunamadı.")
                            except Exception as map_error:
                                st.error(f"Harita oluşturulamadı: {map_error}")
                                import traceback
                                st.code(traceback.format_exc())
                                # Fallback: show basic map
                                try:
                                    bounds = gdf.total_bounds
                                    center_lat = (bounds[1] + bounds[3]) / 2
                                    center_lon = (bounds[0] + bounds[2]) / 2
                                    m = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles="cartodbpositron")
                                    st_folium(m, width="100%", height=600)
                                except:
                                    st.error("Harita gösterilemedi.")
                        with table_col:
                            st.markdown("#### En Yüksek Riskli 10 Ekosistem")
                            # Find ecosystem name column
                            ecosystem_name_col = None
                            for col_name in ["ka_adi", "name", "ecosystem_name"]:
                                if col_name in gdf.columns:
                                    ecosystem_name_col = col_name
                                    break
                            
                            display_cols = [score_col, "drought_norm", "groundwater_sensitivity_norm", "ecosystem_type"]
                            if ecosystem_name_col:
                                display_cols.insert(0, ecosystem_name_col)
                            
                            top10 = gdf[display_cols].copy()
                            top10 = top10.sort_values(score_col, ascending=False).head(10)
                            if "geometry" in top10.columns:
                                top10 = pd.DataFrame(top10.drop(columns="geometry"))
                            
                            # Format columns
                            if score_col in top10.columns:
                                top10[score_col] = top10[score_col].apply(
                                    lambda x: f"{x:.3f}" if pd.notna(x) else "N/A"
                                )
                            for col in ["drought_norm", "groundwater_sensitivity_norm"]:
                                if col in top10.columns:
                                    top10[col] = top10[col].apply(
                                        lambda x: f"{x:.3f}" if pd.notna(x) else "N/A"
                                    )
                            
                            rename_dict = {
                                score_col: "Hassasiyet Skoru",
                                "drought_norm": "Kuraklık",
                                "groundwater_sensitivity_norm": "Yeraltı Suyu",
                                "ecosystem_type": "Tip",
                            }
                            if ecosystem_name_col:
                                rename_dict[ecosystem_name_col] = "Ekosistem Adı"
                            top10 = top10.rename(columns=rename_dict)
                            st.dataframe(top10.reset_index(drop=True), use_container_width=True)
                        
                        # Otomatik içgörüler
                        st.markdown("---")
                        st.markdown("#### Otomatik Ekosistem İçgörüleri")
                        if _compute_ecosystem_insights:
                            insights = _compute_ecosystem_insights(gdf, score_col=score_col)
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                render_metric_card("🔴", "Yüksek Hassasiyet", f"{insights['high_risk_share_pct']:.1f}%", "En üst %20", color="danger")
                            with col2:
                                render_metric_card("🟡", "Orta Hassasiyet", f"{insights['medium_risk_share_pct']:.1f}%", "%40–80 bandı", color="warning")
                            with col3:
                                render_metric_card("🟢", "Düşük Hassasiyet", f"{insights['low_risk_share_pct']:.1f}%", "%40 altı", color="success")
                            
                            pattern_insights = insights.get("pattern_insights") or []
                            if pattern_insights:
                                st.markdown("**Mekansal ve ekolojik desenler:**")
                                for line in pattern_insights:
                                    render_insight_box("🌍", line, icon="🌍", type="info")
                            
                            recommended_actions = insights.get("recommended_actions") or []
                            if recommended_actions:
                                st.markdown("**Önerilen eylemler:**")
                                for action in recommended_actions:
                                    render_insight_box("💡", action, icon="💡", type="success")
                        
                        # Bileşen analizi
                        st.markdown("---")
                        st.markdown("#### Bileşen Analizi")
                        component_cols = [
                            "drought_norm",
                            "groundwater_sensitivity_norm",
                            "wetland_proximity_risk_norm",
                            "protected_area_importance_norm",
                        ]
                        
                        component_data = []
                        component_names_tr = {
                            "drought_norm": "Kuraklık",
                            "groundwater_sensitivity_norm": "Yeraltı Suyu Hassasiyeti",
                            "wetland_proximity_risk_norm": "Sulak Alan Yakınlık Riski",
                            "protected_area_importance_norm": "Korunan Alan Önemi",
                        }
                        
                        for col in component_cols:
                            if col in gdf.columns:
                                component_data.append({
                                    "Bileşen": component_names_tr.get(col, col.replace("_norm", "").replace("_", " ").title()),
                                    "Ortalama": f"{gdf[col].mean():.3f}",
                                    "Min": f"{gdf[col].min():.3f}",
                                    "Max": f"{gdf[col].max():.3f}",
                                    "Ağırlık": "35%" if "drought" in col else "30%" if "groundwater" in col else "20%" if "wetland" in col else "15%",
                                })
                        
                        if component_data:
                            comp_df = pd.DataFrame(component_data)
                            st.dataframe(comp_df, use_container_width=True)
                    else:
                        st.error(f"Beklenen '{score_col}' sütunu veride bulunamadı.")
                else:
                    st.warning("Yüklenen GeoJSON dosyası hiçbir özellik içermiyor.")
            except FileNotFoundError as e:
                st.error(str(e))
                st.info("GeoJSON çıktısını oluşturmak için önce Model 3'ü çalıştırın.")
            except Exception as e:
                st.error(f"Model 3 yüklenemedi: {e}")
    
    else:
        # Eski kamu modu içeriği kaldırıldı - yeni dashboard kullanılıyor
        render_section_divider()
        render_insight_box(
            "⚠️ Su Stresi Modelleri Yüklenemedi",
            "Yeni su stresi modelleri yüklenemedi. Lütfen `water_stress_helpers.py` dosyasının doğru konumda olduğundan emin olun.",
            icon="⚠️",
            type="warning"
        )
