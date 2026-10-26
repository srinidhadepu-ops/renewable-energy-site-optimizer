from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import os

# Phase 1 Core Services
from backend.services.weather_service import fetch_weather_for_location
from backend.services.resource_scoring import evaluate_site_resources
from backend.services.terrain_service import get_elevation_and_terrain
from backend.services.energy_model import simulate_energy_generation
from backend.services.economics_service import calculate_techno_economics
from backend.services.recommendation_engine import generate_site_recommendation

# Phase 2 Advanced Siting & System Selection Services
from backend.services.wind_turbine_catalog import select_optimal_turbine
from backend.services.bess_service import size_bess_storage
from backend.services.rooftop_shadow_service import analyze_rooftop_shading_and_placement
from backend.services.rooftop_image_service import analyze_rooftop_image
from backend.services.regional_scanner import generate_regional_heatmap

app = FastAPI(
    title="Helios & Aeolus — Renewable Siting & Optimization Engine",
    description="Geospatial AI & Satellite Decision Support System for Solar, Wind, and BESS Storage",
    version="2.5.0"
)

# Enable CORS for frontend UI
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
    # Phase 2 Parameters
    site_category: str = Field(default="residential_rooftop", description="residential_rooftop, commercial_building, farmland_agri, open_barren_land, hillcrest_ridge")
    desired_backup_hours: float = Field(default=8.0, ge=0.0, le=24.0)
    neighbor_height_m: float = Field(default=4.0, ge=0.0)
    neighbor_distance_m: float = Field(default=6.0, ge=0.0)
    neighbor_direction: str = Field(default="East")

class RegionalScanRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    radius_km: float = Field(default=8.0, ge=1.0, le=50.0)
    grid_resolution: int = Field(default=5, ge=3, le=9)

@app.get("/")
def serve_home():
    html_path = Path(__file__).resolve().parent.parent / "index.html"
    if html_path.exists():
        return FileResponse(html_path)
    return {"message": "Helios & Aeolus Renewable Optimizer API running"}

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "system": "Helios & Aeolus Renewable Optimizer",
        "phase_1_connected": True,
        "phase_2_connected": True,
        "active_modules": [
            "Satellite Weather Fetcher",
            "Topographic Terrain & Ridge Acceleration",
            "Solar & Wind Physics Modeler",
            "Specific Wind Turbine Catalog & Sizing",
            "BESS Battery Storage Sizing",
            "Rooftop Azimuth & Shadow Placement",
            "Rooftop Drone/Photo Vision Analyzer",
            "Regional Spatial Heatmap Scanner"
        ]
    }

@app.post("/api/analyze-site")
def analyze_site(req: SiteAnalysisRequest):
    """
    Seamlessly integrates Phase 1 (Geospatial Satellite & Climate Engine)
    with Phase 2 (Site Category, Shadow/Orientation, Wind Turbine Model, BESS Storage).
    """
    try:
        # 1. Real-time terrain & ridge slope analysis
        terrain_res = get_elevation_and_terrain(req.latitude, req.longitude)
        terrain_speedup = terrain_res.get("wind_terrain_speedup", 1.0)
        
        # 2. Live Satellite weather fetch (NASA & Copernicus reanalysis)
        fetch_weather_for_location(req.latitude, req.longitude)
        
        # 3. Resource Suitability Scoring
        scores_res = evaluate_site_resources(terrain_speedup=terrain_speedup)
        
        # 4. Phase 2: Rooftop Azimuth, Neighbor Shadow & Micro-Placement Analysis
        shadow_res = analyze_rooftop_shading_and_placement(
            latitude=req.latitude,
            longitude=req.longitude,
            total_area_m2=req.area_m2,
            neighbor_building_height_m=req.neighbor_height_m,
            neighbor_distance_m=req.neighbor_distance_m,
            neighbor_direction=req.neighbor_direction
        )
        effective_solar_area = shadow_res["effective_unshaded_solar_area_m2"]

        # 5. Physical Energy Simulation (using unshaded solar area)
        energy_res = simulate_energy_generation(
            area_m2=effective_solar_area,
            monthly_consumption_kwh=req.monthly_consumption_kwh,
            terrain_speedup=terrain_speedup
        )
        
        # 6. Techno-Economics
        econ_res = calculate_techno_economics(
            tariff_inr_per_kwh=req.tariff_inr_per_kwh
        )
        
        # 7. Final Recommendation
        rec_res = generate_site_recommendation()

        # 8. Phase 2: Concrete Wind Turbine Model & Equipment Selection
        turbine_selection = select_optimal_turbine(
            site_category=req.site_category,
            available_area_m2=req.area_m2,
            mean_wind_speed_10m=scores_res["wind_details"]["mean_speed_10m_ms"],
            wind_suitability_score=scores_res["wind_suitability_score"]
        )

        # 9. Phase 2: BESS Battery Storage Sizing
        daily_consumption = req.monthly_consumption_kwh / 30.0
        bess_res = size_bess_storage(
            daily_consumption_kwh=daily_consumption,
            solar_capacity_kw=rec_res["recommended_capacity"]["solar_kw"],
            wind_capacity_kw=rec_res["recommended_capacity"]["wind_kw"],
            desired_backup_hours=req.desired_backup_hours
        )

        # Totalized System CAPEX (Solar + Selected Turbine + BESS)
        base_capex = rec_res["financial_summary"]["estimated_capex_inr"]
        total_system_capex_with_bess = base_capex + bess_res["battery_capex_inr"]

        return {
            "success": True,
            "coordinates": {"lat": req.latitude, "lon": req.longitude},
            "site_category": req.site_category,
            "terrain": terrain_res,
            "scores": scores_res,
            "energy_yield": energy_res,
            "financials": econ_res,
            "recommendation": rec_res,
            # Phase 2 Extended Results
            "rooftop_shadow_analysis": shadow_res,
            "selected_wind_turbine": turbine_selection,
            "bess_storage": bess_res,
            "total_capex_breakdown": {
                "generation_capex_inr": base_capex,
                "bess_battery_capex_inr": bess_res["battery_capex_inr"],
                "total_turnkey_capex_inr": total_system_capex_with_bess
            }
        }
        
    except Exception as e:
        print(f"Error during site analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/regional-scan")
def regional_scan(req: RegionalScanRequest):
    """Generates multi-point spatial raster heatmap across the selected area."""
    try:
        heatmap_res = generate_regional_heatmap(
            center_lat=req.latitude,
            center_lon=req.longitude,
            radius_km=req.radius_km,
            grid_resolution=req.grid_resolution
        )
        return {"success": True, "data": heatmap_res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-rooftop-image")
async def upload_rooftop_image(file: UploadFile = File(...)):
    """Processes uploaded rooftop or drone image, extracting GPS & roof surface obstruction."""
    try:
        contents = await file.read()
        analysis = analyze_rooftop_image(contents)
        return {"success": True, "filename": file.filename, "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
