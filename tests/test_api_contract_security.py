import unittest
from unittest.mock import Mock, patch

from fastapi import HTTPException

from backend.main import (
    RegionalScanRequest,
    SiteAnalysisRequest,
    analyze_site,
    regional_scan,
    upload_rooftop_image,
)


def run_immediate(coroutine):
    """Run upload-handler coroutines whose mocked file read does not suspend."""
    try:
        coroutine.send(None)
    except StopIteration as completed:
        return completed.value
    raise AssertionError("The mocked coroutine unexpectedly suspended")


class RequestValidationTests(unittest.TestCase):
    def test_site_request_accepts_valid_payload(self):
        request = SiteAnalysisRequest(latitude=22.7, longitude=75.8)
        self.assertEqual(request.site_category, "residential_rooftop")

    def test_latitude_out_of_range_is_rejected(self):
        with self.assertRaises(ValueError):
            SiteAnalysisRequest(latitude=91, longitude=75)

    def test_longitude_out_of_range_is_rejected(self):
        with self.assertRaises(ValueError):
            SiteAnalysisRequest(latitude=22, longitude=181)

    def test_unknown_site_category_is_rejected(self):
        with self.assertRaises(ValueError):
            SiteAnalysisRequest(latitude=22, longitude=75, site_category="unknown")

    def test_area_over_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            SiteAnalysisRequest(latitude=22, longitude=75, area_m2=10_000_001)

    def test_regional_scan_bounds_are_enforced(self):
        with self.assertRaises(ValueError):
            RegionalScanRequest(latitude=22, longitude=75, grid_resolution=2)


class ApiFlowTests(unittest.TestCase):
    @staticmethod
    def image_upload(data=b"image", content_type="image/png", filename="roof.png"):
        class MemoryUpload:
            def __init__(self):
                self.content_type = content_type
                self.filename = filename

            async def read(self, size=-1):
                return data if size < 0 else data[:size]

        return MemoryUpload()

    def test_site_analysis_happy_path_returns_frontend_contract(self):
        recommendation = {
            "recommended_capacity": {"solar_kw": 5.0, "wind_kw": 1.0},
            "financial_summary": {
                "estimated_capex_inr": 500_000,
                "annual_savings_inr": 25_000,
                "payback_years": 8,
            },
        }
        with (
            patch("backend.main.get_elevation_and_terrain", return_value={"wind_terrain_speedup": 1.0}),
            patch("backend.main.fetch_weather_for_location"),
            patch("backend.main.evaluate_site_resources", return_value={
                "wind_details": {"mean_speed_10m_ms": 4.0},
                "solar_suitability_score": 75.0,
                "wind_suitability_score": 50.0,
            }),
            patch("backend.main.analyze_rooftop_shading_and_placement", return_value={"effective_unshaded_solar_area_m2": 80.0}),
            patch("backend.main.simulate_energy_generation", return_value={"annual_generation_kwh": 1000}),
            patch("backend.main.calculate_techno_economics", return_value={}),
            patch("backend.main.generate_site_recommendation", return_value=recommendation),
            patch("backend.main.select_optimal_turbine", return_value={"turbine_recommended": False}),
            patch("backend.main.size_bess_storage", return_value={"battery_capex_inr": 50_000, "installed_capacity_kwh": 10, "module_count": 4, "backup_autonomy_hours": 8}),
        ):
            result = analyze_site(SiteAnalysisRequest(latitude=22.7, longitude=75.8))

        self.assertTrue(result["success"])
        self.assertEqual(result["coordinates"], {"lat": 22.7, "lon": 75.8})
        self.assertIn("scores", result)
        self.assertIn("recommendation", result)
        self.assertEqual(result["total_capex_breakdown"]["total_turnkey_capex_inr"], 550_000)

    def test_regional_scan_happy_path_returns_data_envelope(self):
        with patch("backend.main.generate_regional_heatmap", return_value={"spatial_grid_points": []}):
            result = regional_scan(RegionalScanRequest(latitude=22.7, longitude=75.8))
        self.assertTrue(result["success"])
        self.assertIn("spatial_grid_points", result["data"])

    def test_upload_rejects_unsupported_media_type(self):
        with self.assertRaises(HTTPException) as raised:
            run_immediate(upload_rooftop_image(self.image_upload(content_type="text/html")))
        self.assertEqual(raised.exception.status_code, 400)

    def test_upload_rejects_oversized_body(self):
        upload = self.image_upload(data=b"x" * 33)
        with patch("backend.main.MAX_IMAGE_UPLOAD_BYTES", 32):
            with self.assertRaises(HTTPException) as raised:
                run_immediate(upload_rooftop_image(upload))
        self.assertEqual(raised.exception.status_code, 413)

    def test_upload_sanitizes_filename_and_returns_analysis(self):
        with patch("backend.main.analyze_rooftop_image", return_value={"image_processed": True}):
            result = run_immediate(upload_rooftop_image(self.image_upload(filename="..\\private\\roof.png")))
        self.assertEqual(result["filename"], "roof.png")
        self.assertTrue(result["analysis"]["image_processed"])

    def test_upload_does_not_return_internal_exception_text(self):
        with patch("backend.main.analyze_rooftop_image", side_effect=RuntimeError("secret internal detail")):
            with self.assertRaises(HTTPException) as raised:
                run_immediate(upload_rooftop_image(self.image_upload()))
        self.assertEqual(raised.exception.status_code, 500)
        self.assertNotIn("secret internal detail", raised.exception.detail)

    def test_upload_returns_client_error_for_unprocessable_image(self):
        with patch("backend.main.analyze_rooftop_image", return_value={"image_processed": False, "error": "private parser detail"}):
            with self.assertRaises(HTTPException) as raised:
                run_immediate(upload_rooftop_image(self.image_upload()))
        self.assertEqual(raised.exception.status_code, 400)
        self.assertNotIn("private parser detail", raised.exception.detail)

    def test_oversized_pixel_dimensions_are_rejected_cleanly(self):
        from backend.services.rooftop_image_service import analyze_rooftop_image

        oversized_image = Mock(size=(6000, 5000))
        with patch("backend.services.rooftop_image_service.Image.open", return_value=oversized_image):
            result = analyze_rooftop_image(b"not-decoded")
        self.assertFalse(result["image_processed"])
        self.assertEqual(result["error"], "Image could not be processed.")


if __name__ == "__main__":
    unittest.main()
