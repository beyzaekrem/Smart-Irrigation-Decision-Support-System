# Regional Datasets Integration Guide

This directory contains regional datasets for the Smart Irrigation Decision Support System.

## Supported Dataset Formats

The system supports **CSV** and **JSON** formats for all datasets.

---

## Dataset Files

### 1. Water Resources Dataset
**Filename:** `water_resources.csv` or `water_resources.json`

#### CSV Format
```csv
region_name,lat,lon,groundwater_level,surface_water_availability,water_stress_index,data_source,last_updated
Konya,37.87,32.49,45.2,Medium,0.65,DSI Water Database,2025-01-15
Ankara,39.93,32.86,52.8,High,0.42,DSI Water Database,2025-01-15
```

#### JSON Format
```json
[
  {
    "region_name": "Konya",
    "lat": 37.87,
    "lon": 32.49,
    "groundwater_level": 45.2,
    "surface_water_availability": "Medium",
    "water_stress_index": 0.65,
    "data_source": "DSI Water Database",
    "last_updated": "2025-01-15"
  }
]
```

#### Field Descriptions
| Field | Type | Description |
|-------|------|-------------|
| `region_name` | String | Name of the region (for matching) |
| `lat` | Float | Latitude coordinate |
| `lon` | Float | Longitude coordinate |
| `groundwater_level` | Float | Groundwater level in meters |
| `surface_water_availability` | String | Low/Medium/High |
| `water_stress_index` | Float | 0.0 (no stress) to 1.0 (extreme stress) |
| `data_source` | String | Source of the data |
| `last_updated` | String | Date of last update (YYYY-MM-DD) |

---

### 2. Drought Risk Dataset
**Filename:** `drought_risk.csv` or `drought_risk.json`

#### CSV Format
```csv
region_name,lat,lon,spi_index,drought_severity,historical_trend,data_source,forecast_period
Konya,37.87,32.49,-1.5,Moderate,Worsening,MGM Drought Monitor,3-month
Ankara,39.93,32.86,0.2,None,Stable,MGM Drought Monitor,3-month
```

#### JSON Format
```json
[
  {
    "region_name": "Konya",
    "lat": 37.87,
    "lon": 32.49,
    "spi_index": -1.5,
    "drought_severity": "Moderate",
    "historical_trend": "Worsening",
    "data_source": "MGM Drought Monitor",
    "forecast_period": "3-month"
  }
]
```

#### Field Descriptions
| Field | Type | Description |
|-------|------|-------------|
| `region_name` | String | Name of the region (for matching) |
| `lat` | Float | Latitude coordinate |
| `lon` | Float | Longitude coordinate |
| `spi_index` | Float | Standardized Precipitation Index (-3 to +3) |
| `drought_severity` | String | None/Mild/Moderate/Severe/Extreme |
| `historical_trend` | String | Improving/Stable/Worsening |
| `data_source` | String | Source of the data |
| `forecast_period` | String | Forecast period (e.g., "3-month") |

#### SPI Index Reference
| SPI Value | Category |
|-----------|----------|
| ≥ 2.0 | Extremely Wet |
| 1.5 to 1.99 | Very Wet |
| 1.0 to 1.49 | Moderately Wet |
| -0.99 to 0.99 | Near Normal |
| -1.0 to -1.49 | Moderately Dry |
| -1.5 to -1.99 | Severely Dry |
| ≤ -2.0 | Extremely Dry |

---

### 3. Agricultural Data Dataset
**Filename:** `agricultural_data.csv` or `agricultural_data.json`

#### CSV Format
```csv
region_name,lat,lon,crop_yield_trend,irrigation_coverage,farmer_adoption_rate,dominant_crop,total_agricultural_area,data_source
Konya,37.87,32.49,Stable,72.5,28.3,Wheat,1250000,TUIK Agricultural Statistics
Ankara,39.93,32.86,Increasing,65.2,35.1,Barley,850000,TUIK Agricultural Statistics
```

#### JSON Format
```json
[
  {
    "region_name": "Konya",
    "lat": 37.87,
    "lon": 32.49,
    "crop_yield_trend": "Stable",
    "irrigation_coverage": 72.5,
    "farmer_adoption_rate": 28.3,
    "dominant_crop": "Wheat",
    "total_agricultural_area": 1250000,
    "data_source": "TUIK Agricultural Statistics"
  }
]
```

#### Field Descriptions
| Field | Type | Description |
|-------|------|-------------|
| `region_name` | String | Name of the region (for matching) |
| `lat` | Float | Latitude coordinate |
| `lon` | Float | Longitude coordinate |
| `crop_yield_trend` | String | Increasing/Stable/Decreasing |
| `irrigation_coverage` | Float | Percentage of irrigated land (0-100) |
| `farmer_adoption_rate` | Float | Smart irrigation adoption rate (0-100) |
| `dominant_crop` | String | Main crop in the region |
| `total_agricultural_area` | Float | Total agricultural area in hectares |
| `data_source` | String | Source of the data |

---

## Location Matching

The system matches locations in the following order:

1. **Region Name Match** (if `region_name` provided)
   - Case-insensitive partial match
   - Example: "Konya" matches "Konya İli"

2. **Geographic Proximity** (fallback)
   - Matches nearest location within 0.5 degree tolerance
   - Uses Euclidean distance calculation

---

## Integration Steps

1. **Prepare your datasets** following the formats above
2. **Place files** in this directory (`datasets/`)
3. **Name files correctly:**
   - `water_resources.csv` or `water_resources.json`
   - `drought_risk.csv` or `drought_risk.json`
   - `agricultural_data.csv` or `agricultural_data.json`
4. **Restart the application** to load new datasets

---

## Troubleshooting

### Dataset not loading?
- Check file names match exactly (case-sensitive)
- Verify CSV/JSON format is valid
- Check for encoding issues (use UTF-8)

### Region not found?
- Ensure `region_name` or `lat`/`lon` columns exist
- Check coordinate tolerance (default: 0.5 degrees)
- Verify coordinate format (decimal degrees)

### Missing data showing?
- Check field names match exactly
- Verify data types (numbers should not be quoted in CSV)
- Ensure no extra whitespace in values

---

## Sample Data Files

For testing, you can use the sample data files:
- `sample_water_resources.csv`
- `sample_drought_risk.csv`
- `sample_agricultural_data.csv`

Rename these files (remove "sample_" prefix) to activate them.
