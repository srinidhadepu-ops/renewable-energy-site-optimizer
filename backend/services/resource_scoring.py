import pandas as pd
import numpy as np
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def calculate_solar_score(monthly_summary_path, daily_weather_path):
    summary = pd.read_csv(monthly_summary_path, index_col=0)
    daily = pd.read_csv(daily_weather_path, index_col=0, parse_dates=True)
    
    valid_solar_months = summary["solar_mean"].dropna()
    if len(valid_solar_months) == 0:
        return 0.0, {"error": "Insufficient solar observations"}
    
    annual_avg_ghi = valid_solar_months.mean()
    # 2.0 kWh/m2/day = 0 pts, 6.0 kWh/m2/day = 70 pts
    base_score = np.clip((annual_avg_ghi - 2.0) / (6.0 - 2.0) * 70.0, 0.0, 70.0)
    
    # Temperature Factor (0 to 15 points)
    avg_temp = daily["T2M"].dropna().mean() if "T2M" in daily.columns else 25.0
    if avg_temp <= 25.0:
        temp_score = 15.0
    elif avg_temp >= 40.0:
        temp_score = 5.0
    else:
        temp_score = 15.0 - ((avg_temp - 25.0) / 15.0 * 10.0)
        
    # Consistency Factor (0 to 15 points)
    min_ghi = valid_solar_months.min()
    max_ghi = valid_solar_months.max()
    consistency_ratio = (min_ghi / max_ghi) if max_ghi > 0 else 0
    consistency_score = np.clip(consistency_ratio * 15.0, 0.0, 15.0)
    
    total_solar_score = float(np.round(base_score + temp_score + consistency_score, 1))
    
    details = {
        "annual_avg_ghi_kwh_m2_day": round(float(annual_avg_ghi), 2),
        "annual_avg_temp_c": round(float(avg_temp), 1),
        "min_month_ghi": round(float(min_ghi), 2),
        "max_month_ghi": round(float(max_ghi), 2),
        "consistency_ratio": round(float(consistency_ratio), 2),
        "score_components": {
            "base_irradiance_score": round(float(base_score), 1),
            "temperature_score": round(float(temp_score), 1),
            "consistency_score": round(float(consistency_score), 1)
        }
    }
    return total_solar_score, details


def calculate_wind_score(monthly_summary_path, hourly_wind_path, terrain_speedup=1.0):
    """
    Computes Wind Resource Score (0 to 100), incorporating topographic wind speedup
    from ridges and elevated terrain.
    """
    summary = pd.read_csv(monthly_summary_path, index_col=0)
    hourly = pd.read_csv(hourly_wind_path, index_col=0, parse_dates=True)
    
    valid_speeds = hourly["WS10M"].dropna()
    if len(valid_speeds) == 0:
        return 0.0, {"error": "Insufficient valid wind observations"}
    
    # Apply topographic terrain acceleration (ridges/hills speedup)
    effective_speeds = valid_speeds * terrain_speedup
    
    mean_speed_10m = effective_speeds.mean()
    p50_speed_10m = effective_speeds.median()
    p90_speed_10m = effective_speeds.quantile(0.90)
    
    # Extrapolate to 30m - 50m hub height
    shear_factor = (40.0 / 10.0) ** 0.143
    mean_speed_hub = mean_speed_10m * shear_factor
    
    # 1. Base Wind Speed Score (0 to 50 points)
    # Thresholds:
    # < 3.0 m/s: Poor (< 15)
    # 3.5 - 5.0 m/s: Moderate (15 - 35)
    # 5.0 - 6.5 m/s: Good (35 - 45)
    # > 6.5 m/s: Excellent (45 - 50)
    if mean_speed_hub < 3.0:
        speed_score = (mean_speed_hub / 3.0) * 15.0
    elif mean_speed_hub <= 6.5:
        speed_score = 15.0 + ((mean_speed_hub - 3.0) / 3.5) * 30.0
    else:
        speed_score = 45.0 + np.clip(((mean_speed_hub - 6.5) / 2.0) * 5.0, 0.0, 5.0)
        
    # 2. Operating Hours (Cut-in availability: % of hours >= 3.0 m/s) (0 to 30 points)
    cut_in_ratio = (effective_speeds >= 3.0).sum() / len(effective_speeds)
    availability_score = cut_in_ratio * 30.0
    
    # 3. Wind Power Density (WPD) indicator (0 to 20 points)
    # WPD = 0.5 * rho * v^3
    mean_cubic_speed = (effective_speeds ** 3).mean()
    wpd = 0.5 * 1.225 * mean_cubic_speed
    wpd_score = np.clip((wpd / 200.0) * 20.0, 0.0, 20.0)
    
    total_wind_score = float(np.round(speed_score + availability_score + wpd_score, 1))
    
    details = {
        "mean_speed_10m_ms": round(float(mean_speed_10m), 2),
        "mean_speed_hub_ms": round(float(mean_speed_hub), 2),
        "terrain_speedup_factor": round(float(terrain_speedup), 2),
        "median_speed_10m_ms": round(float(p50_speed_10m), 2),
        "p90_speed_10m_ms": round(float(p90_speed_10m), 2),
        "cut_in_hours_pct": round(float(cut_in_ratio * 100), 1),
        "wind_power_density_w_m2": round(float(wpd), 1),
        "score_components": {
            "speed_score": round(float(speed_score), 1),
            "availability_score": round(float(availability_score), 1),
            "wpd_score": round(float(wpd_score), 1)
        }
    }
    return total_wind_score, details


def evaluate_site_resources(terrain_speedup: float = 1.0):
    monthly_file = DATA_DIR / "monthly_summary.csv"
    daily_file = DATA_DIR / "daily_weather.csv"
    hourly_file = DATA_DIR / "hourly_wind.csv"
    
    solar_score, solar_details = calculate_solar_score(monthly_file, daily_file)
    wind_score, wind_details = calculate_wind_score(monthly_file, hourly_file, terrain_speedup=terrain_speedup)
    
    results = {
        "solar_suitability_score": solar_score,
        "solar_details": solar_details,
        "wind_suitability_score": wind_score,
        "wind_details": wind_details,
        "preliminary_verdict": (
            "Wind Preferred" if wind_score >= 60.0 and wind_score > solar_score else
            "Hybrid Viable" if (solar_score >= 55.0 and wind_score >= 48.0) else
            "Solar Preferred"
        )
    }
    
    output_file = DATA_DIR / "resource_scores.json"
    output_file.write_text(json.dumps(results, indent=4), encoding="utf-8")
    return results

if __name__ == "__main__":
    evaluate_site_resources()
