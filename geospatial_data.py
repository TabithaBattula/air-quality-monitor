from typing import Dict, List, Any
import random


DEMO_LAYERS = {
    "flood": {
        "id": "flood",
        "name": "Flood Risk Zones",
        "description": "Areas at risk of flooding based on elevation and proximity to water bodies",
        "color": "#ef4444",
        "opacity": 0.6,
        "type": "polygon",
    },
    "river": {
        "id": "river",
        "name": "Rivers & Water Bodies",
        "description": "Major rivers, streams, and water bodies",
        "color": "#3b82f6",
        "opacity": 0.8,
        "type": "line",
    },
    "roads": {
        "id": "roads",
        "name": "Road Network",
        "description": "Major highways and roads",
        "color": "#f59e0b",
        "opacity": 0.7,
        "type": "line",
    },
    "landuse": {
        "id": "landuse",
        "name": "Land Use",
        "description": "Urban, forest, agricultural, and other land use categories",
        "color": "#22c55e",
        "opacity": 0.5,
        "type": "polygon",
    },
    "pollution": {
        "id": "pollution",
        "name": "Air Pollution",
        "description": "PM2.5 concentration levels from satellite and ground data",
        "color": "#8b5cf6",
        "opacity": 0.6,
        "type": "heatmap",
    },
}

CITY_FEATURES = {
    "Visakhapatnam": {
        "flood": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Coastal Flood Zone", "risk": "high"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [83.15, 17.65], [83.30, 17.65], [83.30, 17.72],
                            [83.15, 17.72], [83.15, 17.65]
                        ]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {"name": "River Flood Plain", "risk": "medium"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [83.20, 17.70], [83.28, 17.70], [83.28, 17.75],
                            [83.20, 17.75], [83.20, 17.70]
                        ]]
                    }
                }
            ]
        },
        "river": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Gosthani River"},
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[83.10, 17.80], [83.20, 17.72], [83.25, 17.68], [83.30, 17.65]]
                    }
                }
            ]
        }
    },
    "Mumbai": {
        "flood": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Low-lying Areas", "risk": "high"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [72.82, 19.00], [72.92, 19.00], [72.92, 19.10],
                            [72.82, 19.10], [72.82, 19.00]
                        ]]
                    }
                }
            ]
        },
        "river": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Mithi River"},
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[72.85, 19.15], [72.87, 19.10], [72.88, 19.05], [72.90, 19.02]]
                    }
                }
            ]
        }
    },
    "Delhi": {
        "flood": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Yamuna Flood Plain", "risk": "high"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [77.20, 28.55], [77.28, 28.55], [77.28, 28.70],
                            [77.20, 28.70], [77.20, 28.55]
                        ]]
                    }
                }
            ]
        },
        "river": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Yamuna River"},
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[77.22, 28.75], [77.24, 28.65], [77.25, 28.55], [77.26, 28.45]]
                    }
                }
            ]
        }
    },
    "Chennai": {
        "flood": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Adyar River Basin", "risk": "high"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [80.22, 13.00], [80.30, 13.00], [80.30, 13.08],
                            [80.22, 13.08], [80.22, 13.00]
                        ]]
                    }
                }
            ]
        },
        "river": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Adyar River"},
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[80.15, 13.05], [80.22, 13.03], [80.27, 13.01], [80.28, 13.00]]
                    }
                }
            ]
        }
    },
    "Kolkata": {
        "flood": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Hooghly Basin", "risk": "medium"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [88.30, 22.50], [88.40, 22.50], [88.40, 22.62],
                            [88.30, 22.62], [88.30, 22.50]
                        ]]
                    }
                }
            ]
        },
        "river": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Hooghly River"},
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[88.32, 22.70], [88.34, 22.60], [88.35, 22.55], [88.36, 22.48]]
                    }
                }
            ]
        }
    }
}


def get_available_layers() -> List[Dict[str, Any]]:
    return list(DEMO_LAYERS.values())


def get_layer_info(layer_id: str) -> Dict[str, Any]:
    return DEMO_LAYERS.get(layer_id)


def get_layer_data(layer_id: str, city_name: str = None) -> Dict[str, Any]:
    if city_name and city_name in CITY_FEATURES:
        city_data = CITY_FEATURES[city_name]
        if layer_id in city_data:
            return city_data[layer_id]
    
    return generate_generic_layer(layer_id, city_name)


def generate_generic_layer(layer_id: str, city_name: str = None) -> Dict[str, Any]:
    from nlp_engine import LOCATION_ALIASES
    
    center_lat, center_lon = 20.5937, 78.9629
    
    if city_name:
        city_lower = city_name.lower()
        if city_lower in LOCATION_ALIASES:
            center_lat = LOCATION_ALIASES[city_lower]["lat"]
            center_lon = LOCATION_ALIASES[city_lower]["lon"]
    
    random.seed(hash(f"{layer_id}{city_name}"))
    
    features = []
    
    if layer_id == "flood":
        for i in range(2):
            offset_lat = random.uniform(-0.05, 0.05)
            offset_lon = random.uniform(-0.05, 0.05)
            size = random.uniform(0.02, 0.05)
            
            features.append({
                "type": "Feature",
                "properties": {
                    "name": f"Flood Zone {i+1}",
                    "risk": random.choice(["low", "medium", "high"])
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [center_lon + offset_lon, center_lat + offset_lat],
                        [center_lon + offset_lon + size, center_lat + offset_lat],
                        [center_lon + offset_lon + size, center_lat + offset_lat + size],
                        [center_lon + offset_lon, center_lat + offset_lat + size],
                        [center_lon + offset_lon, center_lat + offset_lat]
                    ]]
                }
            })
    
    elif layer_id == "river":
        features.append({
            "type": "Feature",
            "properties": {"name": "River"},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [center_lon - 0.1, center_lat + 0.1],
                    [center_lon - 0.05, center_lat + 0.05],
                    [center_lon, center_lat],
                    [center_lon + 0.05, center_lat - 0.03],
                    [center_lon + 0.1, center_lat - 0.05]
                ]
            }
        })
    
    elif layer_id == "roads":
        for i in range(3):
            start_lat = center_lat + random.uniform(-0.1, 0.1)
            start_lon = center_lon + random.uniform(-0.1, 0.1)
            
            features.append({
                "type": "Feature",
                "properties": {"name": f"Highway {i+1}", "type": "highway"},
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [start_lon, start_lat],
                        [start_lon + 0.05, start_lat + 0.02],
                        [start_lon + 0.1, start_lat + 0.01]
                    ]
                }
            })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }
