import math
from typing import Dict, Any, List, Optional

def calculate_solar_angles(latitude: float, day_of_year: int = 172, solar_time_hour: float = 12.0) -> Dict[str, float]:
    """
    Computes solar elevation (altitude) and solar azimuth angle.
    day_of_year: 172 ~ Summer Solstice (June 21), 355 ~ Winter Solstice (Dec 21), 80 ~ Spring Equinox (March 21)
    """
    lat_rad = math.radians(latitude)
    # Declination angle delta
    declination = 23.45 * math.sin(math.radians((360 / 365) * (day_of_year - 81)))
    dec_rad = math.radians(declination)
    
    # Hour angle (omega): 15 degrees per hour from solar noon (12:00)
    hour_angle = 15.0 * (solar_time_hour - 12.0)
    omega_rad = math.radians(hour_angle)
    
    # Solar Elevation / Altitude angle (alpha)
    sin_alpha = math.sin(lat_rad) * math.sin(dec_rad) + math.cos(lat_rad) * math.cos(dec_rad) * math.cos(omega_rad)
    alpha = math.degrees(math.asin(max(-1.0, min(1.0, sin_alpha))))
    
    # Solar Azimuth angle (gamma_s) - measured clockwise from North (180 = South)
    cos_gamma = (math.sin(math.radians(alpha)) * math.sin(lat_rad) - math.sin(dec_rad)) / (math.cos(math.radians(alpha)) * math.cos(lat_rad) + 1e-6)
    gamma_s = math.degrees(math.acos(max(-1.0, min(1.0, cos_gamma))))
    if hour_angle > 0:
        gamma_s = 360.0 - gamma_s
        
    return {
        "solar_altitude_deg": round(alpha, 1),
        "solar_azimuth_deg": round(gamma_s, 1),
        "declination_deg": round(declination, 1)
    }

def analyze_rooftop_shading_and_placement(
    latitude: float,
    longitude: float,
    polygon_points: Optional[List[Dict[str, float]]] = None,
    total_area_m2: float = 100.0,
    neighbor_building_height_m: float = 4.0,
    neighbor_distance_m: float = 5.0,
    neighbor_direction: str = "East" # North, South, East, West
) -> Dict[str, Any]:
    """
    Rooftop solar shadow analysis, obstacle buffering, tilt & azimuth orientation,
    and micro-placement heatmap zones.
    """
    # 1. Optimal tilt and azimuth orientation
    # In Northern Hemisphere, optimal azimuth is True South (180°), optimal tilt is roughly latitude +/- 5°
    optimal_azimuth = 180.0 if latitude >= 0 else 0.0 # South for North hemisphere, North for South hemisphere
    optimal_tilt = round(max(10.0, min(35.0, abs(latitude))), 1)

    # 2. Shadow length calculation from neighboring building at critical winter solstice (low sun angle)
    winter_angles = calculate_solar_angles(latitude, day_of_year=355, solar_time_hour=10.5)
    winter_elevation = max(10.0, winter_angles["solar_altitude_deg"])
    
    # Shadow length L = Height / tan(solar_altitude)
    shadow_length_m = round(neighbor_building_height_m / math.tan(math.radians(winter_elevation)), 1)
    
    # Calculate shadow penetration into user's plot
    shadow_penetration_m = max(0.0, shadow_length_m - neighbor_distance_m)
    
    # Estimate shaded area fraction based on neighbor direction
    # North neighbor causes minimal shadow on south roof; East/West/South neighbors cause significant shadows
    if neighbor_direction in ["East", "West"]:
        shading_fraction = min(0.35, (shadow_penetration_m * 4.0) / total_area_m2)
    elif neighbor_direction == "South" and latitude >= 0:
        shading_fraction = min(0.45, (shadow_penetration_m * 6.0) / total_area_m2)
    else:
        shading_fraction = min(0.12, (shadow_penetration_m * 2.0) / total_area_m2)
        
    shading_fraction = max(0.04, round(shading_fraction, 2)) # minimum baseline for parapet / water tank

    # 3. Micro-Placement Partitioning
    unshaded_solar_area_m2 = round(total_area_m2 * (1.0 - shading_fraction) * 0.85, 1) # 15% buffer for walkway
    shaded_area_m2 = round(total_area_m2 - unshaded_solar_area_m2, 1)

    # Micro-placement coordinates / segments for heatmap rendering
    placement_zones = [
        {
            "zone_id": "zone_prime_solar_south",
            "zone_name": "Prime Solar Hotspot (South/Center)",
            "status": "Recommended for Solar PV",
            "color": "#10b981", # Green
            "usable_area_m2": round(unshaded_solar_area_m2 * 0.8, 1),
            "estimated_annual_sun_hours": 2850,
            "shading_risk": "Low (Unobstructed)",
            "optimal_panel_azimuth_deg": optimal_azimuth,
            "optimal_panel_tilt_deg": optimal_tilt
        },
        {
            "zone_id": "zone_micro_wind_parapet",
            "zone_name": "Aerodynamic Edge (Wind Parapet)",
            "status": "Optimal for Micro VAWT Turbine",
            "color": "#06b6d4", # Cyan
            "usable_area_m2": round(min(12.0, total_area_m2 * 0.1), 1),
            "wind_exposure": "High (Clear Boundary Layer)",
            "recommended_equipment": "Rooftop Vertical-Axis Helix Turbine"
        },
        {
            "zone_id": "zone_shaded_boundary",
            "zone_name": f"{neighbor_direction} Boundary Shadow Zone",
            "status": "Avoid Solar Placement (Shaded / Walkway)",
            "color": "#ef4444", # Red
            "usable_area_m2": shaded_area_m2,
            "shading_cause": f"{neighbor_building_height_m}m adjacent structure ({neighbor_direction})"
        }
    ]

    return {
        "total_site_area_m2": total_area_m2,
        "effective_unshaded_solar_area_m2": unshaded_solar_area_m2,
        "shading_loss_factor_pct": int(shading_fraction * 100),
        "optimal_orientation": {
            "azimuth_degrees": optimal_azimuth,
            "azimuth_direction": "True South" if optimal_azimuth == 180 else "True North",
            "tilt_angle_degrees": optimal_tilt
        },
        "shadow_diagnostics": {
            "winter_sun_elevation_deg": winter_elevation,
            "estimated_shadow_length_m": shadow_length_m,
            "neighbor_distance_m": neighbor_distance_m,
            "shadow_penetration_m": shadow_penetration_m
        },
        "micro_placement_zones": placement_zones
    }
