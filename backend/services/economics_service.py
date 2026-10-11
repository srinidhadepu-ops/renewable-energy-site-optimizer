import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def calculate_techno_economics(
    tariff_inr_per_kwh: float = 7.5,
    currency_symbol: str = "INR"
):
    """
    Computes Capital Expenditure (CAPEX), Operational Expenditure (OPEX),
    Annual Electricity Savings, Net Present Value (NPV), Payback Period, and LCOE.
    
    Standard Benchmark Parameters (India & International Market Rates):
    - Solar CAPEX: ~ Rs. 50,000 per kW (includes panels, mounting, inverter, installation)
    - Solar OPEX: 1.5% of CAPEX / year
    - Wind CAPEX: ~ Rs. 95,000 per kW (mast, small turbine, inverter, civil works)
    - Wind OPEX: 3.0% of CAPEX / year
    - Discount Rate: 8% per annum
    - System Lifespan: 25 years for Solar, 20 years for Wind
    """
    energy_sim_file = DATA_DIR / "energy_simulation.json"
    if not energy_sim_file.exists():
        raise FileNotFoundError(f"Missing {energy_sim_file}. Run energy_model.py first.")
        
    with open(energy_sim_file, "r") as f:
        energy_data = json.load(f)
        
    solar = energy_data["solar_system"]
    wind = energy_data["wind_system"]
    consumption_annual = energy_data["inputs"]["annual_consumption_kwh"]
    
    # ----------------- 1. SOLAR FINANCIALS -----------------
    solar_kw = solar["capacity_kw"]
    solar_capex = solar_kw * 50000.0
    solar_opex_annual = solar_capex * 0.015
    
    # Only energy offset up to user consumption creates direct bill savings; surplus can be net-metered at 50% tariff
    usable_solar = min(solar["annual_generation_kwh"], consumption_annual)
    surplus_solar = max(0.0, solar["annual_generation_kwh"] - consumption_annual)
    solar_annual_savings = (usable_solar * tariff_inr_per_kwh) + (surplus_solar * tariff_inr_per_kwh * 0.5)
    solar_net_annual_cashflow = solar_annual_savings - solar_opex_annual
    solar_payback_years = (solar_capex / solar_net_annual_cashflow) if solar_net_annual_cashflow > 0 else 99.0
    
    # 25-Year NPV for Solar (Discount rate r = 8%)
    r = 0.08
    solar_npv = -solar_capex
    for year in range(1, 26):
        # 0.5% yearly degradation on output
        yearly_cash = (solar_annual_savings * ((1 - 0.005) ** (year - 1))) - solar_opex_annual
        solar_npv += yearly_cash / ((1 + r) ** year)

    # ----------------- 2. WIND FINANCIALS -----------------
    wind_kw = wind["capacity_kw"]
    wind_capex = wind_kw * 95000.0 if wind["feasible_on_site"] else 0.0
    wind_opex_annual = wind_capex * 0.03
    
    usable_wind = min(wind["annual_generation_kwh"], consumption_annual)
    surplus_wind = max(0.0, wind["annual_generation_kwh"] - consumption_annual)
    wind_annual_savings = (usable_wind * tariff_inr_per_kwh) + (surplus_wind * tariff_inr_per_kwh * 0.5)
    wind_net_annual_cashflow = wind_annual_savings - wind_opex_annual
    wind_payback_years = (wind_capex / wind_net_annual_cashflow) if wind_net_annual_cashflow > 0 else 99.0

    # ----------------- 3. HYBRID FINANCIALS -----------------
    hybrid_capex = solar_capex + wind_capex
    hybrid_annual_savings = solar_annual_savings + wind_annual_savings
    hybrid_net_cashflow = hybrid_annual_savings - (solar_opex_annual + wind_opex_annual)
    hybrid_payback_years = (hybrid_capex / hybrid_net_cashflow) if hybrid_net_cashflow > 0 else 99.0

    economics = {
        "tariff_per_kwh": tariff_inr_per_kwh,
        "solar_financials": {
            "capacity_kw": solar_kw,
            "estimated_capex": round(solar_capex, 0),
            "annual_opex": round(solar_opex_annual, 0),
            "annual_savings": round(solar_annual_savings, 0),
            "payback_period_years": round(min(25.0, solar_payback_years), 1),
            "npv_25_year": round(solar_npv, 0),
            "lcoe_per_kwh": round(solar_capex / (solar["annual_generation_kwh"] * 25 * 0.9), 2)
        },
        "wind_financials": {
            "capacity_kw": wind_kw,
            "estimated_capex": round(wind_capex, 0),
            "annual_opex": round(wind_opex_annual, 0),
            "annual_savings": round(wind_annual_savings, 0),
            "payback_period_years": round(min(25.0, wind_payback_years), 1) if wind_payback_years < 25 else ">25 (Unfavorable)"
        },
        "hybrid_financials": {
            "estimated_capex": round(hybrid_capex, 0),
            "annual_savings": round(hybrid_annual_savings, 0),
            "payback_period_years": round(min(25.0, hybrid_payback_years), 1)
        }
    }
    
    output_file = DATA_DIR / "techno_economics.json"
    output_file.write_text(json.dumps(economics, indent=4), encoding="utf-8")
    
    print("\n" + "="*55)
    print("          TECHNO-ECONOMIC FEASIBILITY ANALYSIS")
    print("="*55)
    print(f"Electricity Tariff: Rs. {tariff_inr_per_kwh} / kWh")
    print("-" * 55)
    print(f"[SOLAR PV ECONOMICS]")
    print(f"   * Initial CAPEX:       Rs. {solar_capex:,.0f}")
    print(f"   * Annual Bill Savings: Rs. {solar_annual_savings:,.0f}/year")
    print(f"   * Payback Period:      {economics['solar_financials']['payback_period_years']} Years")
    print(f"   * 25-Year Net Profit:  Rs. {solar_npv:,.0f} (NPV)")
    print(f"   * LCOE:                Rs. {economics['solar_financials']['lcoe_per_kwh']} / kWh")
    print("-" * 55)
    print(f"[WIND TURBINE ECONOMICS]")
    print(f"   * Initial CAPEX:       Rs. {wind_capex:,.0f}")
    print(f"   * Annual Bill Savings: Rs. {wind_annual_savings:,.0f}/year")
    print(f"   * Payback Period:      {economics['wind_financials']['payback_period_years']}")
    print("-" * 55)
    print(f"[OUTPUT] Saved financials to: {output_file}")
    print("="*55 + "\n")
    
    return economics


if __name__ == "__main__":
    calculate_techno_economics()
