from typing import Dict, Any, List

# Catalog of standardized commercial/residential wind turbines
WIND_TURBINE_MODELS = {
    "vawt_micro_urban": {
        "model_name": "HelixUrban V-800 (Darrieus/Savonius Hybrid)",
        "turbine_type": "VAWT (Vertical Axis Wind Turbine)",
        "rated_capacity_kw": 0.8,
        "cut_in_speed_ms": 1.8,
        "rated_wind_speed_ms": 9.5,
        "rotor_diameter_m": 1.4,
        "swept_area_m2": 2.2,
        "capex_inr": 85000,
        "noise_db": 34,
        "recommended_sites": ["residential_rooftop", "urban_commercial"],
        "advantages": "Silent, omnidirectional (no yaw needed), safe for building vibration limits."
    },
    "vawt_compact_commercial": {
        "model_name": "Aeolus Tower-2K (Vertical Axis)",
        "turbine_type": "VAWT (Vertical Axis Wind Turbine)",
        "rated_capacity_kw": 2.0,
        "cut_in_speed_ms": 2.2,
        "rated_wind_speed_ms": 10.5,
        "rotor_diameter_m": 2.2,
        "swept_area_m2": 5.8,
        "capex_inr": 165000,
        "noise_db": 38,
        "recommended_sites": ["residential_rooftop", "commercial_building", "institutional"],
        "advantages": "Compact footprint, turbulent boundary layer resilient, rooftop parapet mounting."
    },
    "hawt_small_farm": {
        "model_name": "Zephyr-3200 Mast HAWT",
        "turbine_type": "HAWT (Horizontal Axis Wind Turbine)",
        "rated_capacity_kw": 3.2,
        "cut_in_speed_ms": 2.8,
        "rated_wind_speed_ms": 11.0,
        "rotor_diameter_m": 3.8,
        "swept_area_m2": 11.34,
        "capex_inr": 240000,
        "noise_db": 46,
        "recommended_sites": ["farmland_agri", "open_barren_land", "rural_residential"],
        "advantages": "High aerodynamic efficiency (Cp ~ 0.42), guyed tilt-up mast (12m - 15m)."
    },
    "hawt_utility_ranch": {
        "model_name": "Boreas-10K Industrial Wind Mast",
        "turbine_type": "HAWT (Horizontal Axis Wind Turbine)",
        "rated_capacity_kw": 10.0,
        "cut_in_speed_ms": 3.0,
        "rated_wind_speed_ms": 11.5,
        "rotor_diameter_m": 7.2,
        "swept_area_m2": 40.7,
        "capex_inr": 680000,
        "noise_db": 52,
        "recommended_sites": ["open_barren_land", "farmland_agri", "hillcrest_ridge"],
        "advantages": "Substantial continuous generation yield, lattice tower (18m - 24m), high ROI."
    }
}

def select_optimal_turbine(
    site_category: str,
    available_area_m2: float,
    mean_wind_speed_10m: float,
    wind_suitability_score: float
) -> Dict[str, Any]:
    """
    Selects the optimal turbine model, rotor geometry, installation constraints, and equipment CAPEX.
    Site categories:
      - residential_rooftop
      - commercial_building
      - farmland_agri
      - open_barren_land
      - hillcrest_ridge
    """
    if wind_suitability_score < 40.0 or mean_wind_speed_10m < 2.5:
        return {
            "turbine_recommended": False,
            "reason": f"Mean wind speed ({mean_wind_speed_10m} m/s) is below viable turbine cut-in range.",
            "selected_model": None,
            "turbine_capex_inr": 0,
            "capacity_kw": 0.0
        }

    # Selection rules based on structural and acoustic limits of site type
    if site_category == "residential_rooftop":
        # Strictly Vertical Axis Wind Turbine for low noise and minimal vibration
        if available_area_m2 < 40:
            selected_key = "vawt_micro_urban"
        else:
            selected_key = "vawt_compact_commercial"
    elif site_category == "commercial_building":
        if available_area_m2 < 120:
            selected_key = "vawt_compact_commercial"
        else:
            selected_key = "hawt_small_farm"
    elif site_category in ["farmland_agri", "open_barren_land"]:
        if available_area_m2 < 300:
            selected_key = "hawt_small_farm"
        else:
            selected_key = "hawt_utility_ranch"
    elif site_category == "hillcrest_ridge":
        selected_key = "hawt_utility_ranch"
    else:
        selected_key = "vawt_compact_commercial" if available_area_m2 < 100 else "hawt_small_farm"

    turbine = WIND_TURBINE_MODELS[selected_key]
    
    return {
        "turbine_recommended": True,
        "site_category": site_category,
        "model_key": selected_key,
        "model_name": turbine["model_name"],
        "turbine_type": turbine["turbine_type"],
        "capacity_kw": turbine["rated_capacity_kw"],
        "cut_in_speed_ms": turbine["cut_in_speed_ms"],
        "rated_wind_speed_ms": turbine["rated_wind_speed_ms"],
        "rotor_diameter_m": turbine["rotor_diameter_m"],
        "swept_area_m2": turbine["swept_area_m2"],
        "turbine_capex_inr": turbine["capex_inr"],
        "noise_db": turbine["noise_db"],
        "engineering_rationale": turbine["advantages"]
    }
