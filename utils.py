"""
Utility functions for Smart Irrigation Dashboard
"""
import requests
from typing import Dict, Optional, Tuple, List
import pandas as pd


API_KEY = "03b355316ba8c38da288915abc1deb25"


def fetch_weather_data(lat: float, lon: float) -> Tuple[Optional[Dict], Optional[Dict]]:
    """Fetch current weather and forecast data from OpenWeatherMap API."""
    try:
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        
        weather_response = requests.get(weather_url, timeout=10)
        forecast_response = requests.get(forecast_url, timeout=10)
        
        weather_response.raise_for_status()
        forecast_response.raise_for_status()
        
        return weather_response.json(), forecast_response.json()
    except Exception as e:
        return None, None


def calculate_et0(temp: float, humidity: float, wind: float) -> float:
    """Calculate reference evapotranspiration (ET0) using simplified formula."""
    # Simplified ET0 calculation
    # In production, use FAO Penman-Monteith or similar standard method
    et0 = (0.35 * temp) + (0.45 * wind) - (0.25 * (humidity / 100))
    return round(max(0, et0), 2)  # Ensure non-negative


def calculate_water_need(et0: float, area: float, kc: float) -> float:
    """Calculate water need in liters."""
    # ET0 is in mm, convert to liters: 1 mm = 1 L per m²
    water_need = et0 * area * kc
    return round(water_need, 1)


def analyze_hourly_irrigation(forecast_data: Dict, hours: int = 8) -> Tuple[pd.DataFrame, Optional[str], float, bool]:
    """Analyze hourly irrigation suitability from forecast data."""
    rows = []
    best_hour = None
    best_score = -9999
    rain_expected = False
    
    for hour in forecast_data.get("list", [])[:hours]:
        temp = hour["main"]["temp"]
        humidity = hour["main"]["humidity"]
        wind = hour["wind"]["speed"]
        time = hour["dt_txt"]
        
        # Irrigation score: higher humidity, lower temp, lower wind = better
        score = (humidity * 0.4) - (temp * 0.3) - (wind * 0.6)
        
        rows.append({
            "Saat": time,
            "Sıcaklık (°C)": round(temp, 1),
            "Nem (%)": humidity,
            "Rüzgar (m/s)": round(wind, 1),
            "Uygunluk Skoru": round(score, 2)
        })
        
        if score > best_score:
            best_score = score
            best_hour = time
        
        if hour.get("rain"):
            rain_expected = True
    
    df = pd.DataFrame(rows)
    return df, best_hour, best_score, rain_expected


def get_confidence_level(et0: float, forecast_count: int) -> Tuple[str, str]:
    """Get confidence level for recommendations."""
    if forecast_count >= 8 and et0 > 0:
        return "Yüksek", "success"
    elif forecast_count >= 5:
        return "Orta", "warning"
    else:
        return "Düşük", "danger"


def calculate_decision_confidence(
    et0: float,
    forecast_count: int,
    strategy_type: str,
    rain_expected: bool,
    weather_risk: str
) -> float:
    """
    Calculate decision confidence score (0-100%).
    
    Factors:
    - Forecast data quality (more data points = higher confidence)
    - ET0 reliability (reasonable ET0 values = higher confidence)
    - Strategy type (water-saving strategies are more certain)
    - Weather conditions (stable conditions = higher confidence)
    """
    # Base confidence from forecast data (0-40 points)
    if forecast_count >= 8:
        data_confidence = 40
    elif forecast_count >= 5:
        data_confidence = 30
    elif forecast_count >= 3:
        data_confidence = 20
    else:
        data_confidence = 10
    
    # ET0 reliability (0-25 points)
    if 0 < et0 < 10:
        et0_confidence = 25
    elif 0 < et0 < 15:
        et0_confidence = 20
    else:
        et0_confidence = 15
    
    # Strategy type confidence (0-20 points)
    if strategy_type == "water_saving":
        strategy_confidence = 20  # High confidence - clear decision
    elif strategy_type == "risk_aware":
        strategy_confidence = 15  # Medium-high confidence
    else:
        strategy_confidence = 18  # Recommended strategy - good confidence
    
    # Weather stability (0-15 points)
    if weather_risk == "low":
        weather_confidence = 15
    elif weather_risk == "medium":
        weather_confidence = 10
    else:
        weather_confidence = 5
    
    # Rain expectation bonus/penalty
    if rain_expected:
        rain_bonus = 5  # High confidence when rain is expected
    else:
        rain_bonus = 0
    
    total_confidence = data_confidence + et0_confidence + strategy_confidence + weather_confidence + rain_bonus
    
    # Normalize to 0-100
    confidence_score = min(100, max(0, total_confidence))
    
    return round(confidence_score, 1)


def format_time(time_str: str) -> str:
    """Format datetime string to Turkish readable format."""
    if not time_str:
        return time_str
        
    try:
        from datetime import datetime
        
        # Turkish month names
        turkish_months = {
            1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan",
            5: "Mayıs", 6: "Haziran", 7: "Temmuz", 8: "Ağustos",
            9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
        }
        
        # Try different datetime formats
        dt = None
        formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(time_str, fmt)
                break
            except ValueError:
                continue
        
        if dt is None:
            return time_str
        
        day = dt.day
        month = turkish_months[dt.month]
        year = dt.year
        hour = dt.hour
        minute = dt.minute
        
        return f"{day} {month} {year}, {hour:02d}:{minute:02d}"
    except Exception as e:
        # If formatting fails, return original string
        return time_str


def generate_ai_irrigation_strategy(
    platform_mode: str,
    et0: float,
    water_need: float,
    area: float,
    humidity: float,
    temp: float,
    wind: float,
    rain_expected: bool,
    drought_risk_score: Optional[float] = None,
    user_type: Optional[str] = None,
    geojson_drought_category: Optional[str] = None,
    basin_water_stressed: Optional[bool] = None,
) -> Dict:
    """
    AI-powered decision engine that generates strategic irrigation recommendations.
    
    Returns:
        Dict with strategy_type, strategy_name, recommendation, reasoning, and action_items
    """
    # Determine strategy type based on conditions
    strategy_type = None
    strategy_name = None
    recommendation = ""
    reasoning = []
    action_items = []
    
    # Calculate risk factors
    weather_risk = "low"
    if temp > 30 or humidity < 30 or wind > 5:
        weather_risk = "high"
    elif temp > 25 or humidity < 40:
        weather_risk = "medium"
    
    # Determine field size category
    if platform_mode == "🏛 Kamu / Belediye Modu":
        field_size_category = "regional"
    elif area < 50:
        field_size_category = "small"
    elif area < 500:
        field_size_category = "medium"
    else:
        field_size_category = "large"
    
    geojson_force_water_saving = geojson_drought_category in ("High", "Extreme")
    basin_force = bool(basin_water_stressed)

    # Strategy 1: Water-Saving Mode — policy-grade advisory
    if rain_expected or et0 < 2 or geojson_force_water_saving or basin_force:
        strategy_type = "water_saving"
        strategy_name = "Stratejik Su Koruma Modu"
        
        if platform_mode == "🏛 Kamu / Belediye Modu":
            recommendation = (
                "Politika önerisi: Bölgesel su güvenliği ve kaynak koruma kapsamında sulama ertelenmelidir. "
                "Mevcut meteorolojik koşullar ve beklenen yağış, sulama ihtiyacını minimize etmektedir. "
                "Bu strateji ile bölgesel su kaynaklarında önemli tasarruf ve operasyonel verimlilik sağlanacaktır."
            )
            reasoning = [
                f"ET0 {et0:.2f} mm — düşük referans buharlaşma; su ihtiyacı minimal",
                "Yakın zamanda yağış bekleniyor" if rain_expected else "Su ihtiyacı minimum seviyede",
                "Bölgesel su kaynakları koruma önceliği — veri odaklı karar"
            ]
            action_items = [
                "Sulama işlemlerini erteliyin; protokol uyumunu koruyun",
                "Yağış sonrası durumu yeniden değerlendirin",
                "Su depolama ve dağıtım sistemlerini gözden geçirin"
            ]
        else:
            recommendation = (
                "Öneri: Mevcut koşullarda sulama yapmanız gerekmiyor. "
                f"{'Yakın zamanda yağış bekleniyor' if rain_expected else 'Bitki su ihtiyacı çok düşük'}; "
                "su tasarrufu ve verimlilik için bu strateji uygundur."
            )
            reasoning = [
                f"ET0 {et0:.2f} mm — düşük buharlaşma",
                "Yağış bekleniyor" if rain_expected else "Minimum su ihtiyacı",
                f"{area:.0f} m² alan için optimize edilmiş karar desteği"
            ]
            action_items = [
                "Sulama yapmayın; su tasarrufu sağlayın",
                "Bitkileri gözlemleyin",
                "Yağış sonrası durumu kontrol edin"
            ]
        # Drought-only trigger: override messaging when GeoJSON says High/Extreme
        if geojson_force_water_saving and not rain_expected and et0 >= 2:
            if platform_mode == "🏛 Kamu / Belediye Modu":
                recommendation = (
                    "Politika önerisi: SPI verisine göre bölgede yüksek/ekstrem kuraklık riski tespit edildi. "
                    "Su tasarrufu modu önerilir; sulama ertelenmeli, kaynak koruma önceliklidir."
                )
                reasoning = [
                    f"SPI tabanlı kuraklık: {geojson_drought_category}",
                    "Bölgesel su kaynakları koruma önceliği — veri odaklı karar",
                ]
                action_items = [
                    "Sulama işlemlerini erteleyin",
                    "SPI ve kuraklık izlemesini sürdürün",
                    "Su depolama ve dağıtım sistemlerini gözden geçirin",
                ]
            else:
                recommendation = (
                    "Öneri: Bölgede yüksek kuraklık riski (SPI) tespit edildi. "
                    "Su tasarrufu modu uygulayın; sulama ertelenmeli."
                )
                reasoning = [
                    f"SPI tabanlı kuraklık: {geojson_drought_category}",
                    f"{area:.0f} m² alan için optimize edilmiş karar desteği",
                ]
                action_items = [
                    "Sulama yapmayın; su tasarrufu sağlayın",
                    "Bitkileri gözlemleyin",
                    "Kuraklık verilerini takip edin",
                ]
        elif basin_force and not rain_expected and et0 >= 2 and not geojson_force_water_saving:
            if platform_mode == "🏛 Kamu / Belediye Modu":
                recommendation = (
                    "Politika önerisi: Havza verisine göre bölgede yüksek su stresi tespit edildi. "
                    "Su tasarrufu modu önerilir; sulama ertelenmeli, havza koruma önceliklidir."
                )
                reasoning = [
                    "Havza tabanlı su stresi — yüksek",
                    "Bölgesel su kaynakları koruma önceliği — veri odaklı karar",
                ]
                action_items = [
                    "Sulama işlemlerini erteleyin",
                    "Havza su durumunu izleyin",
                    "Su depolama ve dağıtım sistemlerini gözden geçirin",
                ]
            else:
                recommendation = (
                    "Öneri: Seçilen konumun havzasında yüksek su stresi tespit edildi. "
                    "Su tasarrufu modu uygulayın; sulama ertelenmeli."
                )
                reasoning = [
                    "Havza tabanlı su stresi — yüksek",
                    f"{area:.0f} m² alan için optimize edilmiş karar desteği",
                ]
                action_items = [
                    "Sulama yapmayın; su tasarrufu sağlayın",
                    "Bitkileri gözlemleyin",
                    "Havza verilerini takip edin",
                ]
    
    # Strategy 2: Risk-Aware Irrigation — policy advisory
    elif weather_risk == "high" or (drought_risk_score and drought_risk_score > 2):
        strategy_type = "risk_aware"
        strategy_name = "Risk Farkındalıklı Sulama — Stratejik Yönetim"
        
        if platform_mode == "🏛 Kamu / Belediye Modu":
            recommendation = (
                "Politika önerisi: Yüksek risk koşulları tespit edildi. Bölgesel su yönetimi için "
                "risk farkındalıklı sulama stratejisi uygulanmalıdır. Kuraklık riski ve yüksek buharlaşma "
                "nedeniyle su kullanımı minimize edilmeli; alternatif kaynaklar ve kısıtlama protokolleri değerlendirilmelidir."
            )
            reasoning = [
                f"Kuraklık risk skoru: {drought_risk_score:.2f}" if drought_risk_score else f"ET0 {et0:.2f} mm — yüksek",
                f"Sıcaklık {temp:.1f}°C — yüksek buharlaşma riski; nem %{humidity:.0f}",
                "Bölgesel su kaynakları üzerinde baskı — veri tabanlı uyarı"
            ]
            action_items = [
                "Acil su yönetim protokollerini devreye alın",
                "Çiftçilere / paydaşlara su kısıtlaması bilgilendirmesi yapın",
                "Alternatif su kaynaklarını değerlendirin",
                "Günlük su kullanımını izleyin ve raporlayın"
            ]
        else:
            recommendation = (
                "Öneri: Risk farkındalıklı sulama uygulayın. Yüksek sıcaklık ve düşük nem nedeniyle "
                "su kaybı riski yüksek; dikkatli ve optimize edilmiş sulama verimlilik için kritiktir."
            )
            reasoning = [
                f"ET0 {et0:.2f} mm — yüksek buharlaşma",
                f"Sıcaklık {temp:.1f}°C, nem %{humidity:.0f}",
                f"{area:.0f} m² alan için risk değerlendirmesi"
            ]
            action_items = [
                "Sabah erken veya akşam geç saatlerde sulama yapın",
                "Damla sulama tercih edin; su kaybını azaltın",
                "Bitki kök bölgesine odaklanın",
                "Gölgeleme veya malç kullanımını değerlendirin"
            ]
    
    # Strategy 3: Recommended Irrigation — optimal conditions, policy-grade
    else:
        strategy_type = "recommended"
        strategy_name = "Optimal Sulama Stratejisi"
        
        if platform_mode == "🏛 Kamu / Belediye Modu":
            recommendation = (
                "Politika önerisi: Optimal sulama koşulları mevcut. Bölgesel sulama işlemleri için "
                "standart protokoller uygulanabilir. Meteorolojik koşullar su verimliliği için uygun; "
                "bölgesel su kaynakları yeterli seviyede. Sulama planlaması yapılabilir."
            )
            reasoning = [
                f"ET0 {et0:.2f} mm — optimal aralık",
                f"Sıcaklık {temp:.1f}°C, nem %{humidity:.0f} — uygun koşullar",
                f"Bölgesel alan {area:.0f} km² — veri odaklı karar desteği"
            ]
            action_items = [
                "Standart sulama protokollerini uygulayın",
                "Optimal sulama saatlerini takip edin",
                "Su kullanım verimliliğini izleyin ve raporlayın",
                "Bölgesel çiftçilere / paydaşlara bilgilendirme yapın"
            ]
        else:
            recommendation = (
                "Öneri: Mevcut koşullar sulama için uygun. "
                f"{area:.0f} m² alan için optimize edilmiş sulama planı uygulanabilir; "
                "su verimliliği yüksek olacaktır."
            )
            reasoning = [
                f"ET0 {et0:.2f} mm — optimal buharlaşma",
                f"Sıcaklık {temp:.1f}°C, nem %{humidity:.0f}",
                f"{area:.0f} m² alan için hesaplanmış karar desteği"
            ]
            action_items = [
                "Önerilen saatte sulama yapın",
                "Su miktarını optimize edin",
                "Bitki ihtiyacına göre ayarlayın",
                "Sulama sonrası gözlem yapın"
            ]
    
    # Add user-type specific adjustments for Farmer Mode
    if platform_mode == "👩‍🌾 Bireysel / Çiftçi Modu" and user_type:
        from components import get_user_type_config
        config = get_user_type_config(user_type)
        
        if config["tone"] == "friendly":
            # Make language more friendly for home gardeners
            recommendation = recommendation.replace("öneriliyor", "öneriyoruz")
            recommendation = recommendation.replace("yapmalısınız", "yapabilirsiniz")
        elif config["complexity"] == "expert":
            # Add more technical details for large-scale farmers
            recommendation += f" Teknik detaylar: Kc katsayısı ve alan bazlı hesaplamalar optimize edilmiştir."
    
    return {
        "strategy_type": strategy_type,
        "strategy_name": strategy_name,
        "recommendation": recommendation,
        "reasoning": reasoning,
        "action_items": action_items,
        "weather_risk": weather_risk,
        "field_size_category": field_size_category
    }


def calculate_sustainability_metrics(
    water_need: float,
    et0: float,
    area: float,
    rain_expected: bool,
    strategy_type: str,
    platform_mode: str
) -> Dict:
    """
    Calculate sustainability and impact metrics.
    
    Returns:
        Dict with water_saved, sustainability_score, cost_saved, environmental_impact
    """
    # Base water consumption (if irrigation was done without optimization)
    base_water = water_need
    
    # Calculate water saved based on strategy
    if strategy_type == "water_saving":
        # Water saved by not irrigating or delaying
        water_saved = base_water
    elif strategy_type == "risk_aware":
        # Water saved by optimized irrigation (reduced by 20%)
        water_saved = base_water * 0.2
    else:
        # Recommended strategy saves some water through optimization (10%)
        water_saved = base_water * 0.1
    
    # Calculate sustainability score (0-100)
    # Factors: water efficiency, timing optimization, environmental impact
    # Higher water saved = higher efficiency score
    if base_water > 0:
        water_savings_ratio = water_saved / base_water
        efficiency_score = min(100, water_savings_ratio * 100)
    else:
        efficiency_score = 100  # No water needed = perfect efficiency
    
    # Timing score: better if avoiding rain or optimizing timing
    if rain_expected:
        timing_score = 100  # Perfect score for avoiding rain
    elif strategy_type == "water_saving":
        timing_score = 95  # High score for water-saving mode
    else:
        timing_score = 80  # Good score for optimized timing
    
    # Environmental score: lower ET0 = better environmental conditions
    environmental_score = max(0, min(100, 100 - (et0 * 5)))  # Adjusted multiplier
    
    sustainability_score = round((efficiency_score * 0.4 + timing_score * 0.3 + environmental_score * 0.3), 1)
    sustainability_score = max(0, min(100, sustainability_score))
    
    score_breakdown = {
        "efficiency": round(efficiency_score, 1),
        "timing": round(timing_score, 1),
        "environmental": round(environmental_score, 1),
    }
    
    # Cost savings (assuming water cost per liter)
    # Average water cost: ~0.01 TL per liter for agricultural use
    water_cost_per_liter = 0.01
    cost_saved_tl = water_saved * water_cost_per_liter
    
    # For public mode, scale up
    if platform_mode == "🏛 Kamu / Belediye Modu":
        # Regional scale multiplier
        cost_saved_tl = cost_saved_tl * 10  # Scale for regional impact
    
    # Environmental impact (CO2 equivalent saved)
    # Water treatment and distribution: ~0.5 kg CO2 per m³
    co2_saved_kg = (water_saved / 1000) * 0.5  # Convert liters to m³
    
    # Environmental impact level
    if co2_saved_kg > 10:
        impact_level = "Yüksek Etki"
        impact_color = "success"
    elif co2_saved_kg > 5:
        impact_level = "Orta Etki"
        impact_color = "info"
    else:
        impact_level = "Düşük Etki"
        impact_color = "neutral"
    
    return {
        "water_saved": round(water_saved, 1),
        "sustainability_score": sustainability_score,
        "cost_saved_tl": round(cost_saved_tl, 2),
        "co2_saved_kg": round(co2_saved_kg, 2),
        "environmental_impact_level": impact_level,
        "environmental_impact_color": impact_color,
        "base_water": round(base_water, 1),
        "score_breakdown": score_breakdown,
    }


def simulate_scenarios(
    current_water_need: float,
    current_et0: float,
    area: float,
    rain_expected: bool,
    forecast_data: Optional[Dict] = None,
    platform_mode: str = "👩‍🌾 Bireysel / Çiftçi Modu"
) -> Dict:
    """
    Simulate different irrigation scenarios for comparison.
    
    Returns:
        Dict with scenario comparisons
    """
    scenarios = {}
    
    # Scenario 1: Irrigate Today (Current recommendation)
    if rain_expected or current_et0 < 2:
        scenario1_water = 0  # Don't irrigate
        scenario1_score = 95  # High score for saving water
    else:
        scenario1_water = current_water_need
        scenario1_score = 75  # Good score for optimal timing
    
    scenarios["today"] = {
        "name": "Bugün Sulama",
        "water_used": scenario1_water,
        "sustainability_score": scenario1_score,
        "description": "Önerilen stratejiye göre bugün sulama yapılması"
    }
    
    # Scenario 2: Delay Irrigation (Wait for better conditions)
    if forecast_data:
        # Estimate tomorrow's ET0 (simplified - use average of next day)
        future_et0 = current_et0 * 0.9  # Assume slightly better conditions
        future_water = current_water_need * (future_et0 / max(current_et0, 0.1))
        delay_score = 85 if future_et0 < current_et0 else 70
    else:
        future_water = current_water_need * 1.1  # Assume conditions worsen
        delay_score = 65
    
    scenarios["delay"] = {
        "name": "Sulamayı Ertelama",
        "water_used": round(future_water, 1),
        "sustainability_score": delay_score,
        "description": "Sulamayı ertesi güne erteleme senaryosu"
    }
    
    # Scenario 3: Water-Saving Mode (Minimal irrigation)
    water_saving_water = current_water_need * 0.6  # 40% reduction
    water_saving_score = 90  # High score for conservation
    
    scenarios["water_saving"] = {
        "name": "Su Tasarrufu Modu",
        "water_used": round(water_saving_water, 1),
        "sustainability_score": water_saving_score,
        "description": "Minimum su kullanımı ile sulama"
    }
    
    # Scenario 4: Normal Mode (Standard irrigation without optimization)
    normal_water = current_water_need * 1.2  # 20% more water (less efficient)
    normal_score = 60  # Lower score
    
    scenarios["normal"] = {
        "name": "Normal Mod",
        "water_used": round(normal_water, 1),
        "sustainability_score": normal_score,
        "description": "Optimizasyon olmadan standart sulama"
    }
    
    # Calculate differences
    best_scenario = min(scenarios.values(), key=lambda x: x["water_used"])
    worst_scenario = max(scenarios.values(), key=lambda x: x["water_used"])
    
    water_difference = worst_scenario["water_used"] - best_scenario["water_used"]
    
    return {
        "scenarios": scenarios,
        "best_scenario": best_scenario["name"],
        "worst_scenario": worst_scenario["name"],
        "water_difference": round(water_difference, 1),
        "recommended_scenario": scenarios["today"]["name"]
    }


# ==================== REGIONAL INTELLIGENCE LAYER ====================
# This layer is designed to integrate external datasets (regional water, drought risk, agricultural data)
#
# DATASET INTEGRATION GUIDE:
# --------------------------
# Supported dataset formats: CSV, JSON
# Expected dataset locations: ./datasets/ directory
#
# Dataset file naming convention:
#   - Water resources: water_resources.csv or water_resources.json
#   - Drought risk: drought_risk.csv or drought_risk.json
#   - Agricultural data: agricultural_data.csv or agricultural_data.json
#
# CSV column requirements:
#   - Must include 'region_name' or 'lat'/'lon' columns for location matching
#   - See individual loader functions for required column names
#
# JSON structure requirements:
#   - Must be a list of records or a dict with region keys
#   - See individual loader functions for required field names

import os
import json
from pathlib import Path

# Dataset configuration
DATASETS_DIR = Path("datasets")  # Change this to your datasets directory
DATASET_CACHE = {}  # In-memory cache for loaded datasets

# GeoJSON drought dataset (SPI index)
_DROUGHT_GEOJSON_FILENAME = "kuraklık-spi-i̇ndeksi.geojson"
_drought_geojson_cache: Optional[dict] = None


def _load_drought_geojson() -> Optional[dict]:
    """Load SPI GeoJSON safely. Returns None if missing or invalid. Cached."""
    global _drought_geojson_cache
    if _drought_geojson_cache is not None:
        return _drought_geojson_cache
    path = Path(__file__).resolve().parent / "datasets" / _DROUGHT_GEOJSON_FILENAME
    if not path.exists():
        _drought_geojson_cache = {}
        return _drought_geojson_cache
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        _drought_geojson_cache = data if isinstance(data, dict) else {}
        return _drought_geojson_cache
    except Exception:
        _drought_geojson_cache = {}
        return _drought_geojson_cache


def _spi_to_drought_category(spi: float) -> str:
    """Map SPI to drought severity: Low, Medium, High, Extreme."""
    if spi >= -0.5:
        return "Low"
    if spi >= -1.0:
        return "Medium"
    if spi >= -1.5:
        return "High"
    return "Extreme"


def get_drought_risk_from_geojson(lat: float, lon: float) -> Dict:
    """
    Extract drought risk (SPI-based) for a map location from the GeoJSON dataset.
    
    Uses the nearest feature by lat/lon. SPI from last6month (primary), then last3month, last1month.
    Returns placeholder and 'Dataset unavailable' if file is missing or no match.
    
    Returns:
        Dict with:
        - spi_value: float or None
        - spi_label: str (e.g. "-1.2")
        - drought_category: "Low" | "Medium" | "High" | "Extreme"
        - risk_label: str for UI (e.g. "Düşük", "Orta", "Yüksek", "Ekstrem")
        - data_available: bool
        - source: str ("SPI GeoJSON" or "Dataset unavailable")
    """
    risk_labels = {"Low": "Düşük", "Medium": "Orta", "High": "Yüksek", "Extreme": "Ekstrem"}
    placeholder = {
        "spi_value": None,
        "spi_label": "—",
        "drought_category": "Low",
        "risk_label": "Düşük",
        "data_available": False,
        "source": "Dataset unavailable",
    }
    
    geo = _load_drought_geojson()
    if not geo or not geo.get("features"):
        return placeholder
    
    features = [f for f in geo["features"] if f.get("geometry") and f["geometry"].get("coordinates")]
    if not features:
        return placeholder
    
    best = None
    best_dist = float("inf")
    for f in features:
        coords = f["geometry"]["coordinates"]
        plon, plat = coords[0], coords[1]
        d = (lat - plat) ** 2 + (lon - plon) ** 2
        if d < best_dist:
            best_dist = d
            best = f
    
    if best is None:
        return placeholder
    
    props = best.get("properties") or {}
    spi = props.get("last6month")
    if spi is None:
        spi = props.get("last3month")
    if spi is None:
        spi = props.get("last1month")
    if spi is None:
        return placeholder
    
    try:
        spi = float(spi)
    except (TypeError, ValueError):
        return placeholder
    
    category = _spi_to_drought_category(spi)
    return {
        "spi_value": round(spi, 2),
        "spi_label": f"{spi:.2f}",
        "drought_category": category,
        "risk_label": risk_labels.get(category, "Düşük"),
        "data_available": True,
        "source": "SPI GeoJSON",
    }


# Watershed / basin boundary GeoJSON
_WATERSHED_GEOJSON_FILENAME = "havza_sinirlari.geojson"
_watershed_geojson_cache: Optional[dict] = None


def _load_watershed_geojson() -> Optional[dict]:
    """Load watershed GeoJSON safely. Returns {} if missing or invalid. Cached."""
    global _watershed_geojson_cache
    if _watershed_geojson_cache is not None:
        return _watershed_geojson_cache
    path = Path(__file__).resolve().parent / "datasets" / _WATERSHED_GEOJSON_FILENAME
    if not path.exists():
        _watershed_geojson_cache = {}
        return _watershed_geojson_cache
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        _watershed_geojson_cache = data if isinstance(data, dict) else {}
        return _watershed_geojson_cache
    except Exception:
        _watershed_geojson_cache = {}
        return _watershed_geojson_cache


def get_watershed_for_location(lat: float, lon: float) -> Dict:
    """
    Detect which watershed (basin) the given map location belongs to via point-in-polygon.
    
    Uses shapely for GeoJSON Polygon/MultiPolygon containment. Returns basin name, ID,
    and water stress label when available. Placeholder and 'Dataset unavailable' if missing.
    
    Returns:
        Dict with:
        - basin_name: str
        - basin_id: str or None
        - water_stress_label: str ("Veri yok", "Düşük", "Orta", "Yüksek", or "—")
        - data_available: bool
        - source: str ("Havza GeoJSON" or "Dataset unavailable")
    """
    placeholder = {
        "basin_name": "—",
        "basin_id": None,
        "water_stress_label": "—",
        "data_available": False,
        "source": "Dataset unavailable",
    }
    
    geo = _load_watershed_geojson()
    if not geo or not geo.get("features"):
        return placeholder
    
    try:
        from shapely.geometry import shape, Point
    except ImportError:
        return placeholder
    
    point = Point(lon, lat)
    
    for feat in geo["features"]:
        geom_data = feat.get("geometry")
        if not geom_data or not geom_data.get("coordinates"):
            continue
        try:
            geom = shape(geom_data)
            if geom.is_valid and not geom.is_empty and geom.contains(point):
                props = feat.get("properties") or {}
                basin_name = props.get("havza_ad") or "—"
                basin_id = props.get("havza_no") or (str(props.get("h_no")) if props.get("h_no") is not None else None)
                water_stress = props.get("water_stress") or props.get("su_stresi")
                if water_stress is not None:
                    stress_map = {"low": "Düşük", "medium": "Orta", "high": "Yüksek", "düşük": "Düşük", "orta": "Orta", "yüksek": "Yüksek"}
                    water_stress_label = stress_map.get(str(water_stress).lower(), str(water_stress))
                else:
                    water_stress_label = "Veri yok"
                return {
                    "basin_name": basin_name,
                    "basin_id": basin_id,
                    "water_stress_label": water_stress_label,
                    "data_available": True,
                    "source": "Havza GeoJSON",
                }
        except Exception:
            continue
    
    return placeholder


def load_regional_dataset(
    dataset_type: str,
    file_format: str = "auto"
) -> Optional[pd.DataFrame]:
    """
    Load a regional dataset from CSV or JSON file.
    
    This is the main data loader function that handles:
    - Auto-detection of file format
    - Caching for performance
    - Graceful fallback if file doesn't exist
    
    Args:
        dataset_type: Type of dataset to load. Options:
            - "water_resources": Regional water level and stress data
            - "drought_risk": Drought indices and severity data
            - "agricultural_data": Crop and irrigation statistics
        file_format: "csv", "json", or "auto" (auto-detect)
        
    Returns:
        pd.DataFrame with dataset or None if not available
        
    Example CSV structure for water_resources:
        region_name,lat,lon,groundwater_level,surface_water_availability,water_stress_index
        Konya,37.87,32.49,45.2,Medium,0.65
        
    Example JSON structure for water_resources:
        [
            {
                "region_name": "Konya",
                "lat": 37.87,
                "lon": 32.49,
                "groundwater_level": 45.2,
                "surface_water_availability": "Medium",
                "water_stress_index": 0.65
            }
        ]
    """
    # Check cache first
    cache_key = f"{dataset_type}_{file_format}"
    if cache_key in DATASET_CACHE:
        return DATASET_CACHE[cache_key]
    
    # Define file paths
    csv_path = DATASETS_DIR / f"{dataset_type}.csv"
    json_path = DATASETS_DIR / f"{dataset_type}.json"
    
    df = None
    
    try:
        # Auto-detect or use specified format
        if file_format == "auto":
            if csv_path.exists():
                df = pd.read_csv(csv_path)
            elif json_path.exists():
                df = pd.read_json(json_path)
        elif file_format == "csv" and csv_path.exists():
            df = pd.read_csv(csv_path)
        elif file_format == "json" and json_path.exists():
            df = pd.read_json(json_path)
        
        # Cache the result
        if df is not None:
            DATASET_CACHE[cache_key] = df
            
    except Exception as e:
        # Log error but don't crash - graceful degradation
        print(f"Warning: Could not load dataset '{dataset_type}': {e}")
        df = None
    
    return df


def find_region_in_dataset(
    df: Optional[pd.DataFrame],
    lat: float,
    lon: float,
    region_name: Optional[str] = None,
    tolerance: float = 0.5
) -> Optional[Dict]:
    """
    Find matching region data in a dataset.
    
    Matching priority:
    1. Exact region_name match (if provided)
    2. Closest lat/lon within tolerance
    
    Args:
        df: DataFrame with regional data
        lat: Latitude to match
        lon: Longitude to match
        region_name: Optional region name for exact matching
        tolerance: Lat/lon tolerance for geographic matching (degrees)
        
    Returns:
        Dict with matching row data or None
    """
    if df is None or df.empty:
        return None
    
    try:
        # Try region name match first
        if region_name and "region_name" in df.columns:
            # Case-insensitive partial match
            mask = df["region_name"].str.lower().str.contains(region_name.lower(), na=False)
            if mask.any():
                return df[mask].iloc[0].to_dict()
        
        # Try lat/lon match
        if "lat" in df.columns and "lon" in df.columns:
            df_filtered = df[
                (abs(df["lat"] - lat) <= tolerance) &
                (abs(df["lon"] - lon) <= tolerance)
            ]
            
            if not df_filtered.empty:
                # Return closest match
                df_filtered = df_filtered.copy()
                df_filtered["_distance"] = (
                    (df_filtered["lat"] - lat) ** 2 +
                    (df_filtered["lon"] - lon) ** 2
                ) ** 0.5
                return df_filtered.nsmallest(1, "_distance").iloc[0].to_dict()
        
    except Exception as e:
        print(f"Warning: Error finding region in dataset: {e}")
    
    return None


def get_placeholder_data() -> Dict:
    """
    Return placeholder data structure when datasets are not available.
    
    This ensures backward compatibility when no datasets are loaded.
    
    Returns:
        Dict with placeholder values matching expected structure
    """
    return {
        "water_resources": {
            "groundwater_level": None,
            "surface_water_availability": None,
            "water_stress_index": None,
            "data_source": "Dataset-powered insight (coming from regional data)",
            "data_available": False
        },
        "drought_risk": {
            "spi_index": None,
            "drought_severity": None,
            "historical_trend": None,
            "data_source": "Dataset-powered insight (coming from regional data)",
            "data_available": False
        },
        "agricultural_data": {
            "crop_yield_trend": None,
            "irrigation_coverage": None,
            "farmer_adoption_rate": None,
            "data_source": "Dataset-powered insight (coming from regional data)",
            "data_available": False
        },
        "regional_insights": {
            "water_availability_score": None,
            "risk_factors": [],
            "recommendations": [],
            "data_source": "Dataset-powered insight (coming from regional data)",
            "data_available": False
        }
    }


def process_water_resources_data(raw_data: Optional[Dict]) -> Dict:
    """
    Process raw water resources data into standardized format.
    
    Expected raw data columns/fields:
        - groundwater_level: Numeric (meters or percentage)
        - surface_water_availability: String (Low/Medium/High) or Numeric
        - water_stress_index: Numeric (0-1 scale)
        
    Args:
        raw_data: Dict from dataset row
        
    Returns:
        Processed water resources dict
    """
    if raw_data is None:
        return {
            "groundwater_level": None,
            "surface_water_availability": None,
            "water_stress_index": None,
            "data_source": "Dataset-powered insight (coming from regional data)",
            "data_available": False
        }
    
    # ==================================================================
    # DATASET INTEGRATION POINT: Water Resources
    # ------------------------------------------------------------------
    # Map your dataset columns to these fields:
    #   - groundwater_level: Your column name for groundwater data
    #   - surface_water_availability: Your column for surface water
    #   - water_stress_index: Your column for water stress (0-1 scale)
    # ==================================================================
    
    return {
        "groundwater_level": raw_data.get("groundwater_level"),
        "surface_water_availability": raw_data.get("surface_water_availability"),
        "water_stress_index": raw_data.get("water_stress_index"),
        "data_source": raw_data.get("data_source", "Regional Water Dataset"),
        "data_available": True,
        # Additional fields can be added here from dataset
        "last_updated": raw_data.get("last_updated"),
        "measurement_unit": raw_data.get("measurement_unit", "meters")
    }


def process_drought_risk_data(raw_data: Optional[Dict]) -> Dict:
    """
    Process raw drought risk data into standardized format.
    
    Expected raw data columns/fields:
        - spi_index: Standardized Precipitation Index (-3 to +3 scale)
        - drought_severity: String (None/Mild/Moderate/Severe/Extreme)
        - historical_trend: String (Improving/Stable/Worsening)
        
    Args:
        raw_data: Dict from dataset row
        
    Returns:
        Processed drought risk dict
    """
    if raw_data is None:
        return {
            "spi_index": None,
            "drought_severity": None,
            "historical_trend": None,
            "data_source": "Dataset-powered insight (coming from regional data)",
            "data_available": False
        }
    
    # ==================================================================
    # DATASET INTEGRATION POINT: Drought Risk
    # ------------------------------------------------------------------
    # Map your dataset columns to these fields:
    #   - spi_index: Standardized Precipitation Index
    #   - drought_severity: Drought severity classification
    #   - historical_trend: Long-term trend direction
    # ==================================================================
    
    return {
        "spi_index": raw_data.get("spi_index"),
        "drought_severity": raw_data.get("drought_severity"),
        "historical_trend": raw_data.get("historical_trend"),
        "data_source": raw_data.get("data_source", "Regional Drought Dataset"),
        "data_available": True,
        # Additional fields can be added here from dataset
        "last_updated": raw_data.get("last_updated"),
        "forecast_period": raw_data.get("forecast_period")
    }


def process_agricultural_data(raw_data: Optional[Dict]) -> Dict:
    """
    Process raw agricultural data into standardized format.
    
    Expected raw data columns/fields:
        - crop_yield_trend: String (Increasing/Stable/Decreasing) or Numeric
        - irrigation_coverage: Numeric (percentage 0-100)
        - farmer_adoption_rate: Numeric (percentage 0-100)
        
    Args:
        raw_data: Dict from dataset row
        
    Returns:
        Processed agricultural data dict
    """
    if raw_data is None:
        return {
            "crop_yield_trend": None,
            "irrigation_coverage": None,
            "farmer_adoption_rate": None,
            "data_source": "Dataset-powered insight (coming from regional data)",
            "data_available": False
        }
    
    # ==================================================================
    # DATASET INTEGRATION POINT: Agricultural Data
    # ------------------------------------------------------------------
    # Map your dataset columns to these fields:
    #   - crop_yield_trend: Yield trend indicator
    #   - irrigation_coverage: Percentage of irrigated land
    #   - farmer_adoption_rate: Smart irrigation adoption rate
    # ==================================================================
    
    return {
        "crop_yield_trend": raw_data.get("crop_yield_trend"),
        "irrigation_coverage": raw_data.get("irrigation_coverage"),
        "farmer_adoption_rate": raw_data.get("farmer_adoption_rate"),
        "data_source": raw_data.get("data_source", "Regional Agricultural Dataset"),
        "data_available": True,
        # Additional fields can be added here from dataset
        "last_updated": raw_data.get("last_updated"),
        "dominant_crop": raw_data.get("dominant_crop"),
        "total_agricultural_area": raw_data.get("total_agricultural_area")
    }


def calculate_regional_insights(
    water_data: Dict,
    drought_data: Dict,
    agricultural_data: Dict
) -> Dict:
    """
    Calculate composite regional insights from all data sources.
    
    This function synthesizes data from multiple sources to provide
    actionable insights and recommendations.
    
    Args:
        water_data: Processed water resources data
        drought_data: Processed drought risk data
        agricultural_data: Processed agricultural data
        
    Returns:
        Dict with composite insights and recommendations
    """
    risk_factors = []
    recommendations = []
    water_availability_score = None
    
    # Check if any data is available
    data_available = any([
        water_data.get("data_available", False),
        drought_data.get("data_available", False),
        agricultural_data.get("data_available", False)
    ])
    
    if not data_available:
        return {
            "water_availability_score": None,
            "risk_factors": [],
            "recommendations": [],
            "data_source": "Dataset-powered insight (coming from regional data)",
            "data_available": False
        }
    
    # ==================================================================
    # DATASET INTEGRATION POINT: Composite Insights
    # ------------------------------------------------------------------
    # Add your logic here to calculate composite scores and generate
    # recommendations based on the available data.
    # ==================================================================
    
    # Calculate water availability score (0-100)
    if water_data.get("water_stress_index") is not None:
        # Convert stress index (0-1, higher is worse) to availability (0-100, higher is better)
        stress_index = water_data["water_stress_index"]
        water_availability_score = max(0, min(100, (1 - stress_index) * 100))
    
    # Generate risk factors from water data
    if water_data.get("data_available"):
        stress_index = water_data.get("water_stress_index")
        if stress_index is not None:
            if stress_index > 0.7:
                risk_factors.append({
                    "factor": "Yüksek Su Stresi",
                    "level": "high",
                    "description": f"Su stres indeksi: {stress_index:.2f}",
                    "source": water_data.get("data_source", "Water Dataset")
                })
            elif stress_index > 0.4:
                risk_factors.append({
                    "factor": "Orta Su Stresi",
                    "level": "medium",
                    "description": f"Su stres indeksi: {stress_index:.2f}",
                    "source": water_data.get("data_source", "Water Dataset")
                })
    
    # Generate risk factors from drought data
    if drought_data.get("data_available"):
        severity = drought_data.get("drought_severity")
        if severity:
            severity_lower = severity.lower() if isinstance(severity, str) else ""
            if "extreme" in severity_lower or "severe" in severity_lower:
                risk_factors.append({
                    "factor": "Kuraklık Riski",
                    "level": "high",
                    "description": f"Kuraklık şiddeti: {severity}",
                    "source": drought_data.get("data_source", "Drought Dataset")
                })
            elif "moderate" in severity_lower:
                risk_factors.append({
                    "factor": "Kuraklık Riski",
                    "level": "medium",
                    "description": f"Kuraklık şiddeti: {severity}",
                    "source": drought_data.get("data_source", "Drought Dataset")
                })
    
    # Generate recommendations based on data
    if water_data.get("data_available"):
        stress_index = water_data.get("water_stress_index")
        if stress_index is not None and stress_index > 0.5:
            recommendations.append("Su tasarrufu önlemleri alınması önerilir")
            recommendations.append("Damla sulama sistemlerine geçiş değerlendirilmeli")
    
    if drought_data.get("data_available"):
        trend = drought_data.get("historical_trend")
        if trend and "worsening" in str(trend).lower():
            recommendations.append("Uzun vadeli su depolama planlaması yapılmalı")
    
    if agricultural_data.get("data_available"):
        adoption_rate = agricultural_data.get("farmer_adoption_rate")
        if adoption_rate is not None and adoption_rate < 30:
            recommendations.append("Akıllı sulama sistemlerinin yaygınlaştırılması önerilir")
    
    return {
        "water_availability_score": water_availability_score,
        "risk_factors": risk_factors,
        "recommendations": recommendations,
        "data_source": "Regional Data Analysis",
        "data_available": data_available
    }


def get_regional_intelligence(
    lat: float,
    lon: float,
    region_name: Optional[str] = None
) -> Dict:
    """
    Regional Intelligence Layer - Integrates external datasets.
    
    This function loads and processes regional datasets to provide
    comprehensive intelligence for irrigation decisions. It supports
    CSV and JSON datasets and falls back to placeholder data when
    datasets are not available.
    
    Args:
        lat: Latitude of the location
        lon: Longitude of the location
        region_name: Optional region name for more precise matching
        
    Returns:
        Dict with regional intelligence data containing:
        - water_resources: Groundwater, surface water, stress index
        - drought_risk: SPI index, severity, trends
        - agricultural_data: Yield trends, irrigation coverage
        - regional_insights: Composite scores, risk factors, recommendations
        
    Dataset Integration:
        Place your datasets in the ./datasets/ directory:
        - water_resources.csv or water_resources.json
        - drought_risk.csv or drought_risk.json
        - agricultural_data.csv or agricultural_data.json
    """
    # ==================================================================
    # STEP 1: Load datasets
    # ------------------------------------------------------------------
    # Each dataset is loaded independently - missing datasets won't
    # affect other data sources.
    # ==================================================================
    
    water_df = load_regional_dataset("water_resources")
    drought_df = load_regional_dataset("drought_risk")
    agricultural_df = load_regional_dataset("agricultural_data")
    
    # ==================================================================
    # STEP 2: Find matching region in each dataset
    # ------------------------------------------------------------------
    # Uses region_name for exact matching, falls back to lat/lon
    # proximity matching within tolerance.
    # ==================================================================
    
    water_raw = find_region_in_dataset(water_df, lat, lon, region_name)
    drought_raw = find_region_in_dataset(drought_df, lat, lon, region_name)
    agricultural_raw = find_region_in_dataset(agricultural_df, lat, lon, region_name)
    
    # ==================================================================
    # STEP 3: Process raw data into standardized format
    # ------------------------------------------------------------------
    # Each processor handles None values gracefully and returns
    # consistent structure.
    # ==================================================================
    
    water_data = process_water_resources_data(water_raw)
    drought_data = process_drought_risk_data(drought_raw)
    agricultural_data_processed = process_agricultural_data(agricultural_raw)
    
    # ==================================================================
    # STEP 4: Calculate composite insights
    # ------------------------------------------------------------------
    # Synthesizes data from all sources to generate actionable
    # insights and recommendations.
    # ==================================================================
    
    regional_insights = calculate_regional_insights(
        water_data,
        drought_data,
        agricultural_data_processed
    )
    
    # ==================================================================
    # STEP 5: Return unified intelligence structure
    # ------------------------------------------------------------------
    # Output structure is backward-compatible with existing UI and
    # AI strategy components.
    # ==================================================================
    
    return {
        "water_resources": water_data,
        "drought_risk": drought_data,
        "agricultural_data": agricultural_data_processed,
        "regional_insights": regional_insights,
        # Metadata
        "location": {
            "lat": lat,
            "lon": lon,
            "region_name": region_name
        },
        "datasets_loaded": {
            "water_resources": water_df is not None,
            "drought_risk": drought_df is not None,
            "agricultural_data": agricultural_df is not None
        }
    }


def enhance_ai_strategy_with_regional_data(
    base_strategy: Dict,
    regional_intelligence: Dict
) -> Dict:
    """
    Enhance AI strategy with regional intelligence data.
    
    This function integrates regional dataset insights into the AI decision engine.
    When datasets are available, it adjusts strategy recommendations based on:
    - Water stress levels
    - Drought risk conditions
    - Agricultural context
    
    Args:
        base_strategy: Base AI strategy from generate_ai_irrigation_strategy
        regional_intelligence: Regional intelligence data from datasets
        
    Returns:
        Enhanced strategy with regional insights
    """
    enhanced_strategy = base_strategy.copy()
    
    # Initialize regional enhancement tracking
    enhanced_strategy["regional_data_enhanced"] = False
    enhanced_strategy["regional_insights"] = []
    enhanced_strategy["regional_adjustments"] = []
    
    # ==================================================================
    # DATASET INTEGRATION: Water Stress Enhancement
    # ------------------------------------------------------------------
    # When water stress data is available, adjust irrigation strategy
    # based on regional water availability.
    # ==================================================================
    
    water_resources = regional_intelligence.get("water_resources", {})
    if water_resources.get("data_available", False):
        enhanced_strategy["regional_data_enhanced"] = True
        
        water_stress = water_resources.get("water_stress_index")
        if water_stress is not None:
            enhanced_strategy["regional_insights"].append(
                f"Su stres indeksi: {water_stress:.2f}"
            )
            
            # Adjust strategy based on water stress
            if water_stress > 0.7:
                enhanced_strategy["regional_adjustments"].append({
                    "type": "water_conservation",
                    "priority": "high",
                    "reason": "Yüksek su stresi nedeniyle su tasarrufu öncelikli"
                })
            elif water_stress > 0.4:
                enhanced_strategy["regional_adjustments"].append({
                    "type": "water_efficiency",
                    "priority": "medium",
                    "reason": "Orta seviye su stresi - verimlilik önemli"
                })
    
    # ==================================================================
    # DATASET INTEGRATION: Drought Risk Enhancement
    # ------------------------------------------------------------------
    # When drought risk data is available, adjust recommendations
    # based on current and projected drought conditions.
    # ==================================================================
    
    drought_risk = regional_intelligence.get("drought_risk", {})
    if drought_risk.get("data_available", False):
        enhanced_strategy["regional_data_enhanced"] = True
        
        spi_index = drought_risk.get("spi_index")
        severity = drought_risk.get("drought_severity")
        
        if spi_index is not None:
            enhanced_strategy["regional_insights"].append(
                f"SPI indeksi: {spi_index}"
            )
        
        if severity:
            enhanced_strategy["regional_insights"].append(
                f"Kuraklık şiddeti: {severity}"
            )
            
            # Adjust strategy based on drought severity
            severity_lower = str(severity).lower()
            if "extreme" in severity_lower or "severe" in severity_lower:
                enhanced_strategy["regional_adjustments"].append({
                    "type": "drought_response",
                    "priority": "critical",
                    "reason": "Ciddi kuraklık koşulları - acil önlem gerekli"
                })
    
    # ==================================================================
    # DATASET INTEGRATION: Agricultural Context Enhancement
    # ------------------------------------------------------------------
    # When agricultural data is available, provide context-aware
    # recommendations based on regional farming patterns.
    # ==================================================================
    
    agricultural_data = regional_intelligence.get("agricultural_data", {})
    if agricultural_data.get("data_available", False):
        enhanced_strategy["regional_data_enhanced"] = True
        
        irrigation_coverage = agricultural_data.get("irrigation_coverage")
        adoption_rate = agricultural_data.get("farmer_adoption_rate")
        
        if irrigation_coverage is not None:
            enhanced_strategy["regional_insights"].append(
                f"Bölgesel sulama kapsamı: %{irrigation_coverage:.1f}"
            )
        
        if adoption_rate is not None:
            enhanced_strategy["regional_insights"].append(
                f"Akıllı sulama benimsenme oranı: %{adoption_rate:.1f}"
            )
    
    # ==================================================================
    # DATASET INTEGRATION: Watershed / Basin Enhancement
    # ------------------------------------------------------------------
    # When watershed data is available, add basin context and adjust
    # for water-stressed basins (conservation emphasis).
    # ==================================================================
    
    watershed = regional_intelligence.get("watershed", {})
    if watershed.get("data_available", False):
        enhanced_strategy["regional_data_enhanced"] = True
        basin_name = watershed.get("basin_name", "—")
        enhanced_strategy["regional_insights"].append(
            f"Havza: {basin_name}"
        )
        if watershed.get("water_stress_label") == "Yüksek":
            enhanced_strategy["regional_adjustments"].append({
                "type": "basin_conservation",
                "priority": "high",
                "reason": "Havza su stresi yüksek — su tasarrufu öncelikli"
            })
    
    # Add recommendations from regional insights
    regional_recommendations = regional_intelligence.get("regional_insights", {}).get("recommendations", [])
    if regional_recommendations:
        enhanced_strategy["dataset_recommendations"] = regional_recommendations
    
    return enhanced_strategy


def enhance_sustainability_with_regional_data(
    base_metrics: Dict,
    regional_intelligence: Dict
) -> Dict:
    """
    Enhance sustainability metrics with regional intelligence data.
    
    This function integrates regional dataset insights into sustainability scoring.
    When datasets are available, it adjusts scores based on:
    - Regional water availability
    - Drought impact factors
    - Agricultural efficiency metrics
    
    Args:
        base_metrics: Base sustainability metrics from calculate_sustainability_metrics
        regional_intelligence: Regional intelligence data from datasets
        
    Returns:
        Enhanced sustainability metrics with regional context
    """
    enhanced_metrics = base_metrics.copy()
    
    # ==================================================================
    # DATASET INTEGRATION: Regional Context Factors
    # ------------------------------------------------------------------
    # Calculate adjustment factors based on regional data availability.
    # These factors modify the base sustainability score.
    # ==================================================================
    
    water_availability_factor = None
    drought_impact_factor = None
    agricultural_efficiency_factor = None
    basin_stress_factor = None
    
    # Water availability factor (0.5 to 1.5 multiplier)
    water_resources = regional_intelligence.get("water_resources", {})
    if water_resources.get("data_available", False):
        water_stress = water_resources.get("water_stress_index")
        if water_stress is not None:
            # Lower stress = higher availability factor
            water_availability_factor = 1.0 + (0.5 - water_stress)
            water_availability_factor = max(0.5, min(1.5, water_availability_factor))
    
    # Drought impact factor (0.5 to 1.2 multiplier)
    drought_risk = regional_intelligence.get("drought_risk", {})
    if drought_risk.get("data_available", False):
        spi_index = drought_risk.get("spi_index")
        if spi_index is not None:
            # SPI ranges from -3 (extreme drought) to +3 (extremely wet)
            # Normalize to factor
            drought_impact_factor = 1.0 + (spi_index / 6.0)
            drought_impact_factor = max(0.5, min(1.2, drought_impact_factor))
    
    # Agricultural efficiency factor (0.8 to 1.2 multiplier)
    agricultural_data = regional_intelligence.get("agricultural_data", {})
    if agricultural_data.get("data_available", False):
        adoption_rate = agricultural_data.get("farmer_adoption_rate")
        if adoption_rate is not None:
            # Higher adoption = higher efficiency
            agricultural_efficiency_factor = 0.8 + (adoption_rate / 250.0)
            agricultural_efficiency_factor = max(0.8, min(1.2, agricultural_efficiency_factor))
    
    # Basin / watershed stress factor (0.85 when high stress, else 1.0)
    watershed = regional_intelligence.get("watershed", {}) or {}
    if watershed.get("data_available", False) and watershed.get("water_stress_label") == "Yüksek":
        basin_stress_factor = 0.85
    
    # Store regional context
    has_any = any([
        water_availability_factor, drought_impact_factor,
        agricultural_efficiency_factor, basin_stress_factor
    ])
    enhanced_metrics["regional_context"] = {
        "water_availability_factor": water_availability_factor,
        "drought_impact_factor": drought_impact_factor,
        "agricultural_efficiency_factor": agricultural_efficiency_factor,
        "basin_stress_factor": basin_stress_factor,
        "data_source": "Regional Dataset Analysis" if has_any else "Dataset-powered insight (coming from regional data)",
        "data_available": has_any or any([
            water_resources.get("data_available", False),
            drought_risk.get("data_available", False),
            agricultural_data.get("data_available", False),
            watershed.get("data_available", False),
        ])
    }
    
    # ==================================================================
    # DATASET INTEGRATION: Adjust Sustainability Score
    # ------------------------------------------------------------------
    # Apply regional factors to the base sustainability score when
    # dataset information is available.
    # ==================================================================
    
    if enhanced_metrics["regional_context"]["data_available"]:
        base_score = enhanced_metrics.get("sustainability_score", 50)
        
        # Calculate composite adjustment factor
        factors = [f for f in [
            water_availability_factor,
            drought_impact_factor,
            agricultural_efficiency_factor,
            basin_stress_factor,
        ] if f is not None]
        
        if factors:
            composite_factor = sum(factors) / len(factors)
            adjusted_score = base_score * composite_factor
            adjusted_score = max(0, min(100, adjusted_score))
            
            enhanced_metrics["sustainability_score_original"] = base_score
            enhanced_metrics["sustainability_score"] = round(adjusted_score, 1)
            enhanced_metrics["regional_adjustment_applied"] = True
    
    return enhanced_metrics


def get_regional_risk_assessment(
    lat: float,
    lon: float,
    et0: float,
    regional_intelligence: Dict
) -> Dict:
    """
    Get comprehensive regional risk assessment combining weather and dataset insights.
    
    This function synthesizes meteorological data with regional datasets to
    provide a comprehensive risk picture.
    
    Args:
        lat: Latitude of the location
        lon: Longitude of the location
        et0: Current ET0 value from weather data
        regional_intelligence: Regional intelligence data from datasets
        
    Returns:
        Comprehensive risk assessment containing:
        - overall_risk: Composite risk level (low/medium/high)
        - risk_factors: List of individual risk factors with sources
        - regional_data_available: Whether dataset insights are included
    """
    # ==================================================================
    # BASE RISK: Meteorological Conditions
    # ------------------------------------------------------------------
    # Calculate base risk from weather API data (always available).
    # ==================================================================
    
    base_risk = "low"
    if et0 > 5:
        base_risk = "high"
    elif et0 > 3:
        base_risk = "medium"
    
    risk_factors = [
        {
            "factor": "Meteorolojik Koşullar",
            "level": base_risk,
            "source": "Weather API",
            "description": f"Güncel ET0: {et0:.2f} mm"
        }
    ]
    
    # Track if regional data is available
    regional_data_available = False
    risk_scores = [{"level": base_risk, "weight": 1.0}]
    
    # ==================================================================
    # DATASET INTEGRATION: Water Resources Risk
    # ------------------------------------------------------------------
    # Add risk factors from water resources dataset when available.
    # ==================================================================
    
    water_resources = regional_intelligence.get("water_resources", {})
    if water_resources.get("data_available", False):
        regional_data_available = True
        
        groundwater = water_resources.get("groundwater_level")
        water_stress = water_resources.get("water_stress_index")
        
        if water_stress is not None:
            if water_stress > 0.7:
                water_risk = "high"
                weight = 1.2
            elif water_stress > 0.4:
                water_risk = "medium"
                weight = 1.0
            else:
                water_risk = "low"
                weight = 0.8
            
            risk_factors.append({
                "factor": "Su Kaynağı Stresi",
                "level": water_risk,
                "source": water_resources.get("data_source", "Water Dataset"),
                "description": f"Su stres indeksi: {water_stress:.2f}"
            })
            risk_scores.append({"level": water_risk, "weight": weight})
        
        if groundwater is not None:
            risk_factors.append({
                "factor": "Yeraltı Su Seviyesi",
                "level": "info",
                "source": water_resources.get("data_source", "Water Dataset"),
                "description": f"Seviye: {groundwater}"
            })
    
    # ==================================================================
    # DATASET INTEGRATION: Drought Risk
    # ------------------------------------------------------------------
    # Add risk factors from drought risk dataset when available.
    # ==================================================================
    
    drought_risk = regional_intelligence.get("drought_risk", {})
    if drought_risk.get("data_available", False):
        regional_data_available = True
        
        spi_index = drought_risk.get("spi_index")
        severity = drought_risk.get("drought_severity")
        trend = drought_risk.get("historical_trend")
        
        if severity:
            severity_lower = str(severity).lower()
            if "extreme" in severity_lower:
                drought_level = "high"
                weight = 1.5
            elif "severe" in severity_lower:
                drought_level = "high"
                weight = 1.3
            elif "moderate" in severity_lower:
                drought_level = "medium"
                weight = 1.0
            else:
                drought_level = "low"
                weight = 0.8
            
            risk_factors.append({
                "factor": "Kuraklık Durumu",
                "level": drought_level,
                "source": drought_risk.get("data_source", "Drought Dataset"),
                "description": f"Şiddet: {severity}"
            })
            risk_scores.append({"level": drought_level, "weight": weight})
        
        if trend:
            trend_description = f"Trend: {trend}"
            trend_level = "warning" if "worsening" in str(trend).lower() else "info"
            risk_factors.append({
                "factor": "Kuraklık Trendi",
                "level": trend_level,
                "source": drought_risk.get("data_source", "Drought Dataset"),
                "description": trend_description
            })
    
    # ==================================================================
    # DATASET INTEGRATION: Agricultural Risk
    # ------------------------------------------------------------------
    # Add risk factors from agricultural dataset when available.
    # ==================================================================
    
    agricultural_data = regional_intelligence.get("agricultural_data", {})
    if agricultural_data.get("data_available", False):
        regional_data_available = True
        
        irrigation_coverage = agricultural_data.get("irrigation_coverage")
        yield_trend = agricultural_data.get("crop_yield_trend")
        
        if irrigation_coverage is not None:
            risk_factors.append({
                "factor": "Sulama Altyapısı",
                "level": "info",
                "source": agricultural_data.get("data_source", "Agricultural Dataset"),
                "description": f"Kapsam: %{irrigation_coverage:.1f}"
            })
        
        if yield_trend:
            risk_factors.append({
                "factor": "Verim Trendi",
                "level": "info",
                "source": agricultural_data.get("data_source", "Agricultural Dataset"),
                "description": f"Trend: {yield_trend}"
            })
    
    # ==================================================================
    # COMPOSITE RISK CALCULATION
    # ------------------------------------------------------------------
    # Calculate overall risk from weighted individual risk factors.
    # ==================================================================
    
    # Convert risk levels to numeric scores
    level_scores = {"low": 1, "medium": 2, "high": 3}
    
    if risk_scores:
        weighted_sum = sum(
            level_scores.get(r["level"], 2) * r["weight"] 
            for r in risk_scores
        )
        total_weight = sum(r["weight"] for r in risk_scores)
        average_score = weighted_sum / total_weight
        
        if average_score >= 2.5:
            overall_risk = "high"
        elif average_score >= 1.5:
            overall_risk = "medium"
        else:
            overall_risk = "low"
    else:
        overall_risk = base_risk
    
    # Add risk factors from regional insights
    regional_insights = regional_intelligence.get("regional_insights", {})
    insight_risk_factors = regional_insights.get("risk_factors", [])
    if insight_risk_factors:
        risk_factors.extend(insight_risk_factors)
    
    return {
        "overall_risk": overall_risk,
        "base_risk": base_risk,
        "risk_factors": risk_factors,
        "regional_data_available": regional_data_available,
        "data_source": "Composite Analysis" if regional_data_available else "Weather API Only",
        "datasets_integrated": {
            "water_resources": water_resources.get("data_available", False),
            "drought_risk": drought_risk.get("data_available", False),
            "agricultural_data": agricultural_data.get("data_available", False)
        }
    }
