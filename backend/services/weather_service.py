import requests
import pandas as pd
import json
from pathlib import Path
from datetime import date, timedelta

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DAILY_NASA_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
HOURLY_NASA_URL = "https://power.larc.nasa.gov/api/temporal/hourly/point"
OPENMETEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

def fetch_weather_for_location(latitude: float, longitude: float):
    """
    Fetches real satellite & climate reanalysis data for the specified latitude & longitude.
    Primary High-Speed Source: Open-Meteo ERA5 Reanalysis (1-year daily solar + hourly wind in seconds).
    Fallback Source: NASA POWER API.
    
    Saves:
      - daily_weather.csv: date, ALLSKY_SFC_SW_DWN (kWh/m2/day), T2M (C)
      - hourly_wind.csv: timestamp, WS10M (m/s), WD10M (deg)
      - monthly_summary.csv: aggregated monthly statistics
      - weather_metadata.json
    """
    end_date = date.today() - timedelta(days=5)
    start_date = end_date - timedelta(days=364)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    print(f"\n[GEO-FETCH] Querying satellite climate data for ({latitude}, {longitude})...")
    
    # 1. Attempt High-Speed Open-Meteo ERA5 / Copernicus API (fast, reliable, global)
    try:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_str,
            "end_date": end_str,
            "daily": "shortwave_radiation_sum,temperature_2m_mean",
            "hourly": "wind_speed_10m,wind_direction_10m",
            "wind_speed_unit": "ms", # meters per second
            "timezone": "UTC"
        }
        res = requests.get(OPENMETEO_ARCHIVE_URL, params=params, timeout=20)
        if res.status_code == 200:
            data = res.json()
            daily_dict = data.get("daily", {})
            hourly_dict = data.get("hourly", {})
            
            # Daily conversion: shortwave_radiation_sum is in MJ/m2 -> convert to kWh/m2 (divide by 3.6)
            daily_dates = pd.to_datetime(daily_dict["time"])
            solar_mj = pd.Series(daily_dict["shortwave_radiation_sum"], index=daily_dates)
            solar_kwh = (solar_mj / 3.6).clip(lower=0.0)
            temp_c = pd.Series(daily_dict["temperature_2m_mean"], index=daily_dates)
            
            daily_df = pd.DataFrame({
                "ALLSKY_SFC_SW_DWN": solar_kwh,
                "T2M": temp_c
            }, index=daily_dates)
            daily_df.index.name = "date"

            # Hourly wind
            hourly_dates = pd.to_datetime(hourly_dict["time"])
            hourly_df = pd.DataFrame({
                "WS10M": hourly_dict["wind_speed_10m"],
                "WD10M": hourly_dict["wind_direction_10m"]
            }, index=hourly_dates)
            hourly_df.index.name = "timestamp"

            # Save data
            daily_file = DATA_DIR / "daily_weather.csv"
            hourly_file = DATA_DIR / "hourly_wind.csv"
            daily_df.to_csv(daily_file)
            hourly_df.to_csv(hourly_file)

            # Metadata
            metadata = {
                "latitude": latitude,
                "longitude": longitude,
                "source": "Open-Meteo ERA5 / Copernicus Global Reanalysis",
                "start": start_str,
                "end": end_str,
                "daily_records": len(daily_df),
                "hourly_records": len(hourly_df)
            }
            (DATA_DIR / "weather_metadata.json").write_text(json.dumps(metadata, indent=4), encoding="utf-8")
            
            # Generate monthly summary automatically
            build_monthly_summary(daily_df, hourly_df)
            print(f"[GEO-FETCH] Success! Fetched {len(daily_df)} daily records and {len(hourly_df)} hourly wind readings.")
            return daily_df, hourly_df
            
    except Exception as e:
        print(f"[GEO-FETCH] Open-Meteo request note ({e}), falling back to NASA POWER...")

    # 2. Fallback to NASA POWER
    return fetch_nasa_data(latitude, longitude)


def build_monthly_summary(daily_df, hourly_df):
    """Generates monthly averages and completeness checks."""
    daily_df["solar_valid"] = daily_df["ALLSKY_SFC_SW_DWN"].notna()
    solar_month = daily_df.resample("MS").agg(
        days_observed=("ALLSKY_SFC_SW_DWN", "size"),
        solar_valid_days=("solar_valid", "sum"),
        solar_mean=("ALLSKY_SFC_SW_DWN", "mean")
    )
    solar_month["days_expected"] = solar_month.index.days_in_month
    solar_month["solar_coverage_pct"] = (100 * solar_month["solar_valid_days"] / solar_month["days_expected"])

    hourly_df["wind_valid"] = hourly_df["WS10M"].notna()
    wind_month = hourly_df.resample("MS").agg(
        wind_records=("WS10M", "size"),
        wind_valid_hours=("wind_valid", "sum"),
        wind_mean=("WS10M", "mean"),
        wind_p50=("WS10M", "median"),
        wind_p90=("WS10M", lambda x: x.quantile(0.90))
    )
    wind_month["hours_expected"] = wind_month.index.days_in_month * 24
    wind_month["wind_coverage_pct"] = (100 * wind_month["wind_valid_hours"] / wind_month["hours_expected"])

    summary = solar_month.join(wind_month, how="outer")
    summary.to_csv(DATA_DIR / "monthly_summary.csv")
    return summary


def fetch_nasa_data(latitude, longitude):
    """NASA POWER API fallback"""
    end_date = date.today() - timedelta(days=5)
    start_date = end_date - timedelta(days=364)
    start = start_date.strftime("%Y%m%d")
    end = end_date.strftime("%Y%m%d")

    daily_params = {
        "parameters": "ALLSKY_SFC_SW_DWN,T2M,WS10M,WS50M",
        "community": "RE",
        "longitude": longitude,
        "latitude": latitude,
        "start": start,
        "end": end,
        "format": "JSON",
        "time-standard": "UTC"
    }
    r = requests.get(DAILY_NASA_URL, params=daily_params, timeout=45)
    r.raise_for_status()
    daily_parameters = r.json()["properties"]["parameter"]
    daily_df = pd.DataFrame(daily_parameters)
    daily_df.index = pd.to_datetime(daily_df.index, format="%Y%m%d")
    daily_df.index.name = "date"
    daily_df = daily_df.replace(-999, float("nan"))

    # Hourly wind
    hourly_params = {
        "parameters": "WS10M,WD10M",
        "community": "RE",
        "longitude": longitude,
        "latitude": latitude,
        "start": start,
        "end": end,
        "format": "JSON",
        "time-standard": "UTC"
    }
    r_h = requests.get(HOURLY_NASA_URL, params=hourly_params, timeout=60)
    r_h.raise_for_status()
    hourly_parameters = r_h.json()["properties"]["parameter"]
    hourly_df = pd.DataFrame(hourly_parameters)
    hourly_df.index = pd.to_datetime(hourly_df.index, format="%Y%m%d%H")
    hourly_df.index.name = "timestamp"
    hourly_df = hourly_df.replace(-999, float("nan"))

    daily_df.to_csv(DATA_DIR / "daily_weather.csv")
    hourly_df.to_csv(DATA_DIR / "hourly_wind.csv")
    build_monthly_summary(daily_df, hourly_df)
    return daily_df, hourly_df


if __name__ == "__main__":
    fetch_weather_for_location(22.7196, 75.8577)
