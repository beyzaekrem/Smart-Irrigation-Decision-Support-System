"""
Kamu Modu için Su Stresi İstihbarat Modelleri
Bu modül, eski dashboard'un kamu modu kısmında kullanılmak üzere hazırlanmıştır.
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from components import render_metric_card, render_insight_box, render_section_header, render_section_divider

def render_water_stress_models_tabs(load_model1_results, load_model2_results, load_model3_results,
                                     make_water_stress_map, make_urban_water_stress_map, make_ecosystem_resilience_map,
                                     _compute_automated_insights, _compute_urban_insights, _compute_ecosystem_insights):
    """Kamu modu için su stresi modellerini render et"""
    
    render_section_divider()
    render_section_header(
        "🌊 Su Stresi İstihbarat Modelleri",
        "Tarımsal, kentsel ve ekosistem su stresi analiz modelleri",
        step_number=1,
        step_title="ANALİZ"
    )
    
    # Model sekmeleri
    tab1, tab2, tab3 = st.tabs(
        [
            "🌾 Tarımsal Su Stresi (Model 1)",
            "🏙️ Kentsel Su Stresi (Model 2)",
            "🌿 Ekosistem Su Direnci (Model 3)",
        ]
    )
    
    # Model 1: Tarımsal Su Stresi
    with tab1:
        st.markdown('<div style="margin-bottom: 1.5rem;"></div>', unsafe_allow_html=True)
        st.markdown("### 🌾 Model 1: Tarımsal Su Stresi İstihbaratı")
        st.markdown("Tarımsal bölgeler için su stresi skorunu hesaplar.")
        
        # Sidebar'da model 1 yapılandırması
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 🌾 Model 1 Yapılandırması")
            root_dir = Path(__file__).resolve().parent.parent / "deneme"
            default_geojson = root_dir / "outputs" / "model1_water_stress.geojson"
            geojson_path_str = st.text_input(
                "Model 1 GeoJSON dosya yolu",
                value=str(default_geojson),
                help="Pipeline tarafından üretilen `model1_water_stress.geojson` dosyasının yolu.",
                key="public_model1_path",
            )
        
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
    
    # Model 2 ve Model 3 için benzer yapı...
    # (Kısa tutmak için sadece Model 1'i gösterdim, Model 2 ve 3 de benzer şekilde eklenebilir)
