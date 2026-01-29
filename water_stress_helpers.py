from pathlib import Path
from typing import Dict, List

import geopandas as gpd
import numpy as np
import pandas as pd
import streamlit as st
import folium
from branca.colormap import LinearColormap
from streamlit_folium import st_folium


st.set_page_config(
    page_title="Water Stress Intelligence Dashboard",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def load_model1_results(geojson_path: str) -> gpd.GeoDataFrame:
    """Load Model 1 GeoJSON output as a GeoDataFrame, in WGS84 for web mapping."""
    path = Path(geojson_path)
    if not path.exists():
        raise FileNotFoundError(f"GeoJSON file not found at: {path}")

    gdf = gpd.read_file(path)
    # Ensure WGS84 for web mapping
    if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    return gdf


@st.cache_data(show_spinner=False)
def load_model2_results(geojson_path: str) -> gpd.GeoDataFrame:
    """Load Model 2 GeoJSON output as a GeoDataFrame, in WGS84 for web mapping."""
    path = Path(geojson_path)
    if not path.exists():
        raise FileNotFoundError(f"GeoJSON file not found at: {path}")

    gdf = gpd.read_file(path)
    # Ensure WGS84 for web mapping
    if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    
    # Convert all datetime/timestamp columns to strings for JSON serialization
    gdf = gdf.copy()
    for col in gdf.columns:
        if col != 'geometry':
            # Check if column is datetime/timestamp type
            if pd.api.types.is_datetime64_any_dtype(gdf[col]):
                gdf[col] = gdf[col].astype(str)
            elif gdf[col].dtype == 'object':
                # Check for datetime objects in object columns
                sample = gdf[col].dropna().head(5)
                if len(sample) > 0 and isinstance(sample.iloc[0], (pd.Timestamp, pd.DatetimeTZDtype)):
                    gdf[col] = gdf[col].astype(str)
    
    # Fix invalid geometries
    invalid_count = (~gdf.geometry.is_valid).sum()
    if invalid_count > 0:
        # Try to fix invalid geometries using buffer(0) trick
        gdf.loc[~gdf.geometry.is_valid, 'geometry'] = gdf.loc[~gdf.geometry.is_valid, 'geometry'].buffer(0)
        # Remove any geometries that are still invalid or empty
        gdf = gdf[gdf.geometry.is_valid & ~gdf.geometry.is_empty].copy()
    
    return gdf


@st.cache_data(show_spinner=False)
def load_model3_results(geojson_path: str) -> gpd.GeoDataFrame:
    """Load Model 3 GeoJSON output as a GeoDataFrame, in WGS84 for web mapping."""
    path = Path(geojson_path)
    if not path.exists():
        raise FileNotFoundError(f"GeoJSON file not found at: {path}")

    gdf = gpd.read_file(path)
    # Ensure WGS84 for web mapping
    if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    
    # Convert all datetime/timestamp columns to strings for JSON serialization
    gdf = gdf.copy()
    for col in gdf.columns:
        if col != 'geometry':
            # Check if column is datetime/timestamp type
            if pd.api.types.is_datetime64_any_dtype(gdf[col]):
                gdf[col] = gdf[col].astype(str)
            elif gdf[col].dtype == 'object':
                # Check for datetime objects in object columns
                sample = gdf[col].dropna().head(5)
                if len(sample) > 0:
                    first_val = sample.iloc[0]
                    if isinstance(first_val, (pd.Timestamp, pd.DatetimeTZDtype)) or 'timestamp' in str(type(first_val)).lower():
                        gdf[col] = gdf[col].astype(str)
    
    # Fix invalid geometries
    invalid_count = (~gdf.geometry.is_valid).sum()
    if invalid_count > 0:
        # Try to fix invalid geometries using buffer(0) trick
        gdf.loc[~gdf.geometry.is_valid, 'geometry'] = gdf.loc[~gdf.geometry.is_valid, 'geometry'].buffer(0)
        # Remove any geometries that are still invalid or empty
        gdf = gdf[gdf.geometry.is_valid & ~gdf.geometry.is_empty].copy()
    
    return gdf


def make_water_stress_map(gdf: gpd.GeoDataFrame) -> folium.Map:
    """Create a Folium map colored by final_water_stress_score."""
    score_col = "final_water_stress_score"
    if score_col not in gdf.columns:
        raise KeyError(f"Expected column '{score_col}' in GeoDataFrame.")

    # Compute map center
    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles="cartodbpositron")

    # Color scale: green (low) → yellow → red (high)
    vmin = float(gdf[score_col].min())
    vmax = float(gdf[score_col].max())
    if vmin == vmax:
        # Avoid zero-range scale; expand slightly
        vmin = vmin - 0.001
        vmax = vmax + 0.001

    colormap = LinearColormap(
        colors=["green", "yellow", "red"],
        vmin=vmin,
        vmax=vmax,
    )
    colormap.caption = "Final Water Stress Score"
    colormap.add_to(m)

    # Fields to show on hover
    hover_fields = [
        "drought_norm",
        "groundwater_norm",
        "agricultural_area_pressure",
        "final_water_stress_score",
    ]
    existing_hover_fields = [f for f in hover_fields if f in gdf.columns]

    def style_function(feature):
        score = feature["properties"].get(score_col, 0)
        return {
            "fillColor": colormap(score),
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.7,
        }

    tooltip = folium.GeoJsonTooltip(
        fields=existing_hover_fields,
        aliases=[
            "Drought (norm):",
            "Groundwater (norm):",
            "Area pressure:",
            "Final water stress:",
        ][: len(existing_hover_fields)],
        localize=True,
        sticky=True,
    )

    folium.GeoJson(
        gdf,
        style_function=style_function,
        tooltip=tooltip,
        name="Water Stress",
    ).add_to(m)

    folium.LayerControl().add_to(m)

    return m


def make_urban_water_stress_map(gdf: gpd.GeoDataFrame) -> folium.Map:
    """Create a Folium map colored by urban_water_stress_score."""
    score_col = "urban_water_stress_score"
    if score_col not in gdf.columns:
        raise KeyError(f"Expected column '{score_col}' in GeoDataFrame.")

    # Convert all datetime/timestamp columns to strings for JSON serialization
    # This is critical for folium.GeoJson to work properly
    gdf = gdf.copy()
    for col in gdf.columns:
        if col != 'geometry':
            # Check if column is datetime/timestamp type
            if pd.api.types.is_datetime64_any_dtype(gdf[col]):
                gdf[col] = gdf[col].astype(str)
            elif gdf[col].dtype == 'object':
                # Check for datetime objects in object columns
                sample = gdf[col].dropna().head(5)
                if len(sample) > 0:
                    first_val = sample.iloc[0]
                    if isinstance(first_val, (pd.Timestamp, pd.DatetimeTZDtype)) or 'timestamp' in str(type(first_val)).lower():
                        gdf[col] = gdf[col].astype(str)

    # Compute map center
    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles="cartodbpositron")

    # Color scale: green (low) → yellow → red (high)
    vmin = float(gdf[score_col].min())
    vmax = float(gdf[score_col].max())
    all_zero = (vmin == 0 and vmax == 0)
    
    if vmin == vmax:
        # Avoid zero-range scale; expand slightly
        if all_zero:
            # If all values are 0, use a small range to show gray/uncolored
            vmin = -0.001
            vmax = 0.001
        else:
            vmin = vmin - 0.001
            vmax = vmax + 0.001

    colormap = LinearColormap(
        colors=["green", "yellow", "red"],
        vmin=vmin,
        vmax=vmax,
    )
    colormap.caption = "Urban Water Stress Score"
    colormap.add_to(m)

    # Fields to show on hover
    # Try to find city name column (common names)
    city_name_col = None
    for col_name in ["name", "city_name", "city", "NAME", "CITY_NAME", "CITY", "kentAtlasiDegeri"]:
        if col_name in gdf.columns:
            city_name_col = col_name
            break

    hover_fields = []
    hover_aliases = []

    if city_name_col:
        hover_fields.append(city_name_col)
        hover_aliases.append("City:")

    hover_fields.extend([
        "total_population",
        "estimated_water_supply",
        "urban_water_stress_score",
    ])
    hover_aliases.extend([
        "Population:",
        "Water Supply:",
        "Water Stress Score:",
    ])

    existing_hover_fields = [f for f in hover_fields if f in gdf.columns]
    existing_aliases = hover_aliases[: len(existing_hover_fields)]

    # Capture all_zero in closure
    all_zero_flag = all_zero
    
    def style_function(feature):
        score = feature["properties"].get(score_col, 0)
        # Handle zero scores - show in light gray
        if all_zero_flag or score == 0 or pd.isna(score):
            return {
                "fillColor": "#cccccc",  # Light gray for zero/no data
                "color": "black",
                "weight": 0.5,
                "fillOpacity": 0.5,
            }
        return {
            "fillColor": colormap(score),
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.7,
        }

    tooltip = folium.GeoJsonTooltip(
        fields=existing_hover_fields,
        aliases=existing_aliases,
        localize=True,
        sticky=True,
    )

    folium.GeoJson(
        gdf,
        style_function=style_function,
        tooltip=tooltip,
        name="Urban Water Stress",
    ).add_to(m)

    folium.LayerControl().add_to(m)

    return m


def make_ecosystem_resilience_map(gdf: gpd.GeoDataFrame) -> folium.Map:
    """Create a Folium map colored by ecosystem_water_sensitivity_score."""
    score_col = "ecosystem_water_sensitivity_score"
    if score_col not in gdf.columns:
        raise KeyError(f"Expected column '{score_col}' in GeoDataFrame.")

    # Compute map center
    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
    center_lat = (bounds[1] + bounds[3]) / 2
    center_lon = (bounds[0] + bounds[2]) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles="cartodbpositron")

    # Color scale: green (low vulnerability) → yellow → red (high vulnerability)
    vmin = float(gdf[score_col].min())
    vmax = float(gdf[score_col].max())
    
    if vmin == vmax:
        # Avoid zero-range scale; expand slightly
        vmin = vmin - 0.001
        vmax = vmax + 0.001

    colormap = LinearColormap(
        colors=["green", "yellow", "red"],
        vmin=vmin,
        vmax=vmax,
    )
    colormap.caption = "Ekosistem Su Hassasiyeti Skoru"
    colormap.add_to(m)

    # Fields to show on hover
    ecosystem_name_col = None
    for col_name in ["ka_adi", "name", "ecosystem_name", "NAME"]:
        if col_name in gdf.columns:
            ecosystem_name_col = col_name
            break

    hover_fields = []
    hover_aliases = []

    if ecosystem_name_col:
        hover_fields.append(ecosystem_name_col)
        hover_aliases.append("Ekosistem:")

    hover_fields.extend([
        "ecosystem_type",
        "drought_norm",
        "groundwater_sensitivity_norm",
        "wetland_proximity_risk_norm",
        "protected_area_importance_norm",
        "ecosystem_water_sensitivity_score",
    ])
    hover_aliases.extend([
        "Tip:",
        "Kuraklık (norm):",
        "Yeraltı Suyu (norm):",
        "Sulak Alan Riski (norm):",
        "Önem (norm):",
        "Hassasiyet Skoru:",
    ])

    existing_hover_fields = [f for f in hover_fields if f in gdf.columns]
    existing_aliases = hover_aliases[: len(existing_hover_fields)]

    def style_function(feature):
        score = feature["properties"].get(score_col, 0)
        return {
            "fillColor": colormap(score),
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.7,
        }

    tooltip = folium.GeoJsonTooltip(
        fields=existing_hover_fields,
        aliases=existing_aliases,
        localize=True,
        sticky=True,
    )

    folium.GeoJson(
        gdf,
        style_function=style_function,
        tooltip=tooltip,
        name="Ecosystem Water Sensitivity",
    ).add_to(m)

    folium.LayerControl().add_to(m)

    return m


def _compute_automated_insights(
    gdf: gpd.GeoDataFrame, score_col: str = "final_water_stress_score"
) -> Dict[str, object]:
    """
    Derive automated insights from the Model 1 output.

    Risk bands (by zone count, not area-weighted):
    - High risk: top 5% of scores
    - Medium risk: 40–70th percentile band
    - Low risk: below 40th percentile
    """
    if score_col not in gdf.columns or gdf.empty:
        return {
            "high_risk_share_pct": 0.0,
            "medium_risk_share_pct": 0.0,
            "low_risk_share_pct": 0.0,
            "cluster_insights": [],
            "recommended_actions": [],
        }

    scores = pd.to_numeric(gdf[score_col], errors="coerce").dropna()
    if scores.empty:
        return {
            "high_risk_share_pct": 0.0,
            "medium_risk_share_pct": 0.0,
            "low_risk_share_pct": 0.0,
            "cluster_insights": [],
            "recommended_actions": [],
        }

    n_total = len(scores)
    p95 = float(scores.quantile(0.95))
    p40 = float(scores.quantile(0.40))
    p70 = float(scores.quantile(0.70))

    high_mask = gdf[score_col] >= p95
    medium_mask = (gdf[score_col] >= p40) & (gdf[score_col] <= p70)
    low_mask = gdf[score_col] < p40

    n_high = int(high_mask.sum())
    n_medium = int(medium_mask.sum())
    n_low = int(low_mask.sum())

    high_share = (n_high / n_total) * 100 if n_total else 0.0
    medium_share = (n_medium / n_total) * 100 if n_total else 0.0
    low_share = (n_low / n_total) * 100 if n_total else 0.0

    # Spatial clustering: compare high-risk centroid to overall centroid
    cluster_insights: List[str] = []
    if n_high > 0 and gdf.geometry.notna().any():
        overall_bounds = gdf.total_bounds  # minx, miny, maxx, maxy
        overall_center_lat = (overall_bounds[1] + overall_bounds[3]) / 2
        overall_center_lon = (overall_bounds[0] + overall_bounds[2]) / 2

        high_gdf = gdf.loc[high_mask].copy()
        # Assume already in WGS84; centroids are approximate but good enough for narrative
        high_centroid = high_gdf.geometry.centroid
        high_center_lat = float(high_centroid.y.mean())
        high_center_lon = float(high_centroid.x.mean())

        lat_desc = "central"
        lon_desc = "central"
        lat_delta = high_center_lat - overall_center_lat
        lon_delta = high_center_lon - overall_center_lon

        # Simple directional description with a small tolerance
        tol = 0.1 * max(
            abs(overall_bounds[3] - overall_bounds[1]),
            abs(overall_bounds[2] - overall_bounds[0]),
        )

        if lat_delta > tol:
            lat_desc = "kuzey"
        elif lat_delta < -tol:
            lat_desc = "güney"
        else:
            lat_desc = "merkez"

        if lon_delta > tol:
            lon_desc = "doğu"
        elif lon_delta < -tol:
            lon_desc = "batı"
        else:
            lon_desc = "merkez"

        # Assess how compact the high-risk cluster is
        high_bounds = high_gdf.total_bounds
        lat_span_ratio = abs(high_bounds[3] - high_bounds[1]) / max(
            1e-9, abs(overall_bounds[3] - overall_bounds[1])
        )
        lon_span_ratio = abs(high_bounds[2] - high_bounds[0]) / max(
            1e-9, abs(overall_bounds[2] - overall_bounds[0])
        )

        if lat_span_ratio < 0.5 and lon_span_ratio < 0.5:
            part = f"{lat_desc}-{lon_desc}" if (lat_desc != "merkez" or lon_desc != "merkez") else "merkez"
            cluster_insights.append(
                f"Yüksek su stresi bölgeleri, çalışma alanının **{part}** "
                "kesiminde belirgin biçimde kümelenmiştir."
            )
        else:
            cluster_insights.append(
                "Yüksek su stresi bölgeleri tek bir baskın küme oluşturmadan tüm bölgeye yayılmıştır; "
                "yaygın kırılganlık göstergesidir."
            )

    # Önerilen eylemler (risk dilimlerine göre)
    recommended_actions: List[str] = []
    if high_share >= 5:
        recommended_actions.append(
            "Yüksek stres bölgelerinde **su tasarruflu sulama yatırımlarını** önceliklendirin: "
            "damla sulama, iyileştirilmiş sulama programları."
        )
        recommended_actions.append(
            "**Kuraklık eylem planları** hazırlayın ve en riskli bölgelerdeki (üst %5) "
            "çiftçilere hedefli destek sağlayın."
        )
    if medium_share >= 20:
        recommended_actions.append(
            "Orta risk bölgelerinde **önce önlem** uygulayın: toprak nemi izleme, malçlama, "
            "kısıntılı sulama stratejileri."
        )
    if low_share > 50:
        recommended_actions.append(
            "Düşük risk bölgelerinde mevcut uygulamaları sürdürün; ortaya çıkan kuraklık "
            "sinyallerini izleyerek riskin tırmanmasını engelleyin."
        )
    if not recommended_actions:
        recommended_actions.append(
            "Genel su stresi nispeten düşüktür; izleme sistemlerini korumaya ve seçili "
            "alanlarda su verimli teknolojileri denemeye odaklanın."
        )

    return {
        "high_risk_share_pct": high_share,
        "medium_risk_share_pct": medium_share,
        "low_risk_share_pct": low_share,
        "cluster_insights": cluster_insights,
        "recommended_actions": recommended_actions,
    }


def _compute_score_decomposition(
    gdf: gpd.GeoDataFrame, top_n: int = 5
) -> pd.DataFrame:
    """
    Decompose final_water_stress_score into percentage contributions for top N zones.

    The score formula is:
        score = (0.45 * drought_norm) + (0.35 * groundwater_norm) + (0.20 * agricultural_area_pressure)

    For each zone, compute the percentage contribution of each component to the final score.
    """
    required_cols = [
        "final_water_stress_score",
        "drought_norm",
        "groundwater_norm",
        "agricultural_area_pressure",
    ]
    missing = [c for c in required_cols if c not in gdf.columns]
    if missing:
        return pd.DataFrame()

    # Get top N highest-risk zones
    top_zones = gdf.nlargest(top_n, "final_water_stress_score").copy()

    # Extract component values
    drought_vals = pd.to_numeric(top_zones["drought_norm"], errors="coerce").fillna(0.0)
    groundwater_vals = pd.to_numeric(
        top_zones["groundwater_norm"], errors="coerce"
    ).fillna(0.0)
    area_vals = pd.to_numeric(
        top_zones["agricultural_area_pressure"], errors="coerce"
    ).fillna(0.0)
    final_scores = pd.to_numeric(
        top_zones["final_water_stress_score"], errors="coerce"
    ).fillna(0.0)

    # Compute weighted contributions
    # Score = 0.45 * drought + 0.35 * groundwater + 0.20 * area
    drought_contribution = 0.45 * drought_vals
    groundwater_contribution = 0.35 * groundwater_vals
    area_contribution = 0.20 * area_vals

    # Compute percentage contributions (avoid division by zero)
    total_contribution = drought_contribution + groundwater_contribution + area_contribution
    epsilon = 1e-10
    drought_pct = (drought_contribution / (total_contribution + epsilon)) * 100
    groundwater_pct = (groundwater_contribution / (total_contribution + epsilon)) * 100
    area_pct = (area_contribution / (total_contribution + epsilon)) * 100

    # Determine dominant risk factor
    contributions_df = pd.DataFrame(
        {
            "drought_pct": drought_pct,
            "groundwater_pct": groundwater_pct,
            "area_pct": area_pct,
        }
    )
    dominant_factors = []
    for idx in contributions_df.index:
        row = contributions_df.loc[idx]
        max_col = row.idxmax()
        if max_col == "drought_pct":
            dominant_factors.append("Drought")
        elif max_col == "groundwater_pct":
            dominant_factors.append("Groundwater")
        else:
            dominant_factors.append("Area Pressure")

    # Build result DataFrame
    result = pd.DataFrame(
        {
            "zone_index": top_zones.index,
            "final_water_stress_score": final_scores.values,
            "drought_contribution_pct": drought_pct.values,
            "groundwater_contribution_pct": groundwater_pct.values,
            "area_contribution_pct": area_pct.values,
            "dominant_risk_factor": dominant_factors,
        }
    )

    return result


def _generate_explainability_summary(decomp_df: pd.DataFrame) -> str:
    """Generate a narrative summary of the score decomposition."""
    if decomp_df.empty:
        return "No data available for explainability analysis."

    # Count dominant factors
    factor_counts = decomp_df["dominant_risk_factor"].value_counts()
    total_zones = len(decomp_df)

    # Determine primary driver
    primary_factor = factor_counts.index[0] if len(factor_counts) > 0 else None
    primary_count = factor_counts.iloc[0] if len(factor_counts) > 0 else 0
    primary_pct = (primary_count / total_zones) * 100 if total_zones > 0 else 0

    # Compute average contributions
    avg_drought = decomp_df["drought_contribution_pct"].mean()
    avg_groundwater = decomp_df["groundwater_contribution_pct"].mean()
    avg_area = decomp_df["area_contribution_pct"].mean()

    summary_parts = []

    if primary_factor and primary_pct >= 60:
        summary_parts.append(
            f"Most high-risk zones ({primary_pct:.0f}%) are primarily driven by "
            f"**{primary_factor.lower()} pressure**."
        )
    elif primary_factor:
        summary_parts.append(
            f"The dominant risk factor varies across zones, with "
            f"**{primary_factor.lower()}** being the primary driver in "
            f"{primary_pct:.0f}% of the top 5 highest-risk zones."
        )

    summary_parts.append(
        f"On average, the final water stress score is composed of "
        f"{avg_drought:.1f}% drought contribution, "
        f"{avg_groundwater:.1f}% groundwater sensitivity contribution, and "
        f"{avg_area:.1f}% agricultural area pressure contribution."
    )

    return " ".join(summary_parts)


def render_model1_tab() -> None:
    """Render the Model 1 (Agricultural Water Stress) tab."""
    st.header("Model 1: Agricultural Water Stress Intelligence")
    st.markdown(
        "Visual decision-support dashboard for **Agricultural Water Stress Intelligence** "
        "(Model 1)."
    )

    # ---- Sidebar configuration ----
    root_dir = Path(__file__).resolve().parents[1]
    default_geojson = root_dir / "outputs" / "model1_water_stress.geojson"

    st.sidebar.header("Model 1 Configuration")
    geojson_path_str = st.sidebar.text_input(
        "Model 1 GeoJSON path",
        value=str(default_geojson),
        help="Path to `model1_water_stress.geojson` produced by the pipeline.",
        key="model1_path",
    )

    # ---- Load data ----
    try:
        gdf = load_model1_results(geojson_path_str)
    except FileNotFoundError as e:
        st.error(str(e))
        st.info("Run Model 1 first to generate the GeoJSON output.")
        return
    except Exception as e:
        st.error(f"Failed to load GeoJSON: {e}")
        return

    if gdf.empty:
        st.warning("The loaded GeoJSON contains no features.")
        return

    score_col = "final_water_stress_score"
    if score_col not in gdf.columns:
        st.error(f"Expected column '{score_col}' not found in data.")
        return

    # ---- Layout: Map + Top 10 table ----
    map_col, table_col = st.columns((2, 1))

    with map_col:
        st.subheader("Water Stress Map")
        m = make_water_stress_map(gdf)
        st_folium(m, width="100%", height=600)

    with table_col:
        st.subheader("Top 10 Highest-Risk Agricultural Zones")
        top10 = (
            gdf[
                [
                    score_col,
                    "drought_norm",
                    "groundwater_norm",
                    "agricultural_area_pressure",
                ]
            ]
            .copy()
        )
        top10 = top10.sort_values(score_col, ascending=False).head(10)
        if "geometry" in top10.columns:
            top10 = pd.DataFrame(top10.drop(columns="geometry"))
        st.dataframe(top10.reset_index(drop=True), use_container_width=True)

    # ---- Automated insights panel ----
    st.markdown("---")
    st.subheader("Automated Insights")

    insights = _compute_automated_insights(gdf, score_col=score_col)

    st.markdown(
        f"**Share of zones under high water stress (top 5%):** "
        f"{insights['high_risk_share_pct']:.1f}%"
    )
    st.markdown(
        f"**Share of zones in medium risk band (40–70th percentile):** "
        f"{insights['medium_risk_share_pct']:.1f}%"
    )
    st.markdown(
        f"**Share of zones in low risk band:** "
        f"{insights['low_risk_share_pct']:.1f}%"
    )

    cluster_insights = insights.get("cluster_insights") or []
    if cluster_insights:
        st.markdown("**Spatial patterns of risk:**")
        for line in cluster_insights:
            st.markdown(f"- {line}")

    recommended_actions = insights.get("recommended_actions") or []
    if recommended_actions:
        st.markdown("**Recommended actions:**")
        for action in recommended_actions:
            st.markdown(f"- {action}")

    # ---- Explainability section ----
    st.markdown("---")
    st.subheader("Explainability: Score Decomposition")

    st.markdown(
        "This section decomposes the **final water stress score** for the top 5 highest-risk "
        "agricultural zones, showing the percentage contribution of each component factor. "
        "The score formula is: "
        "`final_score = (0.45 × drought_norm) + (0.35 × groundwater_norm) + "
        "(0.20 × agricultural_area_pressure)`."
    )

    decomp_df = _compute_score_decomposition(gdf, top_n=5)

    if decomp_df.empty:
        st.warning(
            "Unable to compute score decomposition. Ensure the GeoDataFrame contains "
            "columns: 'final_water_stress_score', 'drought_norm', 'groundwater_norm', "
            "and 'agricultural_area_pressure'."
        )
    else:
        # Display decomposition table
        display_cols = [
            "zone_index",
            "final_water_stress_score",
            "drought_contribution_pct",
            "groundwater_contribution_pct",
            "area_contribution_pct",
            "dominant_risk_factor",
        ]
        display_df = decomp_df[display_cols].copy()
        display_df = display_df.rename(
            columns={
                "zone_index": "Zone ID",
                "final_water_stress_score": "Final Score",
                "drought_contribution_pct": "Drought %",
                "groundwater_contribution_pct": "Groundwater %",
                "area_contribution_pct": "Area Pressure %",
                "dominant_risk_factor": "Dominant Factor",
            }
        )
        # Format percentages
        display_df["Drought %"] = display_df["Drought %"].apply(lambda x: f"{x:.1f}%")
        display_df["Groundwater %"] = display_df["Groundwater %"].apply(
            lambda x: f"{x:.1f}%"
        )
        display_df["Area Pressure %"] = display_df["Area Pressure %"].apply(
            lambda x: f"{x:.1f}%"
        )
        display_df["Final Score"] = display_df["Final Score"].apply(
            lambda x: f"{x:.3f}"
        )

        st.dataframe(display_df.reset_index(drop=True), use_container_width=True)

        # Generate and display narrative summary
        summary = _generate_explainability_summary(decomp_df)
        st.markdown("**Summary:**")
        st.info(summary)


def _compute_urban_insights(
    gdf: gpd.GeoDataFrame, score_col: str = "urban_water_stress_score"
) -> Dict[str, object]:
    """
    Derive automated insights from the Model 2 output.

    Risk bands:
    - High risk: top 20% of scores
    - Medium risk: 40–80th percentile band
    - Low risk: bottom 40%
    """
    if score_col not in gdf.columns or gdf.empty:
        return {
            "high_risk_share_pct": 0.0,
            "medium_risk_share_pct": 0.0,
            "low_risk_share_pct": 0.0,
            "pattern_insights": [],
            "recommended_actions": [],
        }

    scores = pd.to_numeric(gdf[score_col], errors="coerce").dropna()
    if scores.empty:
        return {
            "high_risk_share_pct": 0.0,
            "medium_risk_share_pct": 0.0,
            "low_risk_share_pct": 0.0,
            "pattern_insights": [],
            "recommended_actions": [],
        }

    n_total = len(scores)
    p80 = float(scores.quantile(0.80))  # Top 20%
    p40 = float(scores.quantile(0.40))  # Bottom 40% threshold

    high_mask = gdf[score_col] >= p80
    medium_mask = (gdf[score_col] >= p40) & (gdf[score_col] < p80)
    low_mask = gdf[score_col] < p40

    n_high = int(high_mask.sum())
    n_medium = int(medium_mask.sum())
    n_low = int(low_mask.sum())

    high_share = (n_high / n_total) * 100 if n_total else 0.0
    medium_share = (n_medium / n_total) * 100 if n_total else 0.0
    low_share = (n_low / n_total) * 100 if n_total else 0.0

    # Pattern detection: analyze drivers of high risk
    pattern_insights: List[str] = []

    if n_high > 0:
        high_risk_cities = gdf.loc[high_mask].copy()
        all_cities = gdf.copy()

        # Check if high-risk cities are primarily large-population cities
        if "total_population" in gdf.columns:
            high_pop = pd.to_numeric(
                high_risk_cities["total_population"], errors="coerce"
            ).fillna(0.0)
            all_pop = pd.to_numeric(
                all_cities["total_population"], errors="coerce"
            ).fillna(0.0)

            median_pop_all = all_pop.median()
            median_pop_high = high_pop.median()

            if median_pop_high > median_pop_all * 1.5:
                pattern_insights.append(
                    "Yüksek riskli kentler **ağırlıklı olarak büyük nüfuslu kentlerdir**; "
                    f"medyan nüfus {median_pop_high:,.0f}, tüm kentlerde {median_pop_all:,.0f}."
                )
            elif median_pop_high < median_pop_all * 0.7:
                pattern_insights.append(
                    "Yüksek riskli kentler arasında **küçük kentler** fazladır; "
                    "nüfus baskısından çok **su arzı kısıtları** etkilidir."
                )

        # Analyze correlation: population pressure vs water supply
        if "total_population" in gdf.columns and "estimated_water_supply" in gdf.columns:
            high_pop = pd.to_numeric(
                high_risk_cities["total_population"], errors="coerce"
            ).fillna(0.0)
            high_supply = pd.to_numeric(
                high_risk_cities["estimated_water_supply"], errors="coerce"
            ).fillna(0.0)

            all_pop = pd.to_numeric(
                all_cities["total_population"], errors="coerce"
            ).fillna(0.0)
            all_supply = pd.to_numeric(
                all_cities["estimated_water_supply"], errors="coerce"
            ).fillna(0.0)

            # Normalize for comparison
            max_pop = all_pop.max()
            max_supply = all_supply.max()

            if max_pop > 0 and max_supply > 0:
                high_pop_norm = high_pop / max_pop
                high_supply_norm = high_supply / max_supply

                # Compare medians
                median_pop_norm_high = high_pop_norm.median()
                median_supply_norm_high = high_supply_norm.median()

                if median_pop_norm_high > median_supply_norm_high * 1.3:
                    pattern_insights.append(
                        "Yüksek riskli kentlerde **nüfus baskısı** düşük su kullanılabilirliğinden "
                        "daha baskındır; talep tarafı zorlukları söz konusudur."
                    )
                elif median_supply_norm_high < median_pop_norm_high * 0.7:
                    pattern_insights.append(
                        "Yüksek riskli kentlerde **düşük su arzı** nüfus baskısından daha "
                        "baskındır; arz tarafı kısıtları öne çıkmaktadır."
                    )
                else:
                    pattern_insights.append(
                        "Yüksek riskli kentlerde **nüfus baskısı** ile **su arzı kısıtları** "
                        "dengeli bir bileşim göstermektedir."
                    )

    # Önerilen eylemler (desenlere ve risk dağılımına göre)
    recommended_actions: List[str] = []

    if high_share >= 15:
        if pattern_insights and any(
            "nüfus baskısı" in insight.lower() for insight in pattern_insights
        ):
            recommended_actions.append(
                "Büyük kentlerde **talep yönetimi**: Su tasarrufu programları, kaçak azaltma, "
                "kademeli tarifelerle kişi başı tüketimi düşürün."
            )
            recommended_actions.append(
                "**Su verimli altyapı**: Yüksek nüfuslu stres bölgelerinde akıllı sayaçlar, "
                "gri su geri kazanımı ve yağmur suyu hasadı ile kentsel su sistemlerini iyileştirin."
            )
        elif pattern_insights and any(
            "düşük su arzı" in insight.lower() or "su arzı kısıt" in insight.lower()
            for insight in pattern_insights
        ):
            recommended_actions.append(
                "Arzı kısıtlı kentlerde **altyapı yatırımı**: Yeni su kaynakları, rezervuar "
                "kapasitesi artışı ve dağıtım şebekelerinin iyileştirilmesiyle arz güvenilirliğini artırın."
            )
            recommended_actions.append(
                "**Kaynak çeşitlendirme**: Arzı kısıtlı kentlerde yeraltı suyu geliştirme, "
                "tuzdan arındırma ve havzalar arası transfer seçeneklerini değerlendirin."
            )
        else:
            recommended_actions.append(
                "**Entegre su kaynakları yönetimi**: Hem talep hem arzı tasarruf önlemleri "
                "ve altyapı yatırımları ile birlikte ele alın."
            )

    if medium_share >= 30:
        recommended_actions.append(
            "Orta riskli kentlerde **önleyici önlemler**: Erken uyarı sistemleri, kuraklık "
            "eylem planları ve su verimliliği pilotları ile yüksek riske tırmanmayı engelleyin."
        )

    if low_share > 50:
        recommended_actions.append(
            "Düşük riskli kentlerde **dayanıklılığı koruyun**: İzlemeye devam edin, altyapıyı "
            "koruyun; nüfus artışı ve iklim değişkenliğine hazırlık yapın."
        )

    if not recommended_actions:
        recommended_actions.append(
            "Genel kentsel su stresi nispeten düşüktür; kentler büyürken su güvenliğini "
            "sürdürmek için **izleme sistemleri** ve **uzun vadeli planlama**ya odaklanın."
        )

    return {
        "high_risk_share_pct": high_share,
        "medium_risk_share_pct": medium_share,
        "low_risk_share_pct": low_share,
        "pattern_insights": pattern_insights,
        "recommended_actions": recommended_actions,
    }


def _compute_ecosystem_insights(
    gdf: gpd.GeoDataFrame, score_col: str = "ecosystem_water_sensitivity_score"
) -> Dict[str, object]:
    """
    Derive automated insights from the Model 3 output.

    Risk bands:
    - High risk: top 20% of scores (≥80th percentile)
    - Medium risk: 40–80th percentile band
    - Low risk: bottom 40%
    """
    if score_col not in gdf.columns or gdf.empty:
        return {
            "high_risk_share_pct": 0.0,
            "medium_risk_share_pct": 0.0,
            "low_risk_share_pct": 0.0,
            "pattern_insights": [],
            "recommended_actions": [],
        }

    scores = pd.to_numeric(gdf[score_col], errors="coerce").dropna()
    if scores.empty:
        return {
            "high_risk_share_pct": 0.0,
            "medium_risk_share_pct": 0.0,
            "low_risk_share_pct": 0.0,
            "pattern_insights": [],
            "recommended_actions": [],
        }

    n_total = len(scores)
    p80 = float(scores.quantile(0.80))  # Top 20%
    p40 = float(scores.quantile(0.40))  # Bottom 40% threshold

    high_mask = gdf[score_col] >= p80
    medium_mask = (gdf[score_col] >= p40) & (gdf[score_col] < p80)
    low_mask = gdf[score_col] < p40

    n_high = int(high_mask.sum())
    n_medium = int(medium_mask.sum())
    n_low = int(low_mask.sum())

    high_share = (n_high / n_total) * 100 if n_total else 0.0
    medium_share = (n_medium / n_total) * 100 if n_total else 0.0
    low_share = (n_low / n_total) * 100 if n_total else 0.0

    # Pattern detection: analyze drivers of high risk
    pattern_insights: List[str] = []

    if n_high > 0:
        high_risk_ecosystems = gdf.loc[high_mask].copy()
        all_ecosystems = gdf.copy()

        # Analyze component contributions
        component_cols = [
            "drought_norm",
            "groundwater_sensitivity_norm",
            "wetland_proximity_risk_norm",
            "protected_area_importance_norm",
        ]

        _col_names_tr = {
            "drought_norm": "Kuraklık",
            "groundwater_sensitivity_norm": "Yeraltı suyu hassasiyeti",
            "wetland_proximity_risk_norm": "Sulak alan yakınlık riski",
            "protected_area_importance_norm": "Korunan alan önemi",
        }
        for col in component_cols:
            if col in gdf.columns:
                high_vals = pd.to_numeric(
                    high_risk_ecosystems[col], errors="coerce"
                ).fillna(0.0)
                all_vals = pd.to_numeric(
                    all_ecosystems[col], errors="coerce"
                ).fillna(0.0)

                mean_high = high_vals.mean()
                mean_all = all_vals.mean()

                if mean_high > mean_all * 1.2:
                    col_name = _col_names_tr.get(
                        col, col.replace("_norm", "").replace("_", " ").title()
                    )
                    pattern_insights.append(
                        f"Yüksek riskli ekosistemlerde **{col_name}** belirgin "
                        f"({mean_high:.3f} vs ortalama {mean_all:.3f}); bu faktör "
                        "kırılganlığın önemli bir sürücüsüdür."
                    )

    # Önerilen eylemler
    recommended_actions: List[str] = []

    if high_share >= 15:
        recommended_actions.append(
            "Yüksek riskli ekosistemlerde **acil müdahale** gerekir: Yeraltı suyu koruma "
            "zonları, kuraklık eylem planları ve geliştirilmiş izleme sistemleri uygulayın."
        )

    if medium_share >= 40:
        recommended_actions.append(
            "Orta riskli ekosistemlerde **önleyici dayanıklılık artırımı**: Yüksek riske "
            "geçişi engellemek için erken müdahale önlemlerini hayata geçirin."
        )

    if not recommended_actions:
        recommended_actions.append(
            "Genel ekosistem su direnci nispeten iyidir; iklim değişikliği altında dayanıklılığı "
            "korumak için **izleme sistemleri** ve **önleyici önlemlere** odaklanın."
        )

    return {
        "high_risk_share_pct": high_share,
        "medium_risk_share_pct": medium_share,
        "low_risk_share_pct": low_share,
        "pattern_insights": pattern_insights,
        "recommended_actions": recommended_actions,
    }


def render_model2_tab() -> None:
    """Render the Model 2 (Urban Water Stress) tab."""
    st.header("Model 2: Urban Water Stress Intelligence")
    st.markdown(
        "Visual decision-support dashboard for **Urban Water Stress Intelligence** "
        "(Model 2) - City-level water risk analysis."
    )

    # ---- Sidebar configuration ----
    root_dir = Path(__file__).resolve().parents[1]
    default_geojson = root_dir / "outputs" / "model2_urban_water_stress.geojson"

    st.sidebar.header("Model 2 Configuration")
    geojson_path_str = st.sidebar.text_input(
        "Model 2 GeoJSON path",
        value=str(default_geojson),
        help="Path to `model2_urban_water_stress.geojson` produced by the pipeline.",
        key="model2_path",
    )

    # ---- Load data ----
    try:
        gdf = load_model2_results(geojson_path_str)
    except FileNotFoundError as e:
        st.error(str(e))
        st.info("Run Model 2 first to generate the GeoJSON output.")
        return
    except Exception as e:
        st.error(f"Failed to load GeoJSON: {e}")
        return

    if gdf.empty:
        st.warning("The loaded GeoJSON contains no features.")
        return

    score_col = "urban_water_stress_score"
    if score_col not in gdf.columns:
        st.error(f"Expected column '{score_col}' not found in data.")
        return

    # ---- Layout: Map + Top 10 table ----
    map_col, table_col = st.columns((2, 1))

    with map_col:
        st.subheader("Urban Water Stress Map")
        m = make_urban_water_stress_map(gdf)
        st_folium(m, width="100%", height=600)

    with table_col:
        st.subheader("Top 10 Highest-Stress Cities")
        # Find city name column if available
        city_name_col = None
        for col_name in ["name", "city_name", "city", "NAME", "CITY_NAME", "CITY"]:
            if col_name in gdf.columns:
                city_name_col = col_name
                break

        display_cols = [score_col, "total_population", "estimated_water_supply"]
        if city_name_col:
            display_cols.insert(0, city_name_col)

        top10 = gdf[display_cols].copy()
        top10 = top10.sort_values(score_col, ascending=False).head(10)
        if "geometry" in top10.columns:
            top10 = pd.DataFrame(top10.drop(columns="geometry"))

        # Format numeric columns for better readability
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

        # Rename columns for display
        rename_dict = {
            score_col: "Water Stress Score",
            "total_population": "Population",
            "estimated_water_supply": "Water Supply",
        }
        if city_name_col:
            rename_dict[city_name_col] = "City Name"

        top10 = top10.rename(columns=rename_dict)
        st.dataframe(top10.reset_index(drop=True), use_container_width=True)

    # ---- Automated Urban Insights panel ----
    st.markdown("---")
    st.subheader("Automated Urban Insights")

    insights = _compute_urban_insights(gdf, score_col=score_col)

    st.markdown(
        f"**Share of cities under high water stress (top 20%):** "
        f"{insights['high_risk_share_pct']:.1f}%"
    )
    st.markdown(
        f"**Share of cities in medium risk band (40–80th percentile):** "
        f"{insights['medium_risk_share_pct']:.1f}%"
    )
    st.markdown(
        f"**Share of cities in low risk band (bottom 40%):** "
        f"{insights['low_risk_share_pct']:.1f}%"
    )

    pattern_insights = insights.get("pattern_insights") or []
    if pattern_insights:
        st.markdown("**Risk pattern analysis:**")
        for line in pattern_insights:
            st.markdown(f"- {line}")

    recommended_actions = insights.get("recommended_actions") or []
    if recommended_actions:
        st.markdown("**Recommended actions:**")
        for action in recommended_actions:
            st.markdown(f"- {action}")


def main() -> None:
    st.title("Water Stress Intelligence Dashboard")
    st.markdown(
        "Comprehensive water stress analysis dashboard covering **agricultural zones** "
        "(Model 1) and **urban cities** (Model 2)."
    )

    # Create tabs
    tab1, tab2 = st.tabs(
        [
            "🌾 Agricultural Water Stress (Model 1)",
            "🏙️ Urban Water Stress (Model 2)",
        ]
    )

    with tab1:
        render_model1_tab()

    with tab2:
        render_model2_tab()


if __name__ == "__main__":
    main()
