import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def generate_site_recommendation():
    """
    Synthesizes:
      1. Resource Scores (Solar vs Wind)
      2. Terrain Suitability & Elevation/Slope
      3. Energy Simulations
      4. Techno-Economics (Payback, LCOE, NPV)
    Produces responsive verdicts: Solar PV, Wind Turbine, or Solar-Wind Hybrid.
    """
    scores_file = DATA_DIR / "resource_scores.json"
    terrain_file = DATA_DIR / "terrain_data.json"
    energy_file = DATA_DIR / "energy_simulation.json"
    econ_file = DATA_DIR / "techno_economics.json"
    
    with open(scores_file, "r") as f:
        scores = json.load(f)
    with open(terrain_file, "r") as f:
        terrain = json.load(f)
    with open(energy_file, "r") as f:
        energy = json.load(f)
    with open(econ_file, "r") as f:
        econ = json.load(f)
        
    solar_score = scores["solar_suitability_score"]
    wind_score = scores["wind_suitability_score"]
    
    solar_econ = econ["solar_financials"]
    wind_econ = econ["wind_financials"]
    hybrid_econ = econ["hybrid_financials"]
    
    # ------------------ VIABILITY THRESHOLDS ------------------
    # Wind is viable if score >= 48 or payback <= 14 years
    wind_payback = wind_econ.get("payback_period_years")
    wind_payback_val = float(wind_payback) if isinstance(wind_payback, (int, float)) else 99.0
    wind_viable = (wind_score >= 48.0) or (wind_payback_val <= 14.0)

    solar_payback = solar_econ.get("payback_period_years")
    solar_payback_val = float(solar_payback) if isinstance(solar_payback, (int, float)) else 99.0
    solar_viable = (solar_score >= 50.0) and (solar_payback_val <= 14.0)
    
    mean_speed_10m = scores["wind_details"]["mean_speed_10m_ms"]
    ghi = scores["solar_details"]["annual_avg_ghi_kwh_m2_day"]
    terrain_type = terrain.get("terrain_type", "Plains")
    speedup = terrain.get("wind_terrain_speedup", 1.0)

    # Decision Matrix
    if wind_viable and (wind_score >= solar_score + 10 or mean_speed_10m >= 6.5 or solar_score < 45.0):
        # Pure Wind Preferred (High wind / stormy coastal / high pass)
        rec_system = "Wind Turbine System"
        rec_capacity = {
            "solar_kw": 0.0,
            "wind_kw": wind_econ["capacity_kw"]
        }
        chosen_capex = wind_econ["estimated_capex"]
        chosen_savings = wind_econ["annual_savings"]
        chosen_payback = wind_econ["payback_period_years"]
        chosen_npv = 0.0
        primary_reason = (
            f"Strong wind resource detected at this site (Wind score: {wind_score}/100, "
            f"effective wind speed: {mean_speed_10m} m/s on {terrain_type} with a {speedup}x elevation speed-up factor). "
            f"Wind turbines achieve an attractive payback of {wind_payback_val} years."
        )
    elif solar_viable and wind_viable and energy["wind_system"]["feasible_on_site"]:
        # Hybrid Preferred
        rec_system = "Solar-Wind Hybrid System"
        rec_capacity = {
            "solar_kw": solar_econ["capacity_kw"],
            "wind_kw": wind_econ["capacity_kw"]
        }
        chosen_capex = hybrid_econ["estimated_capex"]
        chosen_savings = hybrid_econ["annual_savings"]
        chosen_payback = hybrid_econ["payback_period_years"]
        chosen_npv = solar_econ.get("npv_25_year", 0.0)
        primary_reason = (
            f"Both Solar (score: {solar_score}/100, GHI: {ghi} kWh/m²/day) and Wind (score: {wind_score}/100, "
            f"speed: {mean_speed_10m} m/s) are commercially viable on this {terrain_type}. "
            "A Solar-Wind Hybrid setup provides complementary day/night power generation with higher grid independence."
        )
    elif solar_viable:
        # Solar Preferred
        rec_system = "Rooftop / Ground Solar PV"
        rec_capacity = {
            "solar_kw": solar_econ["capacity_kw"],
            "wind_kw": 0.0
        }
        chosen_capex = solar_econ["estimated_capex"]
        chosen_savings = solar_econ["annual_savings"]
        chosen_payback = solar_econ["payback_period_years"]
        chosen_npv = solar_econ.get("npv_25_year", 0.0)
        primary_reason = (
            f"Solar resource is strong (score: {solar_score}/100, GHI: {ghi} kWh/m²/day) "
            f"with an attractive payback of {solar_payback_val} years. "
            f"In contrast, local wind speeds average {mean_speed_10m} m/s, which is below "
            "the economic threshold for small wind turbines (>5.0 m/s recommended)."
        )
    else:
        rec_system = "Energy Conservation & Grid Only"
        rec_capacity = {"solar_kw": 0.0, "wind_kw": 0.0}
        chosen_capex = 0
        chosen_savings = 0
        chosen_payback = "N/A"
        chosen_npv = 0
        primary_reason = "Neither solar nor wind resources meet economic viability criteria at this coordinate."

    recommendation = {
        "verdict": rec_system,
        "recommended_capacity": rec_capacity,
        "suitability_ratings": {
            "solar_score": solar_score,
            "wind_score": wind_score,
            "terrain_score": terrain["terrain_suitability_score"]
        },
        "financial_summary": {
            "estimated_capex_inr": chosen_capex,
            "annual_savings_inr": chosen_savings,
            "payback_years": chosen_payback,
            "twenty_five_year_net_profit_inr": chosen_npv
        },
        "explanation": primary_reason
    }
    
    output_file = DATA_DIR / "final_recommendation.json"
    output_file.write_text(json.dumps(recommendation, indent=4), encoding="utf-8")
    return recommendation

if __name__ == "__main__":
    generate_site_recommendation()
