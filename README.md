# Renewable Energy Site Selection & Optimization Engine

An AI and Satellite Geospatial Decision Support System that analyzes any geographical location on Earth to recommend optimal **Solar PV**, **Wind Turbine**, or **Solar-Wind Hybrid** installations.

## Features
- **Live Satellite Climate Data**: Automatically retrieves real 1-year daily Global Horizontal Irradiance ($GHI$) and 8,760 hourly wind speed & direction observations via NASA POWER and Copernicus/ERA5 APIs.
- **Topographic Terrain Modeling**: Estimates slope, elevation, and boundary-layer wind speed-up factors using multi-point digital elevation models.
- **Techno-Economic Sizing**: Calculates physical system capacity (kWp), CAPEX, annual bill savings, Simple Payback Period (years), LCOE, and 25-Year Net Present Value (NPV).
- **Multi-Criteria Recommendation Engine**: Provides human-readable justifications and optimal sizing for Solar, Wind, or Hybrid systems.
- **Interactive Web Interface**: Leaflet-based map with OpenStreetMap, ESRI satellite imagery, and topographic terrain overlays.

## Project Structure
```text
AI/
├── index.html                     # Interactive Frontend Dashboard & Map
├── requirements.txt               # Python package dependencies
├── .gitignore
└── backend/
    ├── main.py                    # FastAPI REST API (http://127.0.0.1:8000)
    ├── data/                      # Simulation benchmarks and sample datasets
    └── services/
        ├── weather_service.py     # Live satellite weather & wind fetcher
        ├── terrain_service.py     # Elevation, slope & ridge acceleration model
        ├── resource_scoring.py    # 0-100 Solar & Wind Suitability Scoring
        ├── energy_model.py        # Physical energy generation simulation (kWh)
        ├── economics_service.py   # CAPEX, OPEX, Payback & NPV financial models
        ├── recommendation_engine.py # Decision tree and natural language rationale
        └── validate_and_summarize.py # Missing data cleaning & quality control
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Backend API
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be available at: `http://127.0.0.1:8000/docs`

### 3. Launch the Web Interface
Double-click `index.html` or open it in your browser. Click anywhere on the map and hit **Run Renewable Optimization**!
