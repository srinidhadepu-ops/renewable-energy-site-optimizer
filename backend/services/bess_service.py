from typing import Dict, Any

def size_bess_storage(
    daily_consumption_kwh: float,
    solar_capacity_kw: float,
    wind_capacity_kw: float,
    desired_backup_hours: float = 8.0,
    depth_of_discharge: float = 0.85,
    round_trip_efficiency: float = 0.92
) -> Dict[str, Any]:
    """
    Sizes Battery Energy Storage System (BESS) for peak shift, night autonomy, and grid independence.
    Standard Chemistry: Lithium Iron Phosphate (LiFePO4 / LFP)
    - 6000+ cycle life (12-15 year lifespan)
    - High thermal stability, fire-safe for residential/commercial building installation
    - Average cost benchmark: ~Rs. 13,500 per kWh of usable storage (includes BMS & Hybrid Inverter interface)
    """
    # 1. Evening & Night Load Requirement
    # Standard residential/commercial profile: ~50-60% of daily consumption occurs evening/night (6 PM - 8 AM)
    hourly_consumption_avg = daily_consumption_kwh / 24.0
    evening_night_demand_kwh = hourly_consumption_avg * desired_backup_hours

    # 2. Storage Sizing accounting for DoD (85%) and Round-Trip Efficiency (92%)
    effective_storage_needed = evening_night_demand_kwh / (depth_of_discharge * round_trip_efficiency)
    
    # Standardize to commercial battery module increments (e.g., 2.5 kWh or 5.0 kWh pack steps)
    module_size_kwh = 2.5
    num_modules = max(1, round(effective_storage_needed / module_size_kwh))
    installed_battery_capacity_kwh = round(num_modules * module_size_kwh, 1)

    # 3. Financial Metrics (CAPEX)
    cost_per_kwh_inr = 13500.0
    battery_capex_inr = round(installed_battery_capacity_kwh * cost_per_kwh_inr)

    # 4. Self-Consumption & Autonomy Evaluation
    estimated_autonomy_hours = round((installed_battery_capacity_kwh * depth_of_discharge * round_trip_efficiency) / max(0.1, hourly_consumption_avg), 1)

    return {
        "bess_recommended": True,
        "battery_chemistry": "LiFePO4 (Lithium Iron Phosphate)",
        "installed_capacity_kwh": installed_battery_capacity_kwh,
        "usable_capacity_kwh": round(installed_battery_capacity_kwh * depth_of_discharge, 1),
        "module_count": num_modules,
        "backup_autonomy_hours": estimated_autonomy_hours,
        "battery_capex_inr": battery_capex_inr,
        "expected_lifespan_years": 14,
        "depth_of_discharge_pct": int(depth_of_discharge * 100),
        "round_trip_efficiency_pct": int(round_trip_efficiency * 100),
        "purpose_benefits": [
            f"Provides ~{estimated_autonomy_hours} hours of continuous power during night or blackout outages.",
            "Stores surplus midday solar generation, eliminating wasted clean energy.",
            "Protects against grid peak electricity tariff surcharges."
        ]
    }
