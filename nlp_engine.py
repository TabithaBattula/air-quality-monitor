from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import re


LOCATION_ALIASES = {
    "vizag": {"name": "Visakhapatnam", "lat": 17.6868, "lon": 83.2185},
    "visakhapatnam": {"name": "Visakhapatnam", "lat": 17.6868, "lon": 83.2185},
    "delhi": {"name": "Delhi", "lat": 28.6139, "lon": 77.2090},
    "new delhi": {"name": "Delhi", "lat": 28.6139, "lon": 77.2090},
    "mumbai": {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    "bombay": {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    "kolkata": {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639},
    "calcutta": {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639},
    "chennai": {"name": "Chennai", "lat": 13.0827, "lon": 80.2707},
    "madras": {"name": "Chennai", "lat": 13.0827, "lon": 80.2707},
    "bengaluru": {"name": "Bengaluru", "lat": 12.9716, "lon": 77.5946},
    "bangalore": {"name": "Bengaluru", "lat": 12.9716, "lon": 77.5946},
    "hyderabad": {"name": "Hyderabad", "lat": 17.3850, "lon": 78.4867},
    "ahmedabad": {"name": "Ahmedabad", "lat": 23.0225, "lon": 72.5714},
    "pune": {"name": "Pune", "lat": 18.5204, "lon": 73.8567},
    "jaipur": {"name": "Jaipur", "lat": 26.9124, "lon": 75.7873},
    "lucknow": {"name": "Lucknow", "lat": 26.8467, "lon": 80.9462},
    "kanpur": {"name": "Kanpur", "lat": 26.4499, "lon": 80.3319},
    "nagpur": {"name": "Nagpur", "lat": 21.1458, "lon": 79.0882},
    "patna": {"name": "Patna", "lat": 25.5941, "lon": 85.1376},
    "indore": {"name": "Indore", "lat": 22.7196, "lon": 75.8577},
    "bhopal": {"name": "Bhopal", "lat": 23.2599, "lon": 77.4126},
    "surat": {"name": "Surat", "lat": 21.1702, "lon": 72.8311},
    "varanasi": {"name": "Varanasi", "lat": 25.3176, "lon": 82.9739},
    "agra": {"name": "Agra", "lat": 27.1767, "lon": 78.0081},
    "goa": {"name": "Goa", "lat": 15.2993, "lon": 74.1240},
    "kochi": {"name": "Kochi", "lat": 9.9312, "lon": 76.2673},
    "cochin": {"name": "Kochi", "lat": 9.9312, "lon": 76.2673},
    "thiruvananthapuram": {"name": "Thiruvananthapuram", "lat": 8.5241, "lon": 76.9366},
    "trivandrum": {"name": "Thiruvananthapuram", "lat": 8.5241, "lon": 76.9366},
    "guwahati": {"name": "Guwahati", "lat": 26.1445, "lon": 91.7362},
    "chandigarh": {"name": "Chandigarh", "lat": 30.7333, "lon": 76.7794},
    "shimla": {"name": "Shimla", "lat": 31.1048, "lon": 77.1734},
    "dehradun": {"name": "Dehradun", "lat": 30.3165, "lon": 78.0322},
    "srinagar": {"name": "Srinagar", "lat": 34.0837, "lon": 74.7973},
    "amritsar": {"name": "Amritsar", "lat": 31.6340, "lon": 74.8723},
    "ranchi": {"name": "Ranchi", "lat": 23.3441, "lon": 85.3096},
    "bhubaneswar": {"name": "Bhubaneswar", "lat": 20.2961, "lon": 85.8245},
    "raipur": {"name": "Raipur", "lat": 21.2514, "lon": 81.6296},
    "coimbatore": {"name": "Coimbatore", "lat": 11.0168, "lon": 76.9558},
    "mysore": {"name": "Mysuru", "lat": 12.2958, "lon": 76.6394},
    "mysuru": {"name": "Mysuru", "lat": 12.2958, "lon": 76.6394},
    "noida": {"name": "Noida", "lat": 28.5355, "lon": 77.3910},
    "gurgaon": {"name": "Gurugram", "lat": 28.4595, "lon": 77.0266},
    "gurugram": {"name": "Gurugram", "lat": 28.4595, "lon": 77.0266},
    "faridabad": {"name": "Faridabad", "lat": 28.4089, "lon": 77.3178},
    "ghaziabad": {"name": "Ghaziabad", "lat": 28.6692, "lon": 77.4538},
}

LAYER_KEYWORDS = {
    "flood": ["flood", "flooding", "flood risk", "flood zone", "inundation", "water level"],
    "river": ["river", "rivers", "stream", "waterway", "water body"],
    "roads": ["road", "roads", "highway", "highways", "street", "streets", "route"],
    "landuse": ["land use", "landuse", "land cover", "urban", "forest", "agriculture"],
    "pollution": ["pollution", "air quality", "aqi", "pm2.5", "pm25", "air pollution", "smog"],
    "temperature": ["temperature", "temp", "heat", "hot", "cold", "thermal"],
    "rainfall": ["rain", "rainfall", "precipitation", "monsoon"],
    "elevation": ["elevation", "height", "terrain", "topography", "altitude"],
}

INTENT_PATTERNS = {
    "show_layer": [
        r"show\s+(?:me\s+)?(.+?)(?:\s+in\s+|\s+for\s+|\s+at\s+|\s+near\s+)?(.+)?",
        r"display\s+(.+?)(?:\s+in\s+|\s+for\s+|\s+at\s+)?(.+)?",
        r"what(?:'s| is)\s+the\s+(.+?)(?:\s+in\s+|\s+for\s+|\s+at\s+)?(.+)?",
        r"find\s+(.+?)(?:\s+in\s+|\s+for\s+|\s+at\s+)?(.+)?",
    ],
    "navigate": [
        r"go\s+to\s+(.+)",
        r"fly\s+to\s+(.+)",
        r"zoom\s+to\s+(.+)",
        r"navigate\s+to\s+(.+)",
        r"take\s+me\s+to\s+(.+)",
        r"show\s+me\s+(.+)$",
    ],
    "zoom_in": [r"zoom\s+in", r"closer", r"magnify"],
    "zoom_out": [r"zoom\s+out", r"farther", r"wider view"],
    "reset": [r"reset", r"clear", r"start over", r"default view"],
}


@dataclass
class ParsedQuery:
    intent: str
    location: Optional[Dict[str, Any]]
    layer: Optional[str]
    raw_query: str
    confidence: float


def extract_location(text: str) -> Optional[Dict[str, Any]]:
    text_lower = text.lower().strip()
    
    for alias, data in LOCATION_ALIASES.items():
        if alias in text_lower:
            return data
    
    return None


def extract_layer(text: str) -> Optional[str]:
    text_lower = text.lower()
    
    for layer_id, keywords in LAYER_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return layer_id
    
    return None


def parse_query(query: str) -> ParsedQuery:
    query_lower = query.lower().strip()
    
    for intent_name, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                location = extract_location(query)
                layer = extract_layer(query)
                
                if intent_name == "navigate" and not location:
                    groups = match.groups()
                    if groups:
                        location = extract_location(groups[0])
                
                if intent_name == "show_layer":
                    groups = match.groups()
                    if groups:
                        if not layer and groups[0]:
                            layer = extract_layer(groups[0])
                        if not location and len(groups) > 1 and groups[1]:
                            location = extract_location(groups[1])
                
                if not layer and ("pollution" in query_lower or "air" in query_lower or "pm" in query_lower):
                    layer = "pollution"
                
                confidence = 0.9 if (location or layer) else 0.6
                
                return ParsedQuery(
                    intent=intent_name,
                    location=location,
                    layer=layer,
                    raw_query=query,
                    confidence=confidence
                )
    
    location = extract_location(query)
    layer = extract_layer(query)
    
    if location or layer:
        return ParsedQuery(
            intent="show_layer" if layer else "navigate",
            location=location,
            layer=layer,
            raw_query=query,
            confidence=0.7
        )
    
    return ParsedQuery(
        intent="unknown",
        location=None,
        layer=None,
        raw_query=query,
        confidence=0.3
    )


def get_response_message(parsed: ParsedQuery) -> str:
    if parsed.intent == "unknown":
        return "I didn't understand that. Try 'Show flood risk in Mumbai' or 'Go to Delhi'."
    
    if parsed.intent == "zoom_in":
        return "Zooming in..."
    
    if parsed.intent == "zoom_out":
        return "Zooming out..."
    
    if parsed.intent == "reset":
        return "Resetting map to default view..."
    
    if parsed.intent == "navigate":
        if parsed.location:
            return f"Flying to {parsed.location['name']}..."
        return "Please specify a location to navigate to."
    
    if parsed.intent == "show_layer":
        parts = []
        if parsed.layer:
            layer_names = {
                "flood": "flood risk data",
                "river": "rivers and water bodies",
                "roads": "road network",
                "landuse": "land use map",
                "pollution": "air pollution levels",
                "temperature": "temperature data",
                "rainfall": "rainfall data",
                "elevation": "elevation map",
            }
            parts.append(f"Loading {layer_names.get(parsed.layer, parsed.layer)}")
        
        if parsed.location:
            parts.append(f"for {parsed.location['name']}")
        
        if parts:
            return " ".join(parts) + "..."
        return "What data would you like to see?"
    
    return "Processing your request..."
