import os
from datetime import datetime, timedelta
from typing import Optional, List
from contextlib import asynccontextmanager

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MERRA2_DIR = os.path.join(BASE_DIR, 'merra2_data')
CPCB_FILE = os.path.join(MERRA2_DIR, 'cpcb_ground_latest.csv')

CITIES = {
    "delhi": {"lat": 28.6139, "lon": 77.2090, "display_name": "Delhi"},
    "new delhi": {"lat": 28.6139, "lon": 77.2090, "display_name": "New Delhi"},
    "mumbai": {"lat": 19.0760, "lon": 72.8777, "display_name": "Mumbai"},
    "kolkata": {"lat": 22.5726, "lon": 88.3639, "display_name": "Kolkata"},
    "chennai": {"lat": 13.0827, "lon": 80.2707, "display_name": "Chennai"},
    "bengaluru": {"lat": 12.9716, "lon": 77.5946, "display_name": "Bengaluru"},
    "bangalore": {"lat": 12.9716, "lon": 77.5946, "display_name": "Bangalore"},
    "hyderabad": {"lat": 17.3850, "lon": 78.4867, "display_name": "Hyderabad"},
    "pune": {"lat": 18.5204, "lon": 73.8567, "display_name": "Pune"},
    "ahmedabad": {"lat": 23.0225, "lon": 72.5714, "display_name": "Ahmedabad"},
    "jaipur": {"lat": 26.9124, "lon": 75.7873, "display_name": "Jaipur"},
    "lucknow": {"lat": 26.8467, "lon": 80.9462, "display_name": "Lucknow"},
    "kanpur": {"lat": 26.4499, "lon": 80.3319, "display_name": "Kanpur"},
    "nagpur": {"lat": 21.1458, "lon": 79.0882, "display_name": "Nagpur"},
    "patna": {"lat": 25.5941, "lon": 85.1376, "display_name": "Patna"},
    "indore": {"lat": 22.7196, "lon": 75.8577, "display_name": "Indore"},
    "bhopal": {"lat": 23.2599, "lon": 77.4126, "display_name": "Bhopal"},
    "visakhapatnam": {"lat": 17.6868, "lon": 83.2185, "display_name": "Visakhapatnam"},
    "vadodara": {"lat": 22.3072, "lon": 73.1812, "display_name": "Vadodara"},
    "ludhiana": {"lat": 30.9010, "lon": 75.8573, "display_name": "Ludhiana"},
    "agra": {"lat": 27.1767, "lon": 78.0081, "display_name": "Agra"},
    "varanasi": {"lat": 25.3176, "lon": 82.9739, "display_name": "Varanasi"},
    "surat": {"lat": 21.1702, "lon": 72.8311, "display_name": "Surat"},
    "chandigarh": {"lat": 30.7333, "lon": 76.7794, "display_name": "Chandigarh"},
    "gurgaon": {"lat": 28.4595, "lon": 77.0266, "display_name": "Gurgaon"},
    "gurugram": {"lat": 28.4595, "lon": 77.0266, "display_name": "Gurugram"},
    "noida": {"lat": 28.5355, "lon": 77.3910, "display_name": "Noida"},
    "ghaziabad": {"lat": 28.6692, "lon": 77.4538, "display_name": "Ghaziabad"},
    "faridabad": {"lat": 28.4089, "lon": 77.3178, "display_name": "Faridabad"},
    "amritsar": {"lat": 31.6340, "lon": 74.8723, "display_name": "Amritsar"},
    "ranchi": {"lat": 23.3441, "lon": 85.3096, "display_name": "Ranchi"},
    "coimbatore": {"lat": 11.0168, "lon": 76.9558, "display_name": "Coimbatore"},
    "guwahati": {"lat": 26.1445, "lon": 91.7362, "display_name": "Guwahati"},
    "bhubaneswar": {"lat": 20.2961, "lon": 85.8245, "display_name": "Bhubaneswar"},
    "thiruvananthapuram": {"lat": 8.5241, "lon": 76.9366, "display_name": "Thiruvananthapuram"},
    "kochi": {"lat": 9.9312, "lon": 76.2673, "display_name": "Kochi"},
    "mysuru": {"lat": 12.2958, "lon": 76.6394, "display_name": "Mysuru"},
    "mysore": {"lat": 12.2958, "lon": 76.6394, "display_name": "Mysore"},
    "jodhpur": {"lat": 26.2389, "lon": 73.0243, "display_name": "Jodhpur"},
    "raipur": {"lat": 21.2514, "lon": 81.6296, "display_name": "Raipur"},
    "dehradun": {"lat": 30.3165, "lon": 78.0322, "display_name": "Dehradun"},
    "shimla": {"lat": 31.1048, "lon": 77.1734, "display_name": "Shimla"},
    "srinagar": {"lat": 34.0837, "lon": 74.7973, "display_name": "Srinagar"},
}

def get_unique_cities():
    seen_coords = set()
    unique = []
    for key, data in CITIES.items():
        coord_key = (data["lat"], data["lon"])
        if coord_key not in seen_coords:
            seen_coords.add(coord_key)
            unique.append({
                "name": data["display_name"],
                "lat": data["lat"],
                "lon": data["lon"]
            })
    return sorted(unique, key=lambda x: x["name"])

UNIQUE_CITIES = get_unique_cities()

class City(BaseModel):
    name: str
    lat: float
    lon: float

class PollutionData(BaseModel):
    city: str
    lat: float
    lon: float
    pm25: float
    aqi_category: str
    aqi_color: str
    health_advice: str

class ForecastDay(BaseModel):
    date: str
    day_name: str
    pm25: float
    aqi_category: str
    aqi_color: str
    trend: str  # "rising", "falling", "stable"
    confidence: float

class ForecastResponse(BaseModel):
    city: str
    lat: float
    lon: float
    forecast: List[ForecastDay]

model_state = {
    "model": None,
    "feature_cols": None,
    "daily_mean": None,
    "merra_vars": None,
    "loaded": False
}

def get_seasonal_factor(date: datetime, lat: float) -> float:
    month = date.month

    if month in [11, 12, 1]:  # Peak winter
        if lat > 24:  # North India
            return 1.35
        return 1.1
    elif month in [10, 2]:  # Early/late winter
        if lat > 24:
            return 1.2
        return 1.05
    elif month in [6, 7, 8, 9]:  # Monsoon
        return 0.7
    elif month in [3, 4, 5]:  # Summer
        return 0.9
    return 1.0

def get_weather_trend_factor(days_ahead: int, seed: int) -> float:
    np.random.seed(seed)
    base_trend = np.sin(days_ahead * 0.3) * 0.15
    noise = np.random.normal(0, 0.05)
    return 1.0 + base_trend + noise

def get_aqi_category(pm25: float) -> tuple[str, str]:
    if pm25 <= 30:
        return "Good", "#10b981"
    elif pm25 <= 60:
        return "Satisfactory", "#84cc16"
    elif pm25 <= 90:
        return "Moderate", "#f59e0b"
    elif pm25 <= 120:
        return "Poor", "#f97316"
    elif pm25 <= 250:
        return "Very Poor", "#ef4444"
    else:
        return "Severe", "#475569"

def get_health_advice(pm25: float) -> str:
    if pm25 <= 30:
        return "Air quality is excellent. Perfect for outdoor activities!"
    elif pm25 <= 60:
        return "Air quality is acceptable. Sensitive individuals should limit prolonged outdoor exertion."
    elif pm25 <= 90:
        return "Sensitive groups may experience respiratory symptoms. Consider reducing outdoor activities."
    elif pm25 <= 120:
        return "Everyone may begin to experience health effects. Limit outdoor activities."
    elif pm25 <= 250:
        return "Health alert! Everyone should avoid prolonged outdoor exertion."
    else:
        return "Health emergency! Avoid all outdoor activities. Stay indoors with air purification."

def load_model():
    try:
        from sklearn.ensemble import RandomForestRegressor
        import xarray as xr
    except ImportError:
        model_state["loaded"] = True
        return

    try:
        stations_df = pd.read_csv(CPCB_FILE)
    except FileNotFoundError:
        model_state["loaded"] = True
        return

    merra2_ds = None
    daily_mean = None
    merra_vars = []

    for root, dirs, files in os.walk(MERRA2_DIR):
        for f in files:
            if f.endswith('.nc4'):
                try:
                    merra2_ds = xr.open_dataset(os.path.join(root, f))
                    break
                except:
                    pass
        if merra2_ds is not None:
            break

    if merra2_ds is not None:
        daily_mean = merra2_ds.mean(dim='time')
        merra_vars = list(daily_mean.data_vars)[:10]

    records = []
    for _, row in stations_df.iterrows():
        lat, lon = row['lat'], row['lon']
        feat = {
            'lat': lat, 'lon': lon, 'pm25_value': row['pm25_value'],
            'lat_norm': (lat - 6.5) / 31, 'lon_norm': (lon - 68) / 29.5,
            'dist_delhi': np.sqrt((lat - 28.6139)**2 + (lon - 77.209)**2),
            'indo_gangetic': int((24 < lat < 31) and (74 < lon < 88)),
            'coastal': int((lat < 15) or ((lon < 74) and (lat < 25)))
        }

        if daily_mean is not None:
            try:
                point = daily_mean.sel(lat=lat, lon=lon, method='nearest')
                for var in merra_vars:
                    try:
                        val = float(point[var].values)
                        if not np.isnan(val):
                            feat[var] = val
                    except:
                        pass
            except:
                pass

        records.append(feat)

    df = pd.DataFrame(records)
    feature_cols = [c for c in df.columns if c not in ['pm25_value']]

    X = df[feature_cols].fillna(0).values
    y = df['pm25_value'].values

    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X, y)

    model_state["model"] = model
    model_state["feature_cols"] = feature_cols
    model_state["daily_mean"] = daily_mean
    model_state["merra_vars"] = merra_vars
    model_state["loaded"] = True

def predict_pollution(lat: float, lon: float, date: datetime = None) -> float:
    if date is None:
        date = datetime.now()

    if model_state["model"] is None:
        dist_delhi = np.sqrt((lat - 28.6139)**2 + (lon - 77.209)**2)
        indo_gangetic = (24 < lat < 31) and (74 < lon < 88)
        coastal = (lat < 15) or ((lon < 74) and (lat < 25))

        if indo_gangetic:
            base = 150
        elif dist_delhi < 3:
            base = 170
        elif coastal:
            base = 40
        elif lat < 20:
            base = 50
        else:
            base = 85
    else:
        feat = {
            'lat': lat, 'lon': lon,
            'lat_norm': (lat - 6.5) / 31, 'lon_norm': (lon - 68) / 29.5,
            'dist_delhi': np.sqrt((lat - 28.6139)**2 + (lon - 77.209)**2),
            'indo_gangetic': int((24 < lat < 31) and (74 < lon < 88)),
            'coastal': int((lat < 15) or ((lon < 74) and (lat < 25)))
        }

        if model_state["daily_mean"] is not None:
            try:
                point = model_state["daily_mean"].sel(lat=lat, lon=lon, method='nearest')
                for var in model_state["merra_vars"]:
                    try:
                        val = float(point[var].values)
                        if not np.isnan(val):
                            feat[var] = val
                    except:
                        pass
            except:
                pass

        X = np.array([[feat.get(c, 0) for c in model_state["feature_cols"]]])
        base = model_state["model"].predict(X)[0]

    seasonal = get_seasonal_factor(date, lat)
    pm25 = base * seasonal

    return max(10, min(350, pm25))

def predict_forecast(lat: float, lon: float, days: int = 7) -> List[dict]:
    today = datetime.now()
    forecast = []

    seed = int(abs(lat * 100 + lon * 100))

    prev_pm25 = None
    for i in range(days):
        date = today + timedelta(days=i)

        base_pm25 = predict_pollution(lat, lon, date)

        trend_factor = get_weather_trend_factor(i, seed + date.day)
        pm25 = base_pm25 * trend_factor
        pm25 = max(10, min(350, pm25))

        if prev_pm25 is None:
            trend = "stable"
        elif pm25 > prev_pm25 * 1.05:
            trend = "rising"
        elif pm25 < prev_pm25 * 0.95:
            trend = "falling"
        else:
            trend = "stable"

        confidence = max(0.5, 1.0 - (i * 0.07))

        aqi_category, aqi_color = get_aqi_category(pm25)

        forecast.append({
            "date": date.strftime("%Y-%m-%d"),
            "day_name": "Today" if i == 0 else ("Tomorrow" if i == 1 else date.strftime("%a")),
            "pm25": round(pm25, 1),
            "aqi_category": aqi_category,
            "aqi_color": aqi_color,
            "trend": trend,
            "confidence": round(confidence, 2)
        })

        prev_pm25 = pm25

    return forecast

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading ML model...")
    load_model()
    print("Model loaded!" if model_state["model"] else "Using regional estimates")
    yield

app = FastAPI(
    title="Air Pollution Forecast API",
    description="ML-powered air pollution predictions and forecasts for Indian cities",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Air Pollution Forecast API", "version": "2.0"}

@app.get("/api/cities", response_model=List[City])
def get_cities():
    return UNIQUE_CITIES

@app.get("/api/predict/{city_name}", response_model=PollutionData)
def get_prediction(city_name: str):
    city_lower = city_name.lower().strip()

    if city_lower in CITIES:
        city_data = CITIES[city_lower]
    else:
        matched = None
        for key, data in CITIES.items():
            if city_lower in key or key in city_lower:
                matched = data
                break
        if matched is None:
            raise HTTPException(status_code=404, detail=f"City '{city_name}' not found")
        city_data = matched

    lat, lon = city_data["lat"], city_data["lon"]
    pm25 = predict_pollution(lat, lon)
    aqi_category, aqi_color = get_aqi_category(pm25)
    health_advice = get_health_advice(pm25)

    return PollutionData(
        city=city_data["display_name"],
        lat=lat,
        lon=lon,
        pm25=round(pm25, 1),
        aqi_category=aqi_category,
        aqi_color=aqi_color,
        health_advice=health_advice
    )

@app.get("/api/forecast/{city_name}", response_model=ForecastResponse)
def get_forecast(city_name: str, days: int = Query(default=7, ge=1, le=14)):
    city_lower = city_name.lower().strip()

    if city_lower in CITIES:
        city_data = CITIES[city_lower]
    else:
        matched = None
        for key, data in CITIES.items():
            if city_lower in key or key in city_lower:
                matched = data
                break
        if matched is None:
            raise HTTPException(status_code=404, detail=f"City '{city_name}' not found")
        city_data = matched

    lat, lon = city_data["lat"], city_data["lon"]
    forecast = predict_forecast(lat, lon, days)

    return ForecastResponse(
        city=city_data["display_name"],
        lat=lat,
        lon=lon,
        forecast=forecast
    )

@app.get("/api/predict-coords")
def get_prediction_by_coords(lat: float, lon: float):
    if not (6.5 <= lat <= 37.5 and 68 <= lon <= 97.5):
        raise HTTPException(status_code=400, detail="Coordinates outside India bounds")

    pm25 = predict_pollution(lat, lon)
    aqi_category, aqi_color = get_aqi_category(pm25)
    health_advice = get_health_advice(pm25)

    return {
        "lat": lat,
        "lon": lon,
        "pm25": round(pm25, 1),
        "aqi_category": aqi_category,
        "aqi_color": aqi_color,
        "health_advice": health_advice
    }

class NLPQueryRequest(BaseModel):
    query: str

class NLPQueryResponse(BaseModel):
    intent: str
    location: Optional[dict]
    layer: Optional[str]
    message: str
    confidence: float

@app.post("/api/nlp/query", response_model=NLPQueryResponse)
def process_nlp_query(request: NLPQueryRequest):
    from nlp_engine import parse_query, get_response_message
    
    parsed = parse_query(request.query)
    message = get_response_message(parsed)
    
    return NLPQueryResponse(
        intent=parsed.intent,
        location=parsed.location,
        layer=parsed.layer,
        message=message,
        confidence=parsed.confidence
    )

@app.get("/api/layers")
def get_layers():
    from geospatial_data import get_available_layers
    return get_available_layers()

@app.get("/api/layers/{layer_id}")
def get_layer_data(layer_id: str, city: Optional[str] = None):
    from geospatial_data import get_layer_data as fetch_layer, get_layer_info
    
    layer_info = get_layer_info(layer_id)
    if not layer_info:
        raise HTTPException(status_code=404, detail=f"Layer '{layer_id}' not found")
    
    geojson = fetch_layer(layer_id, city)
    
    return {
        "layer": layer_info,
        "data": geojson
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

