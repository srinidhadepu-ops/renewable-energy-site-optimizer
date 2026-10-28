"""
Regenerates PROJECT_EVALUATION_TEAM_GUIDE.docx to include deep, explicit
technical stacks, library usage, implementation mechanics, algorithm details,
and component interactions for every single member and module.
"""

from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

OUTPUT_FILE = Path(__file__).resolve().parents[1] / "PROJECT_EVALUATION_TEAM_GUIDE.docx"

def set_cell_background(cell, hex_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def add_header(doc, text, level):
    p = doc.add_heading(text, level=level)
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    for run in p.runs:
        if level == 1:
            run.font.color.rgb = RGBColor(18, 52, 86)  # Deep Navy
            run.font.size = Pt(17)
            run.bold = True
        elif level == 2:
            run.font.color.rgb = RGBColor(16, 124, 65) # Deep Green
            run.font.size = Pt(13)
            run.bold = True
        elif level == 3:
            run.font.color.rgb = RGBColor(40, 40, 40)
            run.font.size = Pt(11)
            run.bold = True
    return p

def create_document():
    doc = docx.Document()
    
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(30, 30, 30)

    # ==========================================
    # TITLE SECTION
    # ==========================================
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(4)
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = title_p.add_run("PROJECT EVALUATION & TEAM VIVA GUIDE")
    run_title.font.size = Pt(20)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(18, 52, 86)

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(16)
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = sub_p.add_run(
        "Helios & Aeolus: AI & Satellite Geospatial Decision Support System for Renewable Energy Siting\n"
        "Complete 4-Member Work Division, Exhaustive Technology Stack Mapping, Implementation Mechanics, Code Walkthrough & Defense Strategy"
    )
    run_sub.font.size = Pt(12)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(100, 100, 100)

    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_after = Pt(20)
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_meta = p_meta.add_run("Evaluation Readiness: 100% Complete | Tests: 78/78 Passing | Stack: Python 3.14 + FastAPI + Leaflet GIS")
    r_meta.font.bold = True
    r_meta.font.color.rgb = RGBColor(16, 124, 65)

    doc.add_page_break()

    # ==========================================
    # TABLE OF CONTENTS
    # ==========================================
    add_header(doc, "Table of Contents & Preparation Blueprint", level=1)
    p_toc = doc.add_paragraph(
        "This master preparation guide is crafted for the upcoming project defense. It arms every team member "
        "with deep, unflinching command over their designated role, the exact technologies used, how each algorithm is "
        "implemented in code, and how all parts interconnect:\n\n"
        "• Section 1: Executive 4-Member Work Division & Responsibility Matrix\n"
        "• Section 2: Complete Project Technology Stack & Architecture Topology\n"
        "• Section 3: Member 1 Deep Dive — Technologies, Implementation Mechanics & Algorithms (Data & Topography)\n"
        "• Section 4: Member 2 Deep Dive — Technologies, Implementation Mechanics & Algorithms (Physics & Simulation)\n"
        "• Section 5: Member 3 Deep Dive — Technologies, Implementation Mechanics & Algorithms (Economics & Hardware)\n"
        "• Section 6: Member 4 Deep Dive — Technologies, Implementation Mechanics & Algorithms (GIS, REST API & Security)\n"
        "• Section 7: End-to-End Pipeline Mechanics: How Every Module Operates Independently & Jointly\n"
        "• Section 8: Complete Codebase & Directory Inventory (Every File, Role & Dependency)\n"
        "• Section 9: Professor Viva Defense Strategy — Top 10 Questions & High-Scoring Answers\n"
    )

    # ==========================================
    # SECTION 1: 4-MEMBER WORK DIVISION MATRIX
    # ==========================================
    add_header(doc, "Section 1: 4-Member Work Division & Responsibility Matrix", level=1)
    doc.add_paragraph(
        "The project has been divided cleanly into 4 specialized, non-overlapping yet tightly integrated roles. "
        "Each person is the complete master of their domain from inception to delivery, while understanding how their "
        "outputs feed the next stage in the pipeline."
    )

    table1 = doc.add_table(rows=1, cols=4)
    table1.alignment = WD_TABLE_ALIGNMENT.CENTER
    table1.style = 'Table Grid'
    hdr_cells = table1.rows[0].cells
    headers = ["Member & Title", "Assigned Services & Files", "Exact Technologies Used", "Viva Role & Presentation Focus"]
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        hdr_cells[i].paragraphs[0].runs[0].font.bold = True
        hdr_cells[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(hdr_cells[i], "123456")

    roles_data = [
        ("Member 1\nLead Geospatial Data Engineer",
         "• backend/services/weather_service.py\n• backend/services/terrain_service.py\n• scripts/validate_weather_data.py\n• backend/data/*.csv",
         "• Open-Meteo ERA5 Reanalysis API\n• NASA POWER REST API\n• Open-Elevation SRTM API\n• Python requests, pandas, numpy\n• Vector trigonometric math",
         "Explain how raw satellite solar, wind, and elevation data are acquired for any coordinate on Earth, preprocessed without missing values, and validated for physical plausibility."),
        ("Member 2\nLead Renewable Energy Physicist",
         "• backend/services/resource_scoring.py\n• backend/services/energy_model.py\n• backend/services/rooftop_shadow_service.py",
         "• NumPy vectorization\n• Astronomical solar positioning algorithms\n• Photovoltaic physics (PR=0.78)\n• Cubic aerodynamic power curve models\n• Geometry & trigonometry (tan/atan)",
         "Explain how weather data is converted into physical energy: scoring indices, obstacle shadows, optimal tilt/azimuth angles, and 12-month generation forecasts in kWh."),
        ("Member 3\nTechno-Economics & Hardware Lead",
         "• backend/services/economics_service.py\n• backend/services/recommendation_engine.py\n• backend/services/wind_turbine_catalog.py\n• backend/services/bess_service.py",
         "• Discounted Cash Flow (DCF) modeling\n• Multi-criteria decision trees\n• Python dictionary catalogs & structural safety constraints\n• Electrochemical battery modeling (LiFePO4)",
         "Explain how physical energy yield is turned into financial viability (CAPEX, Payback, NPV), how commercial hardware is matched to site categories, and how the multi-criteria verdict is generated."),
        ("Member 4\nFull-Stack Integrator & Security QA Lead",
         "• backend/main.py\n• index.html\n• backend/services/rooftop_image_service.py\n• backend/services/regional_scanner.py\n• tests/test_api.py",
         "• FastAPI & Pydantic v2\n• Leaflet.js GIS, OpenStreetMap, ESRI Satellite, OpenTopoMap\n• Chart.js & SVG vector graphics\n• Pillow (PIL) & piexif for EXIF metadata\n• Pytest, Bandit, pip-audit, Semgrep",
         "Explain how the user interacts with the system, how frontend and backend communicate via REST, how drone photos auto-navigate the map, and how the entire system was rigorously tested.")
    ]

    for m_title, m_serv, m_tech, m_viva in roles_data:
        row_cells = table1.add_row().cells
        row_cells[0].text = m_title
        row_cells[0].paragraphs[0].runs[0].font.bold = True
        row_cells[1].text = m_serv
        row_cells[2].text = m_tech
        row_cells[3].text = m_viva
        for cell in row_cells:
            cell.paragraphs[0].paragraph_format.space_after = Pt(2)

    doc.add_page_break()

    # ==========================================
    # SECTION 2: COMPLETE TECHNOLOGY STACK
    # ==========================================
    add_header(doc, "Section 2: Complete Project Technology Stack & Architecture Topology", level=1)
    doc.add_paragraph(
        "The project is built on modern, lightweight, industry-standard technologies that require no costly cloud "
        "infrastructure or proprietary licenses. Every tier is designed for rapid execution and reproducible evaluation:"
    )

    table_tech = doc.add_table(rows=1, cols=3)
    table_tech.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_tech.style = 'Table Grid'
    h_tech = table_tech.rows[0].cells
    h_tech[0].text = "Architecture Tier"
    h_tech[1].text = "Technologies, Frameworks & Libraries"
    h_tech[2].text = "Role & Operational Purpose"
    for i in range(3):
        h_tech[i].paragraphs[0].runs[0].font.bold = True
        h_tech[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(h_tech[i], "123456")

    tech_matrix = [
        ("Frontend Client Tier",
         "• HTML5 / CSS3 (Hallmark minimalist sage-slate theme)\n• Vanilla JavaScript (ES6+, async/await, fetch API)\n• Leaflet.js 1.9.4 (Interactive Slippy Map)\n• Chart.js 4.4 (Semicircle gauge & bar charts)\n• Scalable Vector Graphics (SVG 1.1)",
         "Renders the interactive map, controls parameter pills, executes zero-reload asynchronous REST calls, draws generation charts, and updates dynamic SVG artwork without frontend build toolchain overhead."),
        ("Backend Web API Tier",
         "• Python 3.14.3\n• FastAPI 0.143.0 (ASGI high-performance web framework)\n• Starlette & Uvicorn 0.54.0 (ASGI server)\n• Pydantic v2 (Declarative request validation)\n• Python threading.Lock (Concurrency safety)",
         "Validates incoming client parameters, routes HTTP requests, enforces CORS policies, coordinates micro-services sequentially, and serializes JSON envelopes."),
        ("Data & Numerical Tier",
         "• Pandas 3.0.6 (DataFrames, resampling, time-series)\n• NumPy 2.5.4 (Vectorized arrays, L2 Ridge regression)\n• Python math module (Trigonometric functions)\n• File-based datastore (CSV & JSON format)",
         "Performs high-speed tabular processing, data aggregation, 8,760-hour array computations, circular wind vector averaging, and serialization of simulation states."),
        ("Computer Vision & Drone Vision Tier",
         "• Pillow (PIL) 13.0.0 (Image processing)\n• piexif 1.1.3 (EXIF metadata parsing)",
         "Parses uploaded rooftop/drone images, extracts embedded GPS coordinate headers (lat/lon), and performs texture edge-density and entropy scoring to estimate roof obstacle coverage."),
        ("Geospatial & Climate APIs",
         "• Open-Meteo ERA5 / Copernicus Global Reanalysis API\n• NASA POWER API (NASA Langley Research Center)\n• Open-Elevation API (Shuttle Radar Topography Mission)\n• OpenStreetMap, ESRI Satellite, OpenTopoMap",
         "Provides global climate and digital elevation observations without manual hardware deployment, powering site analysis for any coordinate on Earth."),
        ("Testing & Quality Assurance Tier",
         "• Pytest 9.2.0 (Automated test runner)\n• HTTPX 0.28.1 (Asynchronous HTTP client for testing)\n• Bandit 1.9.4 (AST security linter)\n• pip-audit 2.10.1 (CVE vulnerability audit)\n• Semgrep 1.182.1 (Static code analysis rule engine)",
         "Guarantees software correctness, verifying 78 automated test cases, OWASP Top 10 security standards, input sanitization, and dependency safety.")
    ]

    for tier, stack, purp in tech_matrix:
        row = table_tech.add_row().cells
        row[0].text = tier
        row[0].paragraphs[0].runs[0].font.bold = True
        row[1].text = stack
        row[2].text = purp
        for cell in row:
            cell.paragraphs[0].paragraph_format.space_after = Pt(2)

    doc.add_page_break()

    # ==========================================
    # SECTION 3: MEMBER 1 IN-DEPTH TECH & IMPL
    # ==========================================
    add_header(doc, "Section 3: Member 1 — Data Engineering, Satellite Weather & Topography", level=1)
    doc.add_paragraph(
        "Lead Geospatial Data Engineer | Focus: Satellite Acquisition, Data Cleaning, Trigonometric Vector Averaging & Topography\n"
        "Files: `backend/services/weather_service.py`, `backend/services/terrain_service.py`, `scripts/validate_weather_data.py`"
    )

    add_header(doc, "1. Technologies Used & Why:", level=2)
    doc.add_paragraph(
        "• Python requests: Handles HTTP GET requests with custom timeouts, error handling, and parameter encoding.\n"
        "• Pandas (pd.DataFrame, pd.date_range, resample): Time-series indexing, date parsing, and monthly aggregations.\n"
        "• NumPy (np.sin, np.cos, np.arctan2, np.deg2rad): Vectorized circular trigonometry for wind direction.\n"
        "• Open-Meteo ERA5 Reanalysis API: Primary high-speed satellite weather fetcher (responds in <1s with 100% data coverage).\n"
        "• NASA POWER API: Secondary fallback weather source.\n"
        "• Open-Elevation API: Samples global digital elevation data derived from the SRTM satellite mission."
    )

    add_header(doc, "2. How It Is Implemented in Code:", level=2)
    doc.add_paragraph(
        "A. High-Speed Satellite Fetcher (`backend/services/weather_service.py`):\n"
        "   • The function `fetch_weather_for_location(latitude, longitude)` dynamically computes the 1-year date range ending 5 days prior to today: "
        "`start_date = end_date - timedelta(days=364)`.\n"
        "   • Queries Open-Meteo's `/v1/archive` endpoint with `daily=shortwave_radiation_sum,temperature_2m_mean` and `hourly=wind_speed_10m,wind_direction_10m`.\n"
        "   • Radiation Unit Conversion: Open-Meteo returns shortwave radiation in $MJ/m^2/day$. The implementation converts this directly to electrical engineering units: "
        "`solar_kwh = (solar_mj / 3.6).clip(lower=0.0)` ($1\ kWh = 3.6\ MJ$).\n"
        "   • Resampling & Monthly Aggregation: `build_monthly_summary()` uses `daily_df.resample('MS')` and `hourly_df.resample('MS')` to calculate valid observation counts, "
        "coverage percentages, median wind speed, and 90th percentile wind speed (`quantile(0.90)`).\n"
        "   • Automatic Fallback: If Open-Meteo raises an exception or times out, the code catches it inside a `try/except` block and automatically invokes `fetch_nasa_data(latitude, longitude)`.\n\n"
        "B. Circular Wind Direction Averaging (`scripts/validate_weather_data.py` & `weather_service.py`):\n"
        "   • Why it's needed: Arithmetic averaging fails because $359^\circ$ and $1^\circ$ average to $180^\circ$ (South) instead of $0^\circ$ (North).\n"
        "   • Code Implementation:\n"
        "     `rad = np.deg2rad(valid_numeric.values)`\n"
        "     `sin_mean = np.mean(np.sin(rad))`\n"
        "     `cos_mean = np.mean(np.cos(rad))`\n"
        "     `circular_mean_deg = np.rad2deg(np.arctan2(sin_mean, cos_mean)) % 360`\n"
        "   • Evaluated on our 8,760 hourly readings, this proved a prevailing wind vector of $197.82^\circ$ (South-Southwest), matching monsoonal circulation.\n\n"
        "C. Topographic Slope & Venturi Wind Speedup (`backend/services/terrain_service.py`):\n"
        "   • Samples 3 points via Open-Elevation API: `(lat, lon)`, `(lat+0.01, lon)`, and `(lat, lon+0.01)` (offset by ~1.1 km).\n"
        "   • Elevation gradients: `d_north = (north_elev - center_elev) / 1110.0` and `d_east = (east_elev - center_elev) / 1110.0`.\n"
        "   • Slope gradient: `s = math.sqrt(d_north**2 + d_east**2)`, converted to degrees: `slope_deg = math.degrees(math.atan(s))`.\n"
        "   • Aerodynamic Ridge Speed-up: On elevated ground (>600m), terrain accelerates boundary-layer wind via the Venturi effect: "
        "`wind_terrain_speedup = round(1.0 + min(0.35, s * 2.5), 2)`, applying up to a $1.35\times$ multiplier."
    )

    doc.add_page_break()

    # ==========================================
    # SECTION 4: MEMBER 2 IN-DEPTH TECH & IMPL
    # ==========================================
    add_header(doc, "Section 4: Member 2 — Resource Scoring, Shadow Modeling & Energy Physics", level=1)
    doc.add_paragraph(
        "Lead Renewable Energy Physicist | Focus: Suitability Formulas, Astronomical Solar Position, Shadow Geometry & Physical Simulations\n"
        "Files: `backend/services/resource_scoring.py`, `backend/services/energy_model.py`, `backend/services/rooftop_shadow_service.py`"
    )

    add_header(doc, "1. Technologies Used & Why:", level=2)
    doc.add_paragraph(
        "• NumPy: High-speed vectorized computations across 8,760 hourly wind data points without slow Python for-loops.\n"
        "• Python math module: Precision trigonometric functions (`math.sin`, `math.cos`, `math.tan`, `math.radians`, `math.asin`, `math.acos`).\n"
        "• Solar Astronomical Equations: Rigorous solar altitude and azimuth positioning algorithms.\n"
        "• Photovoltaic Engineering Models: Standard IEC 61724 PV performance ratio ($PR = 0.78$).\n"
        "• Wind Turbine Aerodynamics: Continuous cubic power curve interpolation."
    )

    add_header(doc, "2. How It Is Implemented in Code:", level=2)
    doc.add_paragraph(
        "A. Resource Suitability Scoring (`backend/services/resource_scoring.py`):\n"
        "   • Solar Suitability Score (0 to 100):\n"
        "     1. Base Irradiance Score (0 to 70 pts): `np.clip((annual_avg_ghi - 2.0) / (6.0 - 2.0) * 70.0, 0.0, 70.0)`.\n"
        "     2. Temperature Derating (0 to 15 pts): PV cell voltage drops above 25°C. `if avg_temp <= 25: 15.0; elif avg_temp >= 40: 5.0; else: 15.0 - ((avg_temp - 25.0) / 15.0 * 10.0)`.\n"
        "     3. Seasonal Consistency (0 to 15 pts): `consistency_ratio = min_ghi / max_ghi; score = np.clip(consistency_ratio * 15.0, 0.0, 15.0)`.\n"
        "   • Wind Suitability Score (0 to 100):\n"
        "     1. Wind Shear Hub Extrapolation: `mean_speed_hub = mean_speed_10m * ((40.0 / 10.0) ** 0.143)` (Hellman wind shear law).\n"
        "     2. Base Speed Score (0 to 50 pts): Scaled piecewise (<3.0 m/s: poor; 3.0-6.5 m/s: moderate/good; >6.5 m/s: excellent).\n"
        "     3. Cut-In Availability Score (0 to 30 pts): `(effective_speeds >= 3.0).sum() / len(effective_speeds) * 30.0`.\n"
        "     4. Wind Power Density (WPD) Score (0 to 20 pts): `wpd = 0.5 * 1.225 * mean(v^3); score = np.clip((wpd / 200.0) * 20.0, 0.0, 20.0)`.\n\n"
        "B. Rooftop Shadow & Azimuth Micro-Placement (`backend/services/rooftop_shadow_service.py`):\n"
        "   • Astronomical Sun Position: Function `calculate_solar_angles(lat, DOY, solar_hour)` computes declination `delta = 23.45 * sin(360/365 * (DOY - 81))`, "
        "hour angle `omega = 15 * (hour - 12)`, altitude `sin(alpha) = sin(lat)*sin(delta) + cos(lat)*cos(delta)*cos(omega)`, and azimuth `gamma_s`.\n"
        "   • Winter Solstice Shadow: Sun is lowest on Dec 21 (`DOY = 355`). The shadow length is `L = neighbor_height / tan(radians(alpha_winter))`.\n"
        "   • Plot Penetration: `shadow_penetration_m = max(0.0, L - neighbor_distance_m)`. Shaded area is subtracted to yield `effective_unshaded_solar_area_m2`.\n"
        "   • Micro-Placement Zoning: Generates 3 discrete placement polygons: Unobstructed Solar Core (Green), Aerodynamic Wind Parapet (Cyan), and Shaded Buffer (Red).\n\n"
        "C. Physical Energy Generation Simulation (`backend/services/energy_model.py`):\n"
        "   • Solar PV: Sized at 7.0 m²/kWp. Monthly generation: `gen_kwh = capacity_kw * ghi * days_in_month * 0.78`.\n"
        "   • Wind Turbine: Evaluates function `turbine_power_kw(v, rated_kw)` across all 8,760 hourly speeds:\n"
        "     - If $v < 3.0$ or $v > 25.0\ m/s$: Power = $0\ kW$.\n"
        "     - If $v \ge 10.5\ m/s$: Power = $P_{rated}$.\n"
        "     - If $3.0 \le v < 10.5\ m/s$: Power = $P_{rated} \times ((v - 3.0) / (10.5 - 3.0))^{2.5}$."
    )

    doc.add_page_break()

    # ==========================================
    # SECTION 5: MEMBER 3 IN-DEPTH TECH & IMPL
    # ==========================================
    add_header(doc, "Section 5: Member 3 — Techno-Economics, Hardware Catalogs & Decision Engine", level=1)
    doc.add_paragraph(
        "Techno-Economics & Hardware Lead | Focus: 25-Year DCF Financials, Turbine Catalog, BESS Sizing & Decision Matrix\n"
        "Files: `backend/services/economics_service.py`, `backend/services/recommendation_engine.py`, `backend/services/wind_turbine_catalog.py`, `backend/services/bess_service.py`"
    )

    add_header(doc, "1. Technologies Used & Why:", level=2)
    doc.add_paragraph(
        "• Discounted Cash Flow (DCF) Financial Modeling: Incorporates time value of money, annual degradation, and OPEX.\n"
        "• Python Dictionary Data Structures: Encapsulates standardized commercial turbine hardware specifications.\n"
        "• Rule-Based Multi-Criteria Decision Tree: Deterministic logic mapping suitability scores and financials to verdicts without black-box opacity.\n"
        "• Electrochemical Modeling: Sizing Lithium Iron Phosphate (LiFePO4) storage for peak shaving and night autonomy."
    )

    add_header(doc, "2. How It Is Implemented in Code:", level=2)
    doc.add_paragraph(
        "A. Techno-Economic Feasibility Engine (`backend/services/economics_service.py`):\n"
        "   • Capital Benchmarks: Solar CAPEX = ₹50,000/kW (OPEX = 1.5%/yr). Wind CAPEX = ₹95,000/kW (OPEX = 3.0%/yr).\n"
        "   • Net Metering Revenue Formula: Self-consumed energy saves 100% of tariff; surplus energy exported to grid earns 50% export tariff:\n"
        "     `savings = (usable_energy * tariff) + (surplus_energy * tariff * 0.5)`\n"
        "   • 25-Year Discounted Net Present Value (NPV):\n"
        "     `solar_npv = -solar_capex`\n"
        "     `for year in range(1, 26):`\n"
        "     `    yearly_cash = (annual_savings * ((1 - 0.005) ** (year - 1))) - opex`\n"
        "     `    solar_npv += yearly_cash / ((1 + 0.08) ** year)`\n"
        "   • Simple Payback Period: `payback_years = capex / net_annual_cashflow`.\n"
        "   • LCOE: `capex / (annual_kwh * 25 * 0.9)` (Levelized Cost of Energy in INR/kWh).\n\n"
        "B. Commercial Wind Turbine Catalog (`backend/services/wind_turbine_catalog.py`):\n"
        "   • Houses standardized database `WIND_TURBINE_MODELS` with 4 verified commercial units:\n"
        "     1. HelixUrban V-800: 0.8 kW VAWT, 1.8 m/s cut-in, 34 dB noise, ₹85,000 CAPEX.\n"
        "     2. Aeolus Tower-2K: 2.0 kW VAWT, 2.2 m/s cut-in, 38 dB noise, ₹165,000 CAPEX.\n"
        "     3. Zephyr-3200: 3.2 kW HAWT, 2.8 m/s cut-in, 46 dB noise, ₹240,000 CAPEX.\n"
        "     4. Boreas-10K: 10.0 kW Industrial HAWT, 3.0 m/s cut-in, 7.2m rotor, ₹680,000 CAPEX.\n"
        "   • Selection Constraints: If `site_category == 'residential_rooftop'`, code strictly selects VAWT models to protect structural integrity from acoustic resonance and vibration.\n\n"
        "C. Battery Energy Storage System (BESS) Sizing (`backend/services/bess_service.py`):\n"
        "   • Sizing formula: `effective_storage_needed = (daily_load / 24 * backup_hours) / (0.85 * 0.92)`.\n"
        "   • Computes 5 kWh modular pack counts: `module_count = math.ceil(effective_storage_needed / 5.0)`.\n"
        "   • Costing: `battery_capex = installed_kwh * 13500.0` (₹13,500/kWh for LiFePO4 cells + BMS + inverter).\n\n"
        "D. Multi-Criteria Decision Engine (`backend/services/recommendation_engine.py`):\n"
        "   • Evaluates suitability thresholds: Solar viable if score >= 50 and payback <= 14 yrs. Wind viable if score >= 48 or payback <= 14 yrs.\n"
        "   • Decision Logic: If both viable -> 'Solar-Wind Hybrid System'. If only solar viable -> 'Rooftop / Ground Solar PV'. If wind dominant -> 'Wind Turbine System'. Generates dynamic justification text."
    )

    doc.add_page_break()

    # ==========================================
    # SECTION 6: MEMBER 4 IN-DEPTH TECH & IMPL
    # ==========================================
    add_header(doc, "Section 6: Member 4 — Interactive Frontend, GIS UI & Security Verification", level=1)
    doc.add_paragraph(
        "Lead Full-Stack Integrator & Security QA Lead | Focus: FastAPI Routing, Leaflet GIS, Drone Vision & Automated Testing\n"
        "Files: `backend/main.py`, `index.html`, `backend/services/rooftop_image_service.py`, `backend/services/regional_scanner.py`, `tests/test_api.py`"
    )

    add_header(doc, "1. Technologies Used & Why:", level=2)
    doc.add_paragraph(
        "• FastAPI & Pydantic v2: High-speed asynchronous Python web framework with automatic OpenAPI documentation and strict data validation.\n"
        "• Leaflet.js 1.9.4: Open-source interactive mapping library supporting multiple raster tile layers.\n"
        "• Chart.js 4.4: Canvas-based responsive charting for the 180° semicircle Siting Index gauge and 12-month generation forecast.\n"
        "• Pillow & piexif: Binary image header parsing and EXIF metadata extraction.\n"
        "• Pytest & HTTPX: Automated REST API integration and security vulnerability testing."
    )

    add_header(doc, "2. How It Is Implemented in Code:", level=2)
    doc.add_paragraph(
        "A. FastAPI Server Architecture (`backend/main.py`):\n"
        "   • Defines Pydantic models `SiteAnalysisRequest` and `RegionalScanRequest` with strict boundary constraints (`ge=-90, le=90`, regex pattern for site categories).\n"
        "   • Endpoints: `GET /` (serves index.html), `GET /api/health`, `POST /api/analyze-site`, `POST /api/regional-scan`, and `POST /api/upload-rooftop-image`.\n"
        "   • Concurrency Safety: Introduces `_SITE_ANALYSIS_LOCK = Lock()` around `analyze_site` to prevent file-write race conditions.\n"
        "   • CORS Policy: Enforces `CORSMiddleware` with `allow_origins=['*']` and `allow_credentials=False` (prevents credential theft).\n\n"
        "B. Interactive Leaflet GIS & Hallmark UI (`index.html`):\n"
        "   • Map Initialization: `L.map('map', { zoomControl: false, zoomSnap: 0.25, zoomDelta: 0.5, wheelPxPerZoomLevel: 70, inertia: true, inertiaDeceleration: 2000 })`.\n"
        "   • 3 Layer Switcher: OpenStreetMap Streets, ESRI World Imagery Satellite, and OpenTopoMap Topography.\n"
        "   • 4 Floating Map Controls: Zoom In (`map.zoomIn()`), Zoom Out (`map.zoomOut()`), Center Active Pin (`centerOnActivePin()`), and GPS Location (`locateUserPosition()`).\n"
        "   • Search Bar Glitch Fix: The `input` listener only toggles the clear `✕` button; API calls only trigger on `Enter` key or map click, preventing mid-keystroke glitches.\n"
        "   • Dynamic SVG Artwork Card: Styled with `.hero-media-card { height: 100%; }` and `.media-card-art svg { width: 100%; height: 100%; object-fit: cover; }`. Function `renderRecommendationArt(verdict)` dynamically swaps SVG vector art between Solar, Wind, and Hybrid scenes.\n\n"
        "C. Drone Photo Computer Vision (`backend/services/rooftop_image_service.py`):\n"
        "   • Upload Validation: Enforces 15 MB file ceiling and whitelists `image/jpeg`, `image/png`, and `image/webp`.\n"
        "   • EXIF Extraction: Uses `piexif.load()` to parse GPS IFD tags (GPSLatitude, GPSLongitude, GPSAltitude). Converts DMS (Degrees, Minutes, Seconds) to decimal degrees. "
        "Frontend receives GPS and auto-pans the map via `map.setView([lat, lon], 17)`.\n"
        "   • Obstruction Analysis: Converts image to grayscale, calculates Laplacian edge variance and entropy, scoring obstruction density into Low (<20%), Medium, or High.\n\n"
        "D. Pytest QA & Security Test Suite (`tests/test_api.py`):\n"
        "   • 78 automated test cases passing in 72 seconds covering:\n"
        "     - API Contract Integrity: Validates all JSON keys match frontend reads.\n"
        "     - Input Validation: 23 boundary tests verifying 422 HTTP responses on out-of-range inputs.\n"
        "     - Injection Immunity: Verifies 422 rejection on SQL injection strings (`'; DROP TABLE;`) and XSS payloads (`<script>alert(1)</script>`).\n"
        "     - File Upload Security: Rejects ZIP bombs (400), HTML files (400), oversized files >15MB (413), and sanitizes path traversal (`Path(filename).name`).\n"
        "     - E2E Happy Paths: 6 complete flows verifying Solar, Wind, Hybrid, BESS >0, and CAPEX mathematical consistency."
    )

    doc.add_page_break()

    # ==========================================
    # SECTION 7: PIPELINE MECHANICS (HOW IT WORKS)
    # ==========================================
    add_header(doc, "Section 7: Pipeline Mechanics: How Modules Work Independently & Jointly", level=1)
    doc.add_paragraph(
        "To present convincingly, the team must explain both the standalone modularity of each script and their "
        "sequential coordination inside `backend/main.py` when an end-user triggers site optimization:"
    )

    doc.add_paragraph(
        "1. Independent Execution (Standalone Modularity):\n"
        "   • Member 1's `weather_service.py` can be run independently from CLI to fetch and save satellite CSVs for any coordinate.\n"
        "   • Member 1's `terrain_service.py` can be called standalone to compute slopes and Venturi multipliers.\n"
        "   • Member 2's `resource_scoring.py` can evaluate any existing CSV dataset and output 0-100 scores.\n"
        "   • Member 2's `rooftop_shadow_service.py` can run independently given any plot geometry to output shadow lengths and solar angles.\n"
        "   • Member 3's `economics_service.py` can compute 25-year DCF tables for any given kWh generation and tariff.\n"
        "   • Member 3's `wind_turbine_catalog.py` and `bess_service.py` can be queried independently with capacity parameters.\n"
        "   • Member 4's `tests/test_api.py` can run against the backend in isolation to verify contract integrity.\n\n"
        "2. Joint Pipeline Coordination (The Live User Flow):\n"
        "   Step 1: User clicks on the Leaflet map or types coordinates in the search box.\n"
        "   Step 2: Frontend JS packages JSON payload and issues `POST http://127.0.0.1:8000/api/analyze-site`.\n"
        "   Step 3: FastAPI acquires `_SITE_ANALYSIS_LOCK` to ensure single-tenant file safety.\n"
        "   Step 4: `terrain_service.py` (Member 1) executes -> returns elevation & wind speedup factor.\n"
        "   Step 5: `weather_service.py` (Member 1) executes -> downloads/validates 365 daily & 8,760 hourly readings.\n"
        "   Step 6: `resource_scoring.py` (Member 2) executes -> calculates 0-100 Solar & Wind suitability scores.\n"
        "   Step 7: `rooftop_shadow_service.py` (Member 2) executes -> computes winter shadow and effective unshaded area.\n"
        "   Step 8: `energy_model.py` (Member 2) executes -> simulates monthly kWh generation using unshaded area and speedup.\n"
        "   Step 9: `economics_service.py` (Member 3) executes -> evaluates 25-year NPV, payback period, and LCOE.\n"
        "   Step 10: `recommendation_engine.py` (Member 3) executes -> issues final system verdict and explanation.\n"
        "   Step 11: `wind_turbine_catalog.py` & `bess_service.py` (Member 3) execute -> select hardware model and size LiFePO4 battery.\n"
        "   Step 12: FastAPI releases lock and returns unified JSON response.\n"
        "   Step 13: `index.html` (Member 4) reactively updates all DOM elements, Siting Index gauge, 12-month generation charts, and SVG vector art without browser reload."
    )

    doc.add_page_break()

    # ==========================================
    # SECTION 8: FILE INVENTORY
    # ==========================================
    add_header(doc, "Section 8: Complete Project Directory Structure & File Inventory", level=1)
    doc.add_paragraph(
        "A complete mapping of every file in `Desktop\\AI`, explaining its contents, technologies, and usage:"
    )

    table_inv = doc.add_table(rows=1, cols=3)
    table_inv.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_inv.style = 'Table Grid'
    hi = table_inv.rows[0].cells
    hi[0].text = "Directory / File Path"
    hi[1].text = "Technologies & Contents"
    hi[2].text = "Role in Project"
    for i in range(3):
        hi[i].paragraphs[0].runs[0].font.bold = True
        hi[i].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(hi[i], "123456")

    inv_rows = [
        ("index.html", "Vanilla HTML5, CSS3, JS (ES6+), Leaflet.js, Chart.js", "Frontend user interface dashboard. Houses map layers, control pills, Siting Index gauge, charts, and SVG vector art."),
        ("backend/main.py", "Python, FastAPI, Starlette, Uvicorn, Pydantic v2", "FastAPI REST API server. Handles routing, request validation, CORS, and sequential micro-service orchestration."),
        ("backend/services/weather_service.py", "Python, requests, pandas, Open-Meteo, NASA POWER", "Meteorological service. Fetches 365 daily solar and 8,760 hourly wind observations with automatic fallback."),
        ("backend/services/terrain_service.py", "Python, requests, math, Open-Elevation SRTM", "Topography service. Samples 3-point elevation coordinates to compute slope and Venturi wind speedup."),
        ("backend/services/resource_scoring.py", "Python, pandas, numpy", "Scoring engine. Computes 0-100 Solar Suitability Score and 0-100 Wind Suitability Score."),
        ("backend/services/energy_model.py", "Python, pandas, numpy", "Physical simulation engine. Models photovoltaic kWh generation (PR=0.78) and cubic wind turbine power curves."),
        ("backend/services/economics_service.py", "Python, json, math", "Cash flow engine. Computes CAPEX, OPEX, net metering savings, payback period, LCOE, and 25-yr discounted NPV (8% rate)."),
        ("backend/services/recommendation_engine.py", "Python, json", "Multi-criteria decision rule engine. Evaluates scores and financials to recommend Solar, Wind, or Hybrid systems."),
        ("backend/services/rooftop_shadow_service.py", "Python, math", "Shadow geometry service. Computes astronomical sun angles, winter solstice obstacle shadow length, and optimal tilt/azimuth."),
        ("backend/services/wind_turbine_catalog.py", "Python dictionaries", "Hardware catalog. Contains specs for 4 commercial turbines and enforces residential rooftop mounting safety rules."),
        ("backend/services/bess_service.py", "Python, math", "Battery storage model. Sizes LiFePO4 battery capacity for desired backup hours accounting for 85% DoD and 92% efficiency."),
        ("backend/services/rooftop_image_service.py", "Python, Pillow, piexif", "Drone vision service. Extracts embedded EXIF GPS tags for auto-panning and analyzes texture entropy for obstruction scoring."),
        ("backend/services/regional_scanner.py", "Python, math", "Spatial scanner. Evaluates multi-point coordinate grids (3x3 to 9x9) across 1-50 km radius to map regional Solar Hotspots and Wind Corridors."),
        ("backend/data/", "CSV and JSON runtime files", "Stores intermediate simulation outputs: daily_weather.csv, hourly_wind.csv, monthly_summary.csv, resource_scores.json, energy_simulation.json, techno_economics.json, final_recommendation.json."),
        ("reports/", "Markdown, PNG, JSON reports", "Houses master professor report, project audit, data quality report, model metrics JSON, figures, and PowerShell screenshots."),
        ("scripts/validate_weather_data.py", "Python, pandas, numpy", "CLI data validator. Audits meteorological datasets for missing values, NASA sentinels, physical bounds, and circular wind direction."),
        ("scripts/evaluate_model.py", "Python, numpy, pandas", "CLI ML benchmark. Evaluates autoregressive Ridge forecasting model vs persistence baselines and profiles latency."),
        ("tests/test_api.py", "Python, pytest, httpx", "Automated test suite (78 tests). Verifies API contracts, Pydantic bounds, SQL/XSS injection rejection, and end-to-end user flows."),
        ("TESTING_GUIDE.md", "Markdown documentation", "Operational manual with exact PowerShell commands for environment activation, data validation, testing, and starting Uvicorn.")
    ]

    for p_file, p_tech, p_role in inv_rows:
        row = table_inv.add_row().cells
        row[0].text = p_file
        row[0].paragraphs[0].runs[0].font.bold = True
        row[1].text = p_tech
        row[2].text = p_role
        for cell in row:
            cell.paragraphs[0].paragraph_format.space_after = Pt(2)

    doc.add_page_break()

    # ==========================================
    # SECTION 9: TOP 10 VIVA QUESTIONS & DEFENSE
    # ==========================================
    add_header(doc, "Section 9: Top 10 Viva Questions & High-Scoring Defense Answers", level=1)
    doc.add_paragraph(
        "Study these 10 authoritative questions and answers to defend your project with complete technical confidence:"
    )

    qa_list = [
        ("Q1: Why didn't you train a deep neural network directly to predict the final verdict or Siting Index?",
         "Answer: Siting decisions depend on human policy, budget, electricity tariffs, and physical clearances that vary independently of weather patterns. "
         "Conflating weather with financial decisions creates an uninterpretable 'black box'. Instead, we decoupled the architecture: we use empirical machine learning "
         "to forecast solar irradiance and wind speed, physical physics equations (PR=0.78 and cubic power curves) to simulate kWh energy yield, and deterministic techno-economics "
         "to evaluate payback and NPV. This ensures complete explainability and physical auditability."),

        ("Q2: How do you handle wind speed extrapolation from 10m measurement height to turbine hub height?",
         "Answer: We use the atmospheric boundary-layer Wind Shear Law (Hellman Power Law): v_hub = v_10m * (h_hub / 10)^alpha. "
         "We use a standard terrain shear exponent alpha = 0.143 for open terrain. Furthermore, on elevated ridges, terrain_service.py calculates a topographic Venturi speed-up "
         "factor S = 1.0 + min(0.35, s * 2.5), giving up to a 1.35x wind boost on hilltops."),

        ("Q3: How do you average wind direction across the year? Why not use standard mean()?",
         "Answer: Wind direction is circular angular data (0° to 360°). Arithmetic averaging fails catastrophically—359° (NNW) and 1° (NNE) average to 180° (Due South). "
         "We decompose every reading into Cartesian unit vectors: u = sin(theta) and v = cos(theta), average them separately across all 8,760 hours, and take atan2(u_bar, v_bar) mod 360°. "
         "This yielded our circular mean of 197.82° (SSW), matching the monsoonal wind corridor."),

        ("Q4: How did you validate your machine learning model to ensure there is no data leakage?",
         "Answer: In time-series forecasting, random k-fold cross-validation causes temporal leakage (training on future data to predict the past). "
         "We enforced a strict chronological 80/20 train/test split (first 286 days for training, last 72 days for test). "
         "All features use strictly lagged past data (t-1, t-2, 7-day rolling average) combined with annual solar declination harmonics (sin/cos DOY). "
         "Our trained Ridge model achieved an RMSE of 1.068 kWh/m²/day, outperforming the lag-1 persistence baseline (RMSE 1.226) by 12.8%."),

        ("Q5: How does your obstacle shadow model work on rooftops?",
         "Answer: In rooftop_shadow_service.py, we evaluate astronomical solar geometry. We identify the solar altitude and azimuth on the winter solstice (Dec 21, DOY 355), "
         "when the sun is lowest in the sky. Shadow length L = Height / tan(solar_altitude). After subtracting the distance to the neighboring obstacle, any remaining length penetrates the plot. "
         "We deduct this shaded area from the gross roof area, ensuring the solar PV capacity is simulated only over unshaded, viable roof deck."),

        ("Q6: Why do you restrict wind turbines on residential rooftops?",
         "Answer: Standard horizontal-axis wind turbines (HAWT) cause severe low-frequency acoustic noise (>50 dB) and structural vibrations that propagate through building slabs. "
         "Our wind_turbine_catalog.py enforces strict safety rules: residential rooftops can ONLY install silent, omnidirectional Vertical-Axis Wind Turbines (VAWT, <38 dB). "
         "High-efficiency HAWTs are only permitted on farmlands or open barren acreage."),

        ("Q7: How do you size the BESS battery storage, and why did you omit carbon emissions?",
         "Answer: Sizing is based on daily consumption and target night backup hours: Storage = (Daily_Load / 24 * Backup_Hours) / (DoD * Efficiency). "
         "We use LiFePO4 chemistry with 85% Depth of Discharge and 92% round-trip efficiency at ₹13,500/kWh. "
         "We intentionally omitted carbon/CO2 offsets to maintain strict engineering fidelity: grid carbon intensity varies wildly by hourly state dispatch (coal vs hydro) "
         "and cannot be calculated accurately without real-time dispatch API telemetry."),

        ("Q8: How does the computer vision drone photo upload feature work?",
         "Answer: In rooftop_image_service.py, we enforce a 15 MB safety limit and whitelist JPEG/PNG/WebP. "
         "We extract embedded EXIF GPS tags (latitude and longitude) using piexif/Pillow; if GPS is found, the Leaflet map automatically centers and zooms into the photo's location. "
         "We then run edge-detection and entropy analysis to classify obstacle density into Low, Medium, or High, adjusting the usable roof area multiplier."),

        ("Q9: What happens if NASA POWER API is down during an evaluation demo?",
         "Answer: In weather_service.py, we built an automatic high-speed fallback architecture. Our primary engine queries Open-Meteo ERA5 / Copernicus Reanalysis, "
         "which responds in under 1 second with 100% complete data. If that fails, it falls back to NASA POWER. If both fail, our local backend/data/ cache contains verified historical benchmarks, "
         "ensuring the system never crashes during a live demo."),

        ("Q10: What are the security and performance characteristics of your API?",
         "Answer: We benchmarked full-pipeline execution across 100 trials: median warm latency is 107.5 ms, peak RAM is 1.23 MB, and throughput is 9.3 executions/second on standard CPU. "
         "For security, our Pytest suite contains 78 automated tests verifying Pydantic boundary validation, SQL injection immunity, XSS payload rejection, and filename path traversal sanitization. "
         "Bandit scanned 1,341 lines with 0 issues, and pip-audit confirmed 0 known dependency vulnerabilities.")
    ]

    for q, a in qa_list:
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(8)
        p_q.paragraph_format.space_after = Pt(2)
        r_q = p_q.add_run(q)
        r_q.font.bold = True
        r_q.font.color.rgb = RGBColor(18, 52, 86)
        
        p_a = doc.add_paragraph()
        p_a.paragraph_format.space_after = Pt(6)
        r_a = p_a.add_run(a)
        r_a.font.size = Pt(10.5)

    doc.save(OUTPUT_FILE)
    print(f"[SUCCESS] Regenerated expanded Master Document: {OUTPUT_FILE}")

if __name__ == "__main__":
    create_document()
