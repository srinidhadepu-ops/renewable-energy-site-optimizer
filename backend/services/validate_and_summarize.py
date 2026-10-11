
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

daily = pd.read_csv(
    DATA_DIR / "daily_weather.csv",
    parse_dates=["date"]
).set_index("date").sort_index()

hourly = pd.read_csv(
    DATA_DIR / "hourly_wind.csv",
    parse_dates=["timestamp"]
).set_index("timestamp").sort_index()

# Remove duplicate timestamps, if any.
daily = daily[~daily.index.duplicated(keep="last")]
hourly = hourly[~hourly.index.duplicated(keep="last")]

# Validate physical ranges.
daily.loc[
    daily["T2M"].notna() & ~daily["T2M"].between(-90, 65),
    "T2M"
] = float("nan")

hourly.loc[
    hourly["WS10M"].notna() & ~hourly["WS10M"].between(0, 100),
    "WS10M"
] = float("nan")

hourly.loc[
    hourly["WD10M"].notna() & ~hourly["WD10M"].between(0, 360),
    "WD10M"
] = float("nan")

# Calculate daily solar data coverage.
daily["solar_valid"] = daily["ALLSKY_SFC_SW_DWN"].notna()

solar_month = daily.resample("MS").agg(
    days_observed=("ALLSKY_SFC_SW_DWN", "size"),
    solar_valid_days=("solar_valid", "sum"),
    solar_mean=("ALLSKY_SFC_SW_DWN", "mean")
)

solar_month["days_expected"] = solar_month.index.days_in_month
solar_month["solar_coverage_pct"] = (
    100 * solar_month["solar_valid_days"]
    / solar_month["days_expected"]
)

# Do not report a monthly solar average if coverage is below 80%.
solar_month.loc[
    solar_month["solar_coverage_pct"] < 80,
    "solar_mean"
] = float("nan")

# Calculate hourly wind data coverage and statistics.
hourly["wind_valid"] = hourly["WS10M"].notna()

wind_month = hourly.resample("MS").agg(
    wind_records=("WS10M", "size"),
    wind_valid_hours=("wind_valid", "sum"),
    wind_mean=("WS10M", "mean"),
    wind_p50=("WS10M", "median"),
    wind_p90=("WS10M", lambda x: x.quantile(0.90))
)

wind_month["hours_expected"] = (
    wind_month.index.days_in_month * 24
)

wind_month["wind_coverage_pct"] = (
    100 * wind_month["wind_valid_hours"]
    / wind_month["hours_expected"]
)

# Do not report monthly wind statistics with less than 90% coverage.
wind_columns = ["wind_mean", "wind_p50", "wind_p90"]
wind_month.loc[
    wind_month["wind_coverage_pct"] < 90,
    wind_columns
] = float("nan")

# Combine monthly summaries.
summary = solar_month.join(wind_month, how="outer")

output_file = DATA_DIR / "monthly_summary.csv"
summary.to_csv(output_file)

print("\nSolar data coverage by month:")
print(
    solar_month[
        ["solar_valid_days", "days_expected", "solar_coverage_pct"]
    ].round(1).to_string()
)

print("\nWind data coverage by month:")
print(
    wind_month[
        ["wind_valid_hours", "hours_expected", "wind_coverage_pct"]
    ].round(1).to_string()
)

print("\nMonthly summary:")
print(summary.round(2).to_string())

print("\nSaved monthly summary to:", output_file)
