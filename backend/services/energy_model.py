import pandas as pd
import numpy as np
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def simulate_energy_generation(
    area_m2: float = 100.0,
    monthly_consumption_kwh: float = 500.0,
    terrain_speedup: float = 1.0
):
    """
    Simulates physical energy output for solar and wind.
    """
    monthly_summary = pd.read_csv(DATA_DIR / "monthly_summary.csv", index_col=0)
    hourly_wind = pd.read_csv(DATA_DIR / "hourly_wind.csv", index_col=0, parse_dates=True)
    
    # ------------------- 1. SOLAR PV -------------------
    solar_capacity_kw = round(float(area_m2 / 7.0), 2)
    solar_capacity_kw = max(1.0, solar_capacity_kw)
    performance_ratio = 0.78
    
    valid_solar_mean = monthly_summary["solar_mean"].dropna().mean()
    solar_series = monthly_summary["solar_mean"].fillna(valid_solar_mean)
    days_series = monthly_summary["days_expected"]
    
    monthly_solar_kwh = []
    for month_dt, ghi in solar_series.items():
        days = days_series.loc[month_dt]
        gen = solar_capacity_kw * ghi * days * performance_ratio
        monthly_solar_kwh.append(round(float(gen), 1))
        
    annual_solar_kwh = round(float(np.sum(monthly_solar_kwh)), 1)
    
    # ------------------- 2. WIND TURBINE -------------------
    # Wind sizing: 1 kW turbine requires ~25 m2 clearance.
    wind_feasible = area_m2 >= 40.0
    # Scale turbine capacity appropriately based on area and load
    if wind_feasible:
        # e.g., 250 m2 allows up to 5 kW, 100 m2 allows 2-3 kW
        wind_capacity_kw = round(min(10.0, max(1.5, area_m2 / 30.0)), 1)
    else:
        wind_capacity_kw = 0.0

    # Hourly wind speed adjusted by terrain speedup
    hourly_raw_speeds = hourly_wind["WS10M"].dropna()
    effective_10m_speeds = hourly_raw_speeds * terrain_speedup
    # Extrapolate to 25m hub height for small/medium commercial turbine
    hub_speeds = effective_10m_speeds * ((25.0 / 10.0) ** 0.143)
    
    def turbine_power_kw(v, rated_kw):
        if v < 3.0 or v > 25.0:
            return 0.0
        elif v >= 10.5:
            return rated_kw
        else:
            return rated_kw * ((v - 3.0) / (10.5 - 3.0)) ** 2.5
            
    if wind_feasible and len(hub_speeds) > 0:
        hourly_wind_power = [turbine_power_kw(v, wind_capacity_kw) for v in hub_speeds]
        hourly_wind_df = pd.DataFrame({"power_kw": hourly_wind_power}, index=hub_speeds.index)
        monthly_wind_grouped = hourly_wind_df.resample("MS").sum()
        monthly_wind_kwh = [round(float(x), 1) for x in monthly_wind_grouped["power_kw"]]
        annual_wind_kwh = round(float(np.sum(monthly_wind_kwh)), 1)
    else:
        monthly_wind_kwh = [0.0] * len(monthly_solar_kwh)
        annual_wind_kwh = 0.0

    # ------------------- 3. LOAD CONSUMPTION & COVERAGE -------------------
    annual_consumption_kwh = monthly_consumption_kwh * 12.0
    solar_offset_pct = round(min(100.0, (annual_solar_kwh / annual_consumption_kwh) * 100.0), 1)
    wind_offset_pct = round(min(100.0, (annual_wind_kwh / annual_consumption_kwh) * 100.0), 1)
    hybrid_total_kwh = annual_solar_kwh + annual_wind_kwh
    hybrid_offset_pct = round(min(100.0, (hybrid_total_kwh / annual_consumption_kwh) * 100.0), 1)

    result = {
        "inputs": {
            "installation_area_m2": area_m2,
            "monthly_consumption_kwh": monthly_consumption_kwh,
            "annual_consumption_kwh": annual_consumption_kwh
        },
        "solar_system": {
            "capacity_kw": solar_capacity_kw,
            "annual_generation_kwh": annual_solar_kwh,
            "monthly_generation_kwh": monthly_solar_kwh,
            "load_coverage_pct": solar_offset_pct
        },
        "wind_system": {
            "feasible_on_site": wind_feasible,
            "capacity_kw": wind_capacity_kw,
            "annual_generation_kwh": annual_wind_kwh,
            "monthly_generation_kwh": monthly_wind_kwh,
            "load_coverage_pct": wind_offset_pct
        },
        "hybrid_system": {
            "annual_generation_kwh": round(hybrid_total_kwh, 1),
            "load_coverage_pct": hybrid_offset_pct
        }
    }
    
    output_file = DATA_DIR / "energy_simulation.json"
    output_file.write_text(json.dumps(result, indent=4), encoding="utf-8")
    return result

if __name__ == "__main__":
    simulate_energy_generation()
