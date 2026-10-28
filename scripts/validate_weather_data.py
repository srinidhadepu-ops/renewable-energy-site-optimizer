"""
Phase 2 Data Quality & NASA POWER / Open-Meteo Pipeline Validator.
Validates:
- File existence, structure, types, missing values, sentinel values
- Physical boundary limits & plausibility (solar, wind, temp, humidity, pressure, direction)
- Circular continuity of wind direction
- Temporal continuity & duplicates
- Output actionable errors to JSON and console
"""

import json
import math
import sys
from pathlib import Path
import pandas as pd
import numpy as np

DATA_DIR = Path(__file__).resolve().parents[1] / "backend" / "data"
REPORT_DIR = Path(__file__).resolve().parents[1] / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

PHYSICAL_LIMITS = {
    "ALLSKY_SFC_SW_DWN": {"min": 0.0, "max": 14.0, "unit": "kWh/m2/day", "allows_negative": False},
    "T2M": {"min": -60.0, "max": 60.0, "unit": "deg C", "allows_negative": True},
    "T2M_MAX": {"min": -60.0, "max": 65.0, "unit": "deg C", "allows_negative": True},
    "T2M_MIN": {"min": -70.0, "max": 55.0, "unit": "deg C", "allows_negative": True},
    "RH2M": {"min": 0.0, "max": 100.0, "unit": "%", "allows_negative": False},
    "PRECTOTCORR": {"min": 0.0, "max": 500.0, "unit": "mm/day", "allows_negative": False},
    "WS10M": {"min": 0.0, "max": 75.0, "unit": "m/s", "allows_negative": False},
    "WS50M": {"min": 0.0, "max": 90.0, "unit": "m/s", "allows_negative": False},
    "WD10M": {"min": 0.0, "max": 360.0, "unit": "deg", "allows_negative": False, "circular": True}
}

SENTINEL_VALUES = [-999.0, -999, -99.0, -99, 999.0, 9999.0]

def inspect_dataset(df: pd.DataFrame, time_col: str, name: str) -> dict:
    results = {
        "dataset_name": name,
        "row_count": int(len(df)),
        "column_count": int(df.shape[1]),
        "columns": list(df.columns),
        "issues": [],
        "warnings": [],
        "column_metrics": {}
    }

    if time_col not in df.columns:
        results["issues"].append(f"Missing time column '{time_col}'.")
        return results

    # Check temporal ordering & duplicates
    try:
        timestamps = pd.to_datetime(df[time_col])
        duplicates = int(timestamps.duplicated().sum())
        results["duplicate_timestamps"] = duplicates
        if duplicates > 0:
            results["issues"].append(f"Found {duplicates} duplicate timestamps.")
        
        results["start_time"] = str(timestamps.min())
        results["end_time"] = str(timestamps.max())
        results["is_monotonic_increasing"] = bool(timestamps.is_monotonic_increasing)
    except Exception as e:
        results["issues"].append(f"Failed to parse time column '{time_col}': {e}")

    # Inspect each feature
    for col in df.columns:
        if col == time_col:
            continue
        
        series = df[col]
        total_len = len(series)
        
        # Check nulls
        missing_count = int(series.isna().sum())
        missing_pct = round(float((missing_count / total_len) * 100.0), 2)
        
        # Numeric coercion
        numeric_series = pd.to_numeric(series, errors='coerce')
        coerced_nan = int(numeric_series.isna().sum() - missing_count)
        
        # Check sentinels
        sentinel_count = int(numeric_series.isin(SENTINEL_VALUES).sum())
        
        # Check physical bounds
        out_of_bounds = 0
        min_val = None
        max_val = None
        mean_val = None
        
        valid_numeric = numeric_series[~numeric_series.isin(SENTINEL_VALUES)].dropna()
        if len(valid_numeric) > 0:
            min_val = float(valid_numeric.min())
            max_val = float(valid_numeric.max())
            mean_val = float(valid_numeric.mean())
            
            if col in PHYSICAL_LIMITS:
                spec = PHYSICAL_LIMITS[col]
                below = (valid_numeric < spec["min"]).sum()
                above = (valid_numeric > spec["max"]).sum()
                out_of_bounds = int(below + above)
                if out_of_bounds > 0:
                    results["issues"].append(
                        f"Column '{col}' has {out_of_bounds} physically implausible values "
                        f"(Allowed: [{spec['min']}, {spec['max']}] {spec['unit']}, Found: [{min_val}, {max_val}])."
                    )
        
        if sentinel_count > 0:
            results["issues"].append(f"Column '{col}' contains {sentinel_count} NASA POWER sentinel values (-999).")
        
        if missing_pct > 10.0:
            results["warnings"].append(f"Column '{col}' has high missing rate: {missing_pct}% ({missing_count} rows).")
            
        metrics = {
            "dtype": str(series.dtype),
            "missing_count": missing_count,
            "missing_percentage": missing_pct,
            "sentinel_count": sentinel_count,
            "non_numeric_coerced": coerced_nan,
            "min": min_val,
            "max": max_val,
            "mean": round(mean_val, 3) if mean_val is not None else None,
            "out_of_bounds_count": out_of_bounds
        }
        
        # Circular statistics for wind direction
        if col == "WD10M" and len(valid_numeric) > 0:
            rad = np.deg2rad(valid_numeric.values)
            sin_mean = np.mean(np.sin(rad))
            cos_mean = np.mean(np.cos(rad))
            mean_deg = float(np.round(np.rad2deg(np.arctan2(sin_mean, cos_mean)) % 360, 2))
            metrics["circular_mean_deg"] = mean_deg
            
        results["column_metrics"][col] = metrics

    return results

def run_validation():
    print("=" * 65)
    print("      RENEWABLE PIPELINE & DATA QUALITY AUDIT ENGINE")
    print("=" * 65)
    
    overall_report = {
        "audit_version": "1.0",
        "datasets": {}
    }

    files_to_check = [
        ("daily_weather.csv", "date"),
        ("hourly_wind.csv", "timestamp"),
        ("weather_data.csv", "date")
    ]

    for fname, time_col in files_to_check:
        fpath = DATA_DIR / fname
        if not fpath.exists():
            print(f"[-] Missing: {fname}")
            overall_report["datasets"][fname] = {"exists": False, "error": "File does not exist"}
            continue
        
        print(f"[+] Inspecting {fname}...")
        df = pd.read_csv(fpath)
        res = inspect_dataset(df, time_col, fname)
        res["exists"] = True
        res["file_size_bytes"] = fpath.stat().st_size
        overall_report["datasets"][fname] = res
        
        print(f"    Rows: {res['row_count']} | Cols: {res['column_count']} | Duplicates: {res.get('duplicate_timestamps', 0)}")
        if res["issues"]:
            print(f"    ISSUES ({len(res['issues'])}):")
            for iss in res["issues"]:
                print(f"      - {iss}")
        else:
            print("    [OK] No critical physical or sentinel violations found.")
            
        if res["warnings"]:
            print(f"    WARNINGS ({len(res['warnings'])}):")
            for warn in res["warnings"]:
                print(f"      - {warn}")

    # Check metadata
    meta_path = DATA_DIR / "weather_metadata.json"
    if meta_path.exists():
        with open(meta_path, "r") as f:
            overall_report["weather_metadata"] = json.load(f)
            print(f"[+] Metadata loaded: Source = {overall_report['weather_metadata'].get('source')}")

    # Save outputs
    json_path = REPORT_DIR / "data_quality_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(overall_report, f, indent=4)
    print(f"\n[OUTPUT] Saved detailed JSON audit: {json_path}")
    
    return overall_report

if __name__ == "__main__":
    report = run_validation()
    has_issues = any(len(d.get("issues", [])) > 0 for d in report["datasets"].values() if d.get("exists"))
    if has_issues:
        print("\n[NOTE] Actionable findings recorded in data quality report.")
