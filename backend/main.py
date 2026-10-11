from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
import json

from backend.services.weather_service import fetch_weather_for_location
from backend.services.resource_scoring import evaluate_site_resources
from backend.services.terrain_service import get_elevation_and_terrain
from backend.services.energy_model import simulate_energy_generation
from backend.services.economics_service import calculate_techno_economics
from backend.services.recommendation_engine import generate_site_recommendation

app = FastAPI(
    title="Renewable Energy Site Selection & Optimization API",
    description="Geospatial AI & Satellite Decision System for Solar and Wind Power",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SiteAnalysisRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    area_m2: float = Field(default=100.0, gt=0)
    monthly_consumption_kwh: float = Field(default=500.0, gt=0)
    tariff_inr_per_kwh: float = Field(default=7.5, gt=0)

@app.get("/api/health")
def health():
    return {"status": "ok", "message": "Renewable Optimizer Backend operational"}

@app.post("/api/analyze-site")
def analyze_site(req: SiteAnalysisRequest):
    """
    Executes live geospatial satellite & terrain analysis for ANY coordinates clicked.
    1. Terrain analysis: checks elevation and hillcrest/ridge slope speedup.
    2. Live Satellite weather fetch: retrieves 1-year daily solar GHI and hourly wind speeds.
    3. Resource suitability evaluation: solar and wind scores 0-100.
    4. Physical capacity & energy simulation.
    5. Techno-economics (CAPEX, OPEX, Payback, NPV).
    6. System recommendation: Solar PV, Wind Turbine, or Solar-Wind Hybrid.
    """
    try:
        # Step 1: Real-time terrain & ridge slope analysis
        terrain_res = get_elevation_and_terrain(req.latitude, req.longitude)
        terrain_speedup = terrain_res.get("wind_terrain_speedup", 1.0)
        
        # Step 2: Live Satellite weather data for this specific location
        fetch_weather_for_location(req.latitude, req.longitude)
        
        # Step 3: Resource Suitability Scoring (incorporating terrain speedup)
        scores_res = evaluate_site_resources(terrain_speedup=terrain_speedup)
        
        # Step 4: Physical Energy Simulation
        energy_res = simulate_energy_generation(
            area_m2=req.area_m2,
            monthly_consumption_kwh=req.monthly_consumption_kwh,
            terrain_speedup=terrain_speedup
        )
        
        # Step 5: Techno-Economics
        econ_res = calculate_techno_economics(
            tariff_inr_per_kwh=req.tariff_inr_per_kwh
        )
        
        # Step 6: Final Recommendation
        rec_res = generate_site_recommendation()
        
        return {
            "success": True,
            "coordinates": {"lat": req.latitude, "lon": req.longitude},
            "terrain": terrain_res,
            "scores": scores_res,
            "energy_yield": energy_res,
            "financials": econ_res,
            "recommendation": rec_res
        }
        
    except Exception as e:
        print(f"Error during site analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
