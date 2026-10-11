import requests
import json
import math
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def get_elevation_and_terrain(latitude: float, longitude: float):
    """
    Retrieves elevation and computes local topographic slope and ridge exposure.
    Uses multi-point sampling around the coordinate (center + 1 km North & East).
    
    Topographic Wind Acceleration (Speed-up Factor):
    - On ridges and elevated hilltops, wind compresses and accelerates (Venturi effect).
    - Speedup factor S = 1.0 + 2.0 * s (where s = slope gradient up to ~0.3).
    - High elevation sites (>1200m) with hill slopes get significant wind boost.
    """
    # Sample center, north, east (+0.01 deg is ~1.1 km)
    loc_str = f"{latitude},{longitude}|{latitude+0.01:.4f},{longitude:.4f}|{latitude:.4f},{longitude+0.01:.4f}"
    url = f"https://api.open-elevation.com/api/v1/lookup?locations={loc_str}"
    
    center_elev = 500.0
    north_elev = 500.0
    east_elev = 500.0
    source = "Open-Elevation API"
    
    try:
        response = requests.get(url, timeout=8)
        if response.status_code == 200:
            results = response.json().get("results", [])
            if len(results) >= 3:
                center_elev = float(results[0].get("elevation", 500.0))
                north_elev = float(results[1].get("elevation", center_elev))
                east_elev = float(results[2].get("elevation", center_elev))
            elif len(results) >= 1:
                center_elev = float(results[0].get("elevation", 500.0))
                north_elev = center_elev
                east_elev = center_elev
    except Exception as e:
        print(f"Warning: Elevation lookup timed out ({e}), using default elevation.")

    # Calculate topographic gradient
    d_north = (north_elev - center_elev) / 1110.0 # elevation diff over ~1110 meters
    d_east = (east_elev - center_elev) / 1110.0
    slope_gradient = math.sqrt(d_north**2 + d_east**2)
    slope_degrees = round(math.degrees(math.atan(slope_gradient)), 1)
    
    # Wind speedup factor: elevated terrain & ridges experience accelerated airflow
    # If slope between 3 deg and 18 deg on elevated ground (>600m), terrain acts as wind accelerator
    is_ridge_or_hill = (center_elev > 600.0 and slope_degrees >= 2.0)
    if is_ridge_or_hill:
        wind_terrain_speedup = round(1.0 + min(0.35, slope_gradient * 2.5), 2)
        terrain_type = "Elevated Ridge / Hillcrest"
    elif center_elev > 1500.0:
        wind_terrain_speedup = 1.15
        terrain_type = "High Plateau / Mountain"
    else:
        wind_terrain_speedup = 1.0
        terrain_type = "Plains / Flat Lowland"

    # Solar terrain suitability: flat (<10 deg) is best for standard mounting. Steep slopes (>20 deg) have mounting penalties.
    terrain_suitability_score = 92.0
    if slope_degrees > 20:
        terrain_suitability_score = 65.0
    elif slope_degrees > 10:
        terrain_suitability_score = 80.0

    terrain_data = {
        "latitude": latitude,
        "longitude": longitude,
        "elevation_meters": round(center_elev, 1),
        "estimated_slope_degrees": slope_degrees,
        "terrain_type": terrain_type,
        "wind_terrain_speedup": wind_terrain_speedup,
        "terrain_suitability_score": terrain_suitability_score,
        "elevation_source": source
    }
    
    output_file = DATA_DIR / "terrain_data.json"
    output_file.write_text(json.dumps(terrain_data, indent=4), encoding="utf-8")
    return terrain_data

if __name__ == "__main__":
    get_elevation_and_terrain(22.7196, 75.8577)
