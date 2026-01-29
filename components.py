"""
UI Components for Smart Irrigation Dashboard
Premium SaaS-style reusable components - Jury-Ready Edition
Using Streamlit native components for reliable rendering
"""
import streamlit as st
from typing import Dict, Optional, Tuple, List


def render_platform_header(platform_mode: str) -> None:
    """Render the premium platform header with government/SaaS authority."""
    mode_icon = "👩‍🌾" if "Bireysel" in platform_mode else "🏛"
    mode_label = "Bireysel / Çiftçi" if "Bireysel" in platform_mode else "Kamu / Belediye"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%); 
                padding: 1.25rem 1.75rem; border-radius: 16px; margin-bottom: 1.5rem;
                border-left: 4px solid #059669; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem;">
            <div>
                <p style="color: #10B981; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.12em; margin: 0 0 0.25rem 0; font-weight: 600;">
                    Ulusal Su İstihbarat Platformu · Veri Odaklı Karar Desteği
                </p>
                <h1 style="color: white; font-size: 1.5rem; font-weight: 800; margin: 0; letter-spacing: -0.02em;">
                    SinerjiX — Akıllı Su ve Sulama Yönetimi
                </h1>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="background: rgba(16, 185, 129, 0.15); padding: 0.4rem 0.85rem; border-radius: 8px; 
                            color: #34D399; font-weight: 700; font-size: 0.75rem; border: 1px solid rgba(16,185,129,0.3);">{mode_icon} {mode_label}</span>
                <span style="background: rgba(59, 130, 246, 0.15); padding: 0.4rem 0.85rem; border-radius: 8px;
                            color: #60A5FA; font-weight: 600; font-size: 0.7rem;">v2.0</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_section_divider() -> None:
    """Render a premium section divider."""
    st.markdown("---")


def render_metric_card(
    icon: str,
    label: str,
    value: str,
    subtitle: Optional[str] = None,
    trend: Optional[str] = None,
    color: str = "primary"
) -> None:
    """Render a premium metric card."""
    color_map = {
        "primary": ("#3B82F6", "#EFF6FF"),
        "success": ("#10B981", "#ECFDF5"),
        "warning": ("#F59E0B", "#FFFBEB"),
        "danger": ("#EF4444", "#FEF2F2"),
        "info": ("#06B6D4", "#ECFEFF")
    }
    
    accent_color, bg_color = color_map.get(color, color_map["primary"])
    
    subtitle_html = f'<div style="font-size: 0.8rem; color: #64748B; margin-top: 0.5rem;">{subtitle}</div>' if subtitle else ''
    trend_html = f'<div style="font-size: 0.75rem; color: {accent_color}; font-weight: 600; margin-top: 0.25rem;">{trend}</div>' if trend else ''
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {bg_color} 0%, #FFFFFF 100%); 
                border-radius: 12px; padding: 1.25rem; border-left: 4px solid {accent_color};
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
            <span style="font-size: 1.25rem;">{icon}</span>
            <span style="font-size: 0.75rem; font-weight: 600; color: #64748B; text-transform: uppercase;">{label}</span>
        </div>
        <div style="font-size: 1.75rem; font-weight: 800; color: #0F172A;">{value}</div>
        {subtitle_html}
        {trend_html}
    </div>
    """, unsafe_allow_html=True)


def render_drought_risk_card(drought: Dict) -> None:
    """Render 🌵 Drought Risk card from GeoJSON SPI data."""
    available = drought.get("data_available", False)
    spi_label = drought.get("spi_label", "—")
    risk_label = drought.get("risk_label", "Düşük")
    source = drought.get("source", "Dataset unavailable")
    
    color_map = {
        "Düşük": ("#059669", "#ECFDF5"),
        "Orta": ("#D97706", "#FFFBEB"),
        "Yüksek": ("#DC2626", "#FEF2F2"),
        "Ekstrem": ("#7F1D1D", "#FEE2E2"),
    }
    accent, bg = color_map.get(risk_label, ("#64748B", "#F8FAFC"))
    
    if not available:
        accent, bg = "#64748B", "#F8FAFC"
        risk_label = "—"
        spi_label = "—"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {bg} 0%, #FFFFFF 100%); 
                border-radius: 12px; padding: 1.25rem; border-left: 4px solid {accent};
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); margin-bottom: 1rem;">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
            <span style="font-size: 1.25rem;">🌵</span>
            <span style="font-size: 0.75rem; font-weight: 600; color: #64748B; text-transform: uppercase;">Kuraklık Riski (SPI)</span>
        </div>
        <div style="font-size: 1.5rem; font-weight: 800; color: #0F172A;">{spi_label}</div>
        <div style="font-size: 0.8rem; color: #475569; margin-top: 0.25rem;">SPI (6 ay)</div>
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem; flex-wrap: wrap;">
            <span style="background: {accent}20; color: {accent}; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 700;">{risk_label}</span>
            <span style="font-size: 0.7rem; color: #94A3B8;">{source}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_water_basin_card(basin: Dict) -> None:
    """Render 💧 Water Basin Information card from watershed GeoJSON."""
    available = basin.get("data_available", False)
    basin_name = basin.get("basin_name", "—")
    basin_id = basin.get("basin_id")
    stress_label = basin.get("water_stress_label", "—")
    source = basin.get("source", "Dataset unavailable")
    
    stress_colors = {"Düşük": ("#059669", "#ECFDF5"), "Orta": ("#D97706", "#FFFBEB"), "Yüksek": ("#DC2626", "#FEF2F2")}
    accent, bg = stress_colors.get(stress_label, ("#3B82F6", "#EFF6FF"))
    if not available or stress_label in ("—", "Veri yok"):
        accent, bg = "#64748B", "#F8FAFC"
    
    # Convert hex color to RGBA for semi-transparent background (like drought card uses accent20)
    def hex_to_rgba(hex_color, alpha=0.2):
        """Convert hex color to RGBA string."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"
    
    accent_bg_rgba = hex_to_rgba(accent, 0.2)
    
    # Build ID section as plain string (not nested f-string)
    id_html = ''
    if basin_id:
        id_html = f'<div style="font-size: 0.75rem; color: #64748B; margin-top: 0.2rem;">No: {basin_id}</div>'
    
    # Build complete HTML string - concatenate parts to avoid nested f-string issues
    html_parts = [
        f'<div style="background: linear-gradient(135deg, {bg} 0%, #FFFFFF 100%); ',
        f'border-radius: 12px; padding: 1.25rem; border-left: 4px solid {accent}; ',
        'box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); margin-bottom: 1rem;">',
        '<div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">',
        '<span style="font-size: 1.25rem;">💧</span>',
        '<span style="font-size: 0.75rem; font-weight: 600; color: #64748B; text-transform: uppercase;">Havza Bilgisi</span>',
        '</div>',
        f'<div style="font-size: 1.1rem; font-weight: 700; color: #0F172A;">{basin_name}</div>',
        id_html,
        '<div style="display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem; flex-wrap: wrap;">',
        '<span style="font-size: 0.7rem; color: #64748B;">Su yönetimi riski:</span>',
        f'<span style="background: {accent_bg_rgba}; color: {accent}; padding: 0.2rem 0.5rem; border-radius: 6px; font-size: 0.7rem; font-weight: 700;">{stress_label}</span>',
        f'<span style="font-size: 0.65rem; color: #94A3B8;">{source}</span>',
        '</div>',
        '</div>'
    ]
    
    html_content = ''.join(html_parts)
    st.markdown(html_content, unsafe_allow_html=True)


def render_key_metrics_bar(
    temp: float,
    humidity: float,
    wind: float,
    water_need: float,
    et0: float,
    city: str,
    user_type: Optional[str],
    platform_mode: str,
    drought_risk: Optional[str] = None
) -> None:
    """Render key metrics using Streamlit columns."""
    
    # Format water need
    if water_need >= 1000000:
        water_display = f"{water_need/1000000:.2f}M L"
    elif water_need >= 1000:
        water_display = f"{water_need/1000:.1f} m³"
    else:
        water_display = f"{water_need:.0f} L"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); 
                border-radius: 16px; padding: 1.25rem; margin-bottom: 0.5rem; border-left: 4px solid #10B981;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.25rem;">📊</span>
                <span style="color: white; font-size: 1rem; font-weight: 700;">Durum Özeti — Meteoroloji & Su İhtiyacı</span>
            </div>
            <span style="background: rgba(16, 185, 129, 0.2); color: #34D399; padding: 0.25rem 0.75rem; 
                        border-radius: 8px; font-size: 0.75rem; font-weight: 600;">📍 {city}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div style="background: #1E293B; border-radius: 12px; padding: 1rem; text-align: center;">
            <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">🌡️</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: white;">{temp:.1f}°C</div>
            <div style="font-size: 0.65rem; color: #94A3B8; text-transform: uppercase;">Sıcaklık</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: #1E293B; border-radius: 12px; padding: 1rem; text-align: center;">
            <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">💧</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: white;">{humidity}%</div>
            <div style="font-size: 0.65rem; color: #94A3B8; text-transform: uppercase;">Nem</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: #1E293B; border-radius: 12px; padding: 1rem; text-align: center;">
            <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">🌬️</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: white;">{wind:.1f} m/s</div>
            <div style="font-size: 0.65rem; color: #94A3B8; text-transform: uppercase;">Rüzgar</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: #1E293B; border-radius: 12px; padding: 1rem; text-align: center;">
            <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">📈</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #10B981;">{et0:.2f} mm</div>
            <div style="font-size: 0.65rem; color: #94A3B8; text-transform: uppercase;">ET0</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div style="background: #1E293B; border-radius: 12px; padding: 1rem; text-align: center;">
            <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">💦</div>
            <div style="font-size: 1.25rem; font-weight: 800; color: #60A5FA;">{water_display}</div>
            <div style="font-size: 0.65rem; color: #94A3B8; text-transform: uppercase;">Su İhtiyacı</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Drought risk badge
    if drought_risk:
        risk_colors = {"Yüksek": ("#EF4444", "#FEE2E2"), "Orta": ("#F59E0B", "#FEF3C7"), "Düşük": ("#10B981", "#ECFDF5")}
        text_color, bg_color = risk_colors.get(drought_risk, ("#10B981", "#ECFDF5"))
        st.markdown(f"""
        <div style="text-align: center; margin-top: 0.5rem;">
            <span style="background: {bg_color}; color: {text_color}; padding: 0.5rem 1.5rem; 
                        border-radius: 9999px; font-weight: 700; font-size: 0.875rem;">
                ⚠️ Kuraklık Riski: {drought_risk}
            </span>
        </div>
        """, unsafe_allow_html=True)


def render_insight_box(
    title: str,
    message: str,
    icon: str = "💡",
    type: str = "info"
) -> None:
    """Render an insight box."""
    type_config = {
        "info": ("#06B6D4", "#ECFEFF", "#164E63"),
        "success": ("#10B981", "#ECFDF5", "#065F46"),
        "warning": ("#F59E0B", "#FFFBEB", "#92400E"),
        "danger": ("#EF4444", "#FEF2F2", "#991B1B"),
        "tip": ("#8B5CF6", "#F5F3FF", "#5B21B6")
    }
    
    accent_color, bg_color, text_color = type_config.get(type, type_config["info"])
    
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, {bg_color} 0%, #FFFFFF 20%); 
                border-radius: 12px; padding: 1.25rem; margin-bottom: 1rem;
                border-left: 4px solid {accent_color};">
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
            <span style="font-size: 1.25rem;">{icon}</span>
            <span style="font-size: 1rem; font-weight: 700; color: {text_color};">{title}</span>
        </div>
        <div style="font-size: 0.9rem; color: #475569; line-height: 1.6; padding-left: 1.75rem;">{message}</div>
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(text: str, status: str = "active") -> str:
    """Return status badge HTML string."""
    status_config = {
        "active": ("#D1FAE5", "#065F46"),
        "success": ("#D1FAE5", "#065F46"),
        "warning": ("#FEF3C7", "#92400E"),
        "danger": ("#FEE2E2", "#991B1B"),
        "high": ("#FEE2E2", "#991B1B"),
        "medium": ("#FEF3C7", "#92400E"),
        "low": ("#D1FAE5", "#065F46"),
        "info": ("#CFFAFE", "#164E63"),
        "neutral": ("#F1F5F9", "#475569")
    }
    
    bg_color, text_color = status_config.get(status, status_config["neutral"])
    
    return f'<span style="background: {bg_color}; color: {text_color}; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase;">{text}</span>'


def render_section_header(
    title: str,
    subtitle: Optional[str] = None,
    icon: Optional[str] = None,
    step_number: Optional[int] = None,
    step_title: Optional[str] = None
) -> None:
    """Render a section header with optional step indicator."""
    
    if step_number and step_title:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.75rem;">
            <div style="background: linear-gradient(135deg, #059669 0%, #047857 100%); 
                        color: white; width: 28px; height: 28px; border-radius: 50%;
                        display: flex; align-items: center; justify-content: center;
                        font-weight: 700; font-size: 0.8rem;">{step_number}</div>
            <span style="font-size: 0.7rem; font-weight: 700; color: #059669; text-transform: uppercase; letter-spacing: 0.1em;">
                {step_title}
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"### {title}")
    if subtitle:
        st.markdown(f'<p style="color: #64748B; font-size: 0.9rem; margin-top: -0.75rem; margin-bottom: 1rem;">{subtitle}</p>', unsafe_allow_html=True)


def get_user_type_config(user_type: str) -> Dict:
    """Get configuration for different user types."""
    configs = {
        "🪴 Ev Bahçesi": {
            "tone": "friendly",
            "complexity": "simple",
            "area_label": "Bahçe Alanı (m²)",
            "area_default": 10.0,
            "area_help": "Bahçenizin toplam alanını girin",
            "plant_label": "Bahçende Ne Yetiştiriyorsun?",
            "plants": ["Karışık Sebze", "Domates 🍅", "Biber 🌶", "Çiçek 🌸", "Çim 🌿"],
            "kc_map": {
                "Karışık Sebze": 1.0,
                "Domates 🍅": 1.05,
                "Biber 🌶": 1.0,
                "Çiçek 🌸": 0.95,
                "Çim 🌿": 0.9
            }
        },
        "🌱 Küçük Ölçekli Üretim": {
            "tone": "professional",
            "complexity": "moderate",
            "area_label": "Üretim Alanı (m²)",
            "area_default": 200.0,
            "area_help": "Toplam üretim alanınızı girin",
            "plant_label": "Yetiştirilen Tarım Ürünü",
            "plants": ["Buğday", "Mısır", "Şeker Pancarı", "Domates", "Yonca"],
            "kc_map": {
                "Buğday": 1.0,
                "Mısır": 1.2,
                "Şeker Pancarı": 1.15,
                "Domates": 1.1,
                "Yonca": 1.05
            }
        },
        "🚜 Ticari Tarım": {
            "tone": "data_driven",
            "complexity": "advanced",
            "area_label": "Tarla Alanı (m²)",
            "area_default": 1000.0,
            "area_help": "Toplam tarla alanınızı girin",
            "plant_label": "Yetiştirilen Tarım Ürünü",
            "plants": ["Buğday", "Mısır", "Şeker Pancarı", "Domates", "Yonca"],
            "kc_map": {
                "Buğday": 1.0,
                "Mısır": 1.2,
                "Şeker Pancarı": 1.15,
                "Domates": 1.1,
                "Yonca": 1.05
            }
        },
        "🏭 Büyük Tarım Alanı": {
            "tone": "analytical",
            "complexity": "expert",
            "area_label": "Büyük Tarım Alanı (m²)",
            "area_default": 5000.0,
            "area_help": "Toplam tarım alanınızı girin",
            "plant_label": "Yetiştirilen Tarım Ürünü",
            "plants": ["Buğday", "Mısır", "Şeker Pancarı", "Domates", "Yonca"],
            "kc_map": {
                "Buğday": 1.0,
                "Mısır": 1.2,
                "Şeker Pancarı": 1.15,
                "Domates": 1.1,
                "Yonca": 1.05
            }
        }
    }
    
    return configs.get(user_type, configs["🪴 Ev Bahçesi"])


def format_water_amount(liters: float, user_type: str) -> str:
    """Format water amount based on user type."""
    if liters < 100:
        return f"{liters:.1f} L"
    elif liters < 1000:
        return f"{liters:.0f} L"
    else:
        return f"{liters/1000:.2f} m³"


def get_irrigation_recommendation_text(
    rain_expected: bool,
    et0: float,
    best_hour: Optional[str],
    user_type: str
) -> Tuple[str, str, str]:
    """Get human-readable irrigation recommendation."""
    from utils import format_time
    
    formatted_hour = format_time(best_hour) if best_hour else None
    
    if rain_expected:
        return (
            "🌧 Yağmur Bekleniyor",
            "warning",
            "Meteoroloji verilerine göre yakın zamanda yağış beklenmektedir. Su tasarrufu için sulama işlemini erteleyebilirsiniz."
        )
    elif et0 < 2:
        return (
            "💧 Su İhtiyacı Düşük",
            "info",
            f"ET0 değeri {et0:.2f} mm - bitkilerinizin su ihtiyacı minimum seviyede."
        )
    else:
        return (
            f"✅ Önerilen Zaman: {formatted_hour}" if formatted_hour else "✅ Sulama Öneriliyor",
            "success",
            f"{formatted_hour if formatted_hour else 'Belirlenen saatte'} sulama için optimal koşullar mevcut."
        )


def render_ai_decision_engine(strategy_data: Dict) -> None:
    """Render the AI Decision Engine — main message first, details secondary."""
    strategy_type = strategy_data.get("strategy_type", "recommended")
    strategy_name = strategy_data.get("strategy_name", "Önerilen Strateji")
    recommendation = strategy_data.get("recommendation", "")
    reasoning = strategy_data.get("reasoning", [])
    action_items = strategy_data.get("action_items", [])
    weather_risk = strategy_data.get("weather_risk", "low")
    regional_insights = strategy_data.get("regional_insights", [])
    
    strategy_config = {
        "water_saving": ("#059669", "#ECFDF5", "🛡"),
        "risk_aware": ("#D97706", "#FFFBEB", "⚠"),
        "recommended": ("#1D4ED8", "#EFF6FF", "✓")
    }
    accent_color, bg_color, icon = strategy_config.get(strategy_type, strategy_config["recommended"])
    
    # Ana karar: tek cümle, en üstte
    if strategy_type == "water_saving":
        main_answer = "Sulama yapmanıza gerek yok"
        main_sub = "Yağış veya düşük su ihtiyacı nedeniyle şu an sulama önerilmiyor; su tasarrufu sağlanır."
    elif strategy_type == "risk_aware":
        main_answer = "Dikkatli sulama yapın"
        main_sub = "Koşullar elverişli ama hava veya su stresi var; önerilen zamanda ve miktarda sulayın."
    else:
        main_answer = "Sulama yapmanız önerilir"
        main_sub = "Mevcut verilere göre sulama uygun; önerilen saatte sulama yapabilirsiniz."
    
    # 1) Ana mesaj — en üstte, büyük ve net
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {bg_color} 0%, #FFFFFF 100%); 
                border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem;
                border-left: 5px solid {accent_color}; box-shadow: 0 4px 16px rgba(0,0,0,0.08);">
        <p style="color: #64748B; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; margin: 0 0 0.5rem 0; font-weight: 600;">
            Bugünkü karar
        </p>
        <h2 style="color: #0F172A; font-size: 1.5rem; font-weight: 800; margin: 0 0 0.35rem 0;">{main_answer}</h2>
        <p style="color: #475569; font-size: 0.9rem; line-height: 1.5; margin: 0;">{main_sub}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 2) Kısa özet (strategy name + tek paragraf)
    st.markdown(f"""
    <div style="background: white; border-radius: 10px; padding: 1rem; margin-bottom: 1rem; border: 1px solid #E2E8F0;">
        <p style="color: #64748B; font-size: 0.75rem; font-weight: 600; margin: 0 0 0.35rem 0;">{strategy_name}</p>
        <p style="color: #334155; font-size: 0.9rem; line-height: 1.6; margin: 0;">{recommendation}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 3) Detaylar tek expander içinde
    with st.expander("📋 Detaylar: gerekçe, veri ve aksiyonlar"):
        if reasoning:
            st.markdown("**Politika gerekçesi**")
            for i, reason in enumerate(reasoning, 1):
                st.markdown(f"{i}. {reason}")
            st.markdown("")
        if regional_insights:
            st.markdown("**Veri seti tabanlı istihbarat**")
            for insight in regional_insights:
                st.markdown(f"• {insight}")
            st.markdown("")
        if action_items:
            st.markdown("**Önerilen aksiyonlar**")
            for i, action in enumerate(action_items, 1):
                st.markdown(f"{i}. {action}")
    
    risk_config = {"low": ("Düşük", "#059669"), "medium": ("Orta", "#D97706"), "high": ("Yüksek", "#DC2626")}
    risk_text, risk_color = risk_config.get(weather_risk, ("Bilinmiyor", "#64748B"))
    st.markdown(f"""
    <div style="margin-top: 0.5rem; padding: 0.5rem 0.75rem; background: #F8FAFC; border-radius: 8px; border: 1px solid #E2E8F0; font-size: 0.8rem;">
        <span style="font-weight: 600; color: #0F172A;">Meteorolojik risk: </span>
        <span style="background: {risk_color}15; color: {risk_color}; padding: 0.2rem 0.5rem;
                    border-radius: 6px; font-weight: 700; font-size: 0.7rem;">{risk_text}</span>
    </div>
    """, unsafe_allow_html=True)


def render_sustainability_dashboard(metrics: Dict, platform_mode: str) -> None:
    """Hero Sustainability & Impact — explainable scoring, strategic insights."""
    water_saved = metrics.get("water_saved", 0)
    sustainability_score = metrics.get("sustainability_score", 0)
    cost_saved = metrics.get("cost_saved_tl", 0)
    co2_saved = metrics.get("co2_saved_kg", 0)
    impact_level = metrics.get("environmental_impact_level", "Düşük Etki")
    explainable = metrics.get("score_breakdown", {})
    
    if sustainability_score >= 80:
        score_color, score_label = "#059669", "Yüksek"
    elif sustainability_score >= 60:
        score_color, score_label = "#1D4ED8", "İyi"
    elif sustainability_score >= 40:
        score_color, score_label = "#D97706", "Orta"
    else:
        score_color, score_label = "#DC2626", "Geliştirilmeli"
    
    if water_saved >= 1000:
        water_display = f"{water_saved/1000:.2f} m³"
    else:
        water_display = f"{water_saved:.1f} L"
    
    hero_sub = "Su tasarrufu, maliyet ve çevresel etki — karar destek metrikleri." if "Bireysel" in platform_mode else "Bölgesel su yönetimi etkisi — politika ve operasyonel karar desteği."
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #047857 0%, #065F46 50%, #064E3B 100%); 
                border-radius: 16px; padding: 1.75rem; margin-bottom: 1rem; text-align: center;
                border: 1px solid rgba(16, 185, 129, 0.3); box-shadow: 0 8px 24px rgba(5, 150, 105, 0.2);">
        <p style="color: rgba(255,255,255,0.85); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.12em; margin: 0 0 0.5rem 0; font-weight: 600;">
            Sürdürülebilirlik ve Etki
        </p>
        <h2 style="color: white; font-size: 1.75rem; font-weight: 800; margin: 0 0 0.35rem 0;">Etki Raporu</h2>
        <p style="color: rgba(255,255,255,0.75); font-size: 0.85rem; margin: 0;">{hero_sub}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: #ECFDF5; border-radius: 12px; padding: 1.25rem; text-align: center; border: 1px solid #A7F3D0;">
            <div style="font-size: 2rem; margin-bottom: 0.25rem;">💧</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #065F46;">{water_display}</div>
            <div style="font-size: 0.7rem; color: #047857; text-transform: uppercase;">Tasarruf Edilen Su</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: #EFF6FF; border-radius: 12px; padding: 1.25rem; text-align: center; border: 1px solid #BFDBFE;">
            <div style="font-size: 2rem; margin-bottom: 0.25rem;">⭐</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #1E40AF;">{sustainability_score:.0f}/100</div>
            <div style="font-size: 0.7rem; color: #3B82F6; text-transform: uppercase;">Sürdürülebilirlik Skoru</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: #F5F3FF; border-radius: 12px; padding: 1.25rem; text-align: center; border: 1px solid #DDD6FE;">
            <div style="font-size: 2rem; margin-bottom: 0.25rem;">💰</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #5B21B6;">{cost_saved:.2f} ₺</div>
            <div style="font-size: 0.7rem; color: #7C3AED; text-transform: uppercase;">Maliyet Tasarrufu</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: #ECFEFF; border-radius: 12px; padding: 1.25rem; text-align: center; border: 1px solid #A5F3FC;">
            <div style="font-size: 2rem; margin-bottom: 0.25rem;">🌱</div>
            <div style="font-size: 1.5rem; font-weight: 800; color: #155E75;">{co2_saved:.2f} kg</div>
            <div style="font-size: 0.7rem; color: #0891B2; text-transform: uppercase;">CO₂ Tasarrufu</div>
        </div>
        """, unsafe_allow_html=True)
    
    explain_html = ""
    if explainable:
        eff = explainable.get("efficiency", 0)
        tim = explainable.get("timing", 0)
        env = explainable.get("environmental", 0)
        explain_html = f"""
        <div style="margin-top: 1rem; padding: 0.75rem 1rem; background: #F8FAFC; border-radius: 8px; font-size: 0.8rem; color: #475569;">
            <strong>Skor bileşenleri:</strong> Verimlilik {eff:.0f}% · Zamanlama {tim:.0f}% · Çevresel {env:.0f}%
        </div>
        """
    
    st.markdown(f"""
    <div style="background: white; border-radius: 12px; padding: 1.25rem; margin-top: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06); border: 1px solid #E2E8F0;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <span style="font-weight: 600; color: #0F172A;">Sürdürülebilirlik skoru</span>
            <span style="font-size: 1.5rem; font-weight: 800; color: {score_color};">{sustainability_score:.0f}</span>
        </div>
        <div style="background: #E2E8F0; border-radius: 9999px; height: 10px; overflow: hidden;">
            <div style="background: {score_color}; height: 100%; width: {min(100, sustainability_score)}%; border-radius: 9999px;"></div>
        </div>
        <div style="text-align: center; margin-top: 0.5rem;">
            <span style="background: {score_color}20; color: {score_color}; padding: 0.25rem 0.75rem;
                        border-radius: 6px; font-size: 0.75rem; font-weight: 700;">{score_label}</span>
        </div>
        {explain_html}
    </div>
    """, unsafe_allow_html=True)


def render_impact_story(platform_mode: str) -> None:
    """Render the Impact Story hero section — policy-grade, emotional, authority."""
    if "Bireysel" in platform_mode:
        title = "Tarlanız için akıllı sulama"
        subtitle = "Hava ve su ihtiyacınızı görün, doğru zamanda sulayın. Her damla değerli."
        stats = [
            {"value": "%30", "label": "Potansiyel Su Tasarrufu", "icon": "💧"},
            {"value": "ET₀", "label": "Bilimsel Referans", "icon": "📐"},
            {"value": "7/24", "label": "Meteorolojik Veri", "icon": "🌤"},
            {"value": "Veri", "label": "Odaklı Karar", "icon": "🎯"}
        ]
    else:
        title = "Bölgesel Su İstihbaratı ve Politika Desteği"
        subtitle = "Belediyeler ve karar vericiler için veri odaklı su yönetimi, kuraklık riski ve stratejik öneriler."
        stats = [
            {"value": "Bölge", "label": "Risk & Kaynak Analizi", "icon": "🗺"},
            {"value": "Kuraklık", "label": "Risk Değerlendirmesi", "icon": "⚠"},
            {"value": "Senaryo", "label": "Politika Simülasyonu", "icon": "📊"},
            {"value": "Veri Seti", "label": "Stratejik İstihbarat", "icon": "🔗"}
        ]
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0F172A 0%, #134E4A 40%, #0F172A 100%); 
                border-radius: 20px; padding: 2.25rem; margin-bottom: 1rem; text-align: center;
                border: 1px solid rgba(16, 185, 129, 0.2); box-shadow: 0 8px 32px rgba(0,0,0,0.2);">
        <p style="color: #34D399; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.15em; margin: 0 0 0.75rem 0; font-weight: 700;">
            Ulusal Su İstihbarat Platformu
        </p>
        <h1 style="color: white; font-size: 2.1rem; font-weight: 800; margin: 0 0 0.5rem 0; letter-spacing: -0.02em;">{title}</h1>
        <p style="color: #94A3B8; font-size: 0.95rem; line-height: 1.5; margin: 0; max-width: 560px; margin-left: auto; margin-right: auto;">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(4)
    for i, stat in enumerate(stats):
        with cols[i]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1E293B 0%, #334155 100%); 
                        border-radius: 12px; padding: 1rem; text-align: center; border: 1px solid rgba(255,255,255,0.06);">
                <div style="font-size: 1.5rem; margin-bottom: 0.25rem;">{stat['icon']}</div>
                <div style="font-size: 1.25rem; font-weight: 800; color: white;">{stat['value']}</div>
                <div style="font-size: 0.6rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em;">{stat['label']}</div>
            </div>
            """, unsafe_allow_html=True)


def render_decision_confidence_indicator(
    confidence_score: float,
    et0: float,
    forecast_count: int,
    strategy_type: str
) -> None:
    """Decision confidence indicator — authority, clarity."""
    if confidence_score >= 85:
        level, color, icon = "Çok Yüksek", "#059669", "✅"
    elif confidence_score >= 70:
        level, color, icon = "Yüksek", "#1D4ED8", "✓"
    elif confidence_score >= 55:
        level, color, icon = "Orta", "#D97706", "⚠"
    else:
        level, color, icon = "Düşük", "#DC2626", "⚠"
    
    st.markdown(f"""
    <div style="background: white; border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem;
                border: 1px solid #E2E8F0; border-left: 4px solid {color}; box-shadow: 0 4px 12px rgba(0,0,0,0.06);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <div>
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                    <span style="font-size: 1.5rem;">{icon}</span>
                    <h3 style="margin: 0; font-size: 1.2rem; font-weight: 700; color: #0F172A;">Karar Güvenilirliği</h3>
                </div>
                <p style="margin: 0; color: #64748B; font-size: 0.8rem;">Öneri güvenilirlik değerlendirmesi — veri kalitesi & strateji</p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 2.25rem; font-weight: 800; color: {color};">{confidence_score:.0f}%</div>
                <span style="background: {color}15; color: {color}; padding: 0.25rem 0.75rem;
                            border-radius: 6px; font-size: 0.7rem; font-weight: 700;">{level}</span>
            </div>
        </div>
        <div style="background: #E2E8F0; border-radius: 9999px; height: 10px; overflow: hidden;">
            <div style="background: {color}; height: 100%; width: {min(100, confidence_score)}%; border-radius: 9999px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Factors in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="background: #F8FAFC; border-radius: 8px; padding: 0.75rem; text-align: center;">
            <div style="font-size: 0.7rem; color: #64748B; text-transform: uppercase;">ET0</div>
            <div style="font-weight: 700; color: #0F172A;">{et0:.2f} mm</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background: #F8FAFC; border-radius: 8px; padding: 0.75rem; text-align: center;">
            <div style="font-size: 0.7rem; color: #64748B; text-transform: uppercase;">Veri</div>
            <div style="font-weight: 700; color: #0F172A;">{forecast_count} saat</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background: #F8FAFC; border-radius: 8px; padding: 0.75rem; text-align: center;">
            <div style="font-size: 0.7rem; color: #64748B; text-transform: uppercase;">Strateji</div>
            <div style="font-weight: 700; color: #0F172A;">{strategy_type.replace("_", " ").title()}</div>
        </div>
        """, unsafe_allow_html=True)


def render_regional_intelligence_layer(
    regional_intelligence: Dict,
    risk_assessment: Dict,
    platform_mode: str
) -> None:
    """Render the Regional Intelligence Layer using Streamlit columns."""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); 
                border-radius: 16px; padding: 1.25rem; margin-bottom: 1rem;
                border-left: 4px solid #06B6D4;">
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <span style="font-size: 1.5rem;">🧠</span>
            <div>
                <p style="color: #22D3EE; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.12em; margin: 0; font-weight: 600;">
                    Veri Seti Tabanlı Stratejik İstihbarat
                </p>
                <h3 style="color: white; font-size: 1.1rem; font-weight: 700; margin: 0;">Risk & Kaynak Analizi</h3>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(
        "Bu bölüm, seçtiğiniz bölgedeki **su kaynakları durumu** ve **risk faktörlerini** gösterir. "
        "Sulama kararlarınızı bölgesel verilere göre daha bilinçli almanız için sunulur."
    )
    
    water_resources = regional_intelligence.get("water_resources", {})
    
    def _fmt(val):
        """Show value or fallback; never show literal None."""
        if val is None:
            return "—"
        if isinstance(val, float):
            return f"{val:.2f}" if 0 <= val <= 1 else f"{val:.1f}"
        return str(val)
    
    groundwater = water_resources.get("groundwater_level")
    surface_water = water_resources.get("surface_water_availability")
    water_stress = water_resources.get("water_stress_index")
    
    groundwater_display = _fmt(groundwater) if groundwater is not None else "—"
    surface_water_display = _fmt(surface_water) if surface_water is not None else "—"
    water_stress_display = _fmt(water_stress) if water_stress is not None else "—"
    
    nearest = water_resources.get("nearest_region", False)
    nearest_name = water_resources.get("nearest_region_name") or ""
    if nearest and nearest_name:
        st.caption(f"📍 En yakın bölge verisi: **{nearest_name}**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div style="background: white; border-radius: 10px; padding: 1rem; border-left: 4px solid #06B6D4;">
            <div style="font-size: 1.25rem; margin-bottom: 0.25rem;">💧</div>
            <div style="font-size: 0.7rem; color: #64748B; text-transform: uppercase;">Yeraltı Su</div>
            <div style="font-size: 1rem; font-weight: 700; color: #0F172A;">{groundwater_display}</div>
            <div style="font-size: 0.65rem; color: #94A3B8;">{water_resources.get("measurement_unit", "m")}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: white; border-radius: 10px; padding: 1rem; border-left: 4px solid #3B82F6;">
            <div style="font-size: 1.25rem; margin-bottom: 0.25rem;">🌊</div>
            <div style="font-size: 0.7rem; color: #64748B; text-transform: uppercase;">Yüzey Suyu</div>
            <div style="font-size: 1rem; font-weight: 700; color: #0F172A;">{surface_water_display}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: white; border-radius: 10px; padding: 1rem; border-left: 4px solid #10B981;">
            <div style="font-size: 1.25rem; margin-bottom: 0.25rem;">📊</div>
            <div style="font-size: 0.7rem; color: #64748B; text-transform: uppercase;">Su Stresi</div>
            <div style="font-size: 1rem; font-weight: 700; color: #0F172A;">{water_stress_display}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("📖 Bu veriler ne anlama geliyor? Neden önemli?"):
        st.markdown("""
        **💧 Yeraltı Su (metre)**  
        Bölgedeki yeraltı su seviyesini gösterir. Yüksek değer, kuyu ve yeraltı kaynaklarının daha güvenilir olduğu anlamına gelir. Sulama planı yaparken uzun vadeli su teminini değerlendirmenize yardımcı olur.

        **🌊 Yüzey Suyu (Low / Medium / High)**  
        Baraj, göl ve akarsulardan yararlanma imkânını özetler. *High* bölgede yüzey suyu bol demektir; *Low* ise yüzey suyuna bağımlılığı azaltıp tasarruf önlemlerini öne çıkarmanız gerektiğini gösterir.

        **📊 Su Stresi İndeksi (0–1)**  
        Bölgenin su talebi ile arzı arasındaki baskıyı ifade eder. **0’a yakın** = su baskısı düşük, **1’e yakın** = su kıtlığı riski yüksek. Sulama miktarını ve zamanlamasını bu indekse göre ayarlamak verimlilik ve sürdürülebilirlik açısından önemlidir.

        **🎯 Risk Faktörleri**  
        Meteoroloji, su kaynağı stresi ve yeraltı su seviyesi gibi etkenlerin sulama kararınıza etkisini özetler. *High* risk, daha dikkatli planlama ve tasarruf önlemleri; *Low* risk ise mevcut stratejinizi sürdürebileceğiniz anlamına gelir.
        """)
    
    # Risk factors (explanations only in expander above)
    risk_factors = risk_assessment.get("risk_factors", [])
    if risk_factors:
        st.markdown("#### 🎯 Risk Faktörleri — Dataset Tabanlı")
        for factor in risk_factors[:3]:
            risk_color_map = {"high": "#EF4444", "medium": "#F59E0B", "low": "#10B981", "info": "#3B82F6"}
            factor_color = risk_color_map.get(factor.get("level", "info"), "#64748B")
            factor_name = factor.get("factor", "")
            
            st.markdown(f"""
            <div style="background: white; border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;
                        border-left: 3px solid {factor_color};">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 600; color: #0F172A; font-size: 0.875rem;">{factor_name}</span>
                    <span style="background: {factor_color}20; color: {factor_color}; padding: 0.125rem 0.5rem;
                                border-radius: 9999px; font-size: 0.65rem; font-weight: 700;">{factor.get("level", "").upper()}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Status
    data_available = risk_assessment.get("regional_data_available", False)
    status_color = "#10B981" if data_available else "#3B82F6"
    status_text = "Aktif" if data_available else "Hazır"
    
    st.markdown(f"""
    <div style="background: #F8FAFC; border-radius: 8px; padding: 0.75rem; margin-top: 1rem; border: 1px solid #E2E8F0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.75rem; color: #64748B; font-weight: 500;">Dataset tabanlı istihbarat</span>
            <span style="background: {status_color}20; color: {status_color}; padding: 0.25rem 0.75rem;
                        border-radius: 6px; font-size: 0.7rem; font-weight: 700;">{status_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_scenario_simulator(scenario_data: Dict, platform_mode: str) -> None:
    """Render the Scenario Simulator using Streamlit columns."""
    scenarios = scenario_data.get("scenarios", {})
    best_scenario = scenario_data.get("best_scenario", "")
    water_difference = scenario_data.get("water_difference", 0)
    recommended = scenario_data.get("recommended_scenario", "")
    
    st.markdown("### 📊 Politika Senaryo Simülatörü")
    st.markdown('<p style="color: #64748B; font-size: 0.8rem; margin-top: -0.5rem; margin-bottom: 1rem;">Sulama stratejilerini karşılaştırın — karar destek</p>', unsafe_allow_html=True)
    
    scenario_order = ["today", "delay", "water_saving", "normal"]
    cols = st.columns(4)
    
    for idx, key in enumerate(scenario_order):
        if key in scenarios:
            scenario = scenarios[key]
            is_recommended = scenario["name"] == recommended
            
            water_val = scenario["water_used"]
            water_display = f"{water_val/1000:.2f} m³" if water_val >= 1000 else f"{water_val:.0f} L"
            
            border_color = "#10B981" if is_recommended else "#E2E8F0"
            bg_color = "#ECFDF5" if is_recommended else "white"
            
            with cols[idx]:
                badge_html = '<div style="margin-top: 0.5rem;"><span style="background: #10B98120; color: #10B981; padding: 0.125rem 0.5rem; border-radius: 9999px; font-size: 0.6rem; font-weight: 700;">ÖNERİLEN</span></div>' if is_recommended else ''
                
                st.markdown(f"""
                <div style="background: {bg_color}; border-radius: 12px; padding: 1rem;
                            border: 2px solid {border_color}; height: 100%;">
                    <div style="font-weight: 700; color: #0F172A; font-size: 0.8rem; margin-bottom: 0.5rem;">{scenario["name"]}</div>
                    <div style="font-size: 1.25rem; font-weight: 800; color: #0F172A;">{water_display}</div>
                    <div style="font-size: 0.65rem; color: #64748B; margin-bottom: 0.5rem;">Su Kullanımı</div>
                    <div style="font-weight: 700; color: #10B981; font-size: 1rem;">{scenario["sustainability_score"]}/100</div>
                    <div style="font-size: 0.65rem; color: #64748B;">Skor</div>
                    {badge_html}
                </div>
                """, unsafe_allow_html=True)
    
    # Summary
    st.markdown(f"""
    <div style="background: #EFF6FF; border-radius: 12px; padding: 1rem; margin-top: 1rem; text-align: center;">
        <span style="font-weight: 600; color: #0F172A;">Potansiyel Tasarruf: </span>
        <span style="font-weight: 800; color: #3B82F6; font-size: 1.25rem;">{water_difference/1000:.2f} m³</span>
    </div>
    """, unsafe_allow_html=True)


def render_executive_summary(
    weather_data: Dict,
    strategy_data: Dict,
    sustainability_metrics: Dict,
    confidence_score: float,
    platform_mode: str
) -> None:
    """Executive summary for decision-makers — strategic intelligence."""
    
    strategy_name = strategy_data.get("strategy_name", "Önerilen Strateji")
    water_saved = sustainability_metrics.get("water_saved", 0)
    sustainability_score = sustainability_metrics.get("sustainability_score", 0)
    
    water_display = f"{water_saved/1000:.2f} m³" if water_saved >= 1000 else f"{water_saved:.1f} L"
    
    sub = "Karar vericiler için özet metrikler." if "Bireysel" in platform_mode else "Belediye ve politika karar vericileri için stratejik özet."
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); 
                border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; text-align: center;
                border-left: 4px solid #059669;">
        <p style="color: #34D399; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.15em; margin: 0 0 0.5rem 0; font-weight: 600;">
            Yönetici Özeti · Stratejik Karar Desteği
        </p>
        <h2 style="color: white; font-size: 1.5rem; font-weight: 800; margin: 0 0 0.25rem 0;">Karar Özeti</h2>
        <p style="color: #94A3B8; font-size: 0.8rem; margin: 0;">{sub}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: #ECFDF5; border-radius: 10px; padding: 1rem; text-align: center; border: 1px solid #A7F3D0;">
            <div style="font-size: 0.6rem; color: #047857; text-transform: uppercase; margin-bottom: 0.25rem; font-weight: 600;">Strateji</div>
            <div style="font-weight: 700; color: #065F46; font-size: 0.85rem;">{strategy_name}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: #EFF6FF; border-radius: 10px; padding: 1rem; text-align: center; border: 1px solid #BFDBFE;">
            <div style="font-size: 0.6rem; color: #1D4ED8; text-transform: uppercase; margin-bottom: 0.25rem; font-weight: 600;">Güvenilirlik</div>
            <div style="font-weight: 700; color: #1E40AF; font-size: 0.85rem;">{confidence_score:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: #F5F3FF; border-radius: 10px; padding: 1rem; text-align: center; border: 1px solid #DDD6FE;">
            <div style="font-size: 0.6rem; color: #6D28D9; text-transform: uppercase; margin-bottom: 0.25rem; font-weight: 600;">Su Tasarrufu</div>
            <div style="font-weight: 700; color: #5B21B6; font-size: 0.85rem;">{water_display}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: #FFFBEB; border-radius: 10px; padding: 1rem; text-align: center; border: 1px solid #FDE68A;">
            <div style="font-size: 0.6rem; color: #B45309; text-transform: uppercase; margin-bottom: 0.25rem; font-weight: 600;">Sürdürülebilirlik</div>
            <div style="font-weight: 700; color: #92400E; font-size: 0.85rem;">{sustainability_score:.0f}/100</div>
        </div>
        """, unsafe_allow_html=True)


def render_action_card(
    title: str,
    description: str,
    action_label: str,
    action_key: str,
    icon: str = "🚀"
) -> bool:
    """Render an action card with button."""
    st.markdown(f"""
    <div style="background: white; border-radius: 12px; padding: 1.5rem; text-align: center;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05); margin-bottom: 1rem;">
        <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">{icon}</div>
        <h3 style="color: #0F172A; font-size: 1.25rem; font-weight: 700; margin: 0 0 0.5rem 0;">{title}</h3>
        <p style="color: #64748B; font-size: 0.875rem; line-height: 1.5; margin: 0 0 1rem 0;">{description}</p>
    </div>
    """, unsafe_allow_html=True)
    
    return st.button(action_label, key=action_key, use_container_width=True, type="primary")
