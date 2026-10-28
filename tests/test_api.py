"""
Helios & Aeolus — Renewable Optimizer
QA & Security Test Suite (pytest)
Stack: Vanilla HTML/JS + FastAPI/Python | Auth: None | DB: None (file-based)
Run: pytest tests/ -v --tb=short
"""

import io
import pytest
import httpx
from pathlib import Path

# --------------------------------------------------------------------------- #
# Configuration
BASE_URL = "http://127.0.0.1:8000"
HEADERS  = {"Content-Type": "application/json"}

# A minimal valid payload for /api/analyze-site
VALID_SITE_PAYLOAD = {
    "latitude": 17.986188,
    "longitude": 79.519546,
    "area_m2": 120.0,
    "monthly_consumption_kwh": 600.0,
    "tariff_inr_per_kwh": 7.5,
    "site_category": "residential_rooftop",
    "desired_backup_hours": 8.0,
    "neighbor_height_m": 4.0,
    "neighbor_distance_m": 6.0,
    "neighbor_direction": "East"
}

# --------------------------------------------------------------------------- #
# TASK 1 — Frontend-Backend Contract Tests
# --------------------------------------------------------------------------- #

class TestContractAnalyzeSite:
    """POST /api/analyze-site"""

    def test_happy_path_returns_200(self):
        r = httpx.post(f"{BASE_URL}/api/analyze-site", json=VALID_SITE_PAYLOAD, timeout=60)
        assert r.status_code == 200

    def test_response_has_required_top_level_keys(self):
        r = httpx.post(f"{BASE_URL}/api/analyze-site", json=VALID_SITE_PAYLOAD, timeout=60)
        body = r.json()
        required_keys = [
            "success", "coordinates", "scores", "energy_yield",
            "recommendation", "rooftop_shadow_analysis",
            "selected_wind_turbine", "bess_storage", "total_capex_breakdown"
        ]
        for k in required_keys:
            assert k in body, f"Missing key '{k}' in response"

    def test_recommendation_verdict_is_string(self):
        r = httpx.post(f"{BASE_URL}/api/analyze-site", json=VALID_SITE_PAYLOAD, timeout=60)
        verdict = r.json()["recommendation"]["verdict"]
        assert isinstance(verdict, str) and len(verdict) > 0

    def test_bess_storage_keys_present(self):
        r = httpx.post(f"{BASE_URL}/api/analyze-site", json=VALID_SITE_PAYLOAD, timeout=60)
        bess = r.json()["bess_storage"]
        for k in ["installed_capacity_kwh", "backup_autonomy_hours", "battery_capex_inr"]:
            assert k in bess

    def test_coordinates_echo_matches_input(self):
        r = httpx.post(f"{BASE_URL}/api/analyze-site", json=VALID_SITE_PAYLOAD, timeout=60)
        coords = r.json()["coordinates"]
        assert abs(coords["lat"] - VALID_SITE_PAYLOAD["latitude"]) < 0.001
        assert abs(coords["lon"] - VALID_SITE_PAYLOAD["longitude"]) < 0.001


class TestContractRegionalScan:
    """POST /api/regional-scan"""

    def test_happy_path_returns_200(self):
        payload = {"latitude": 17.986, "longitude": 79.519, "radius_km": 5.0, "grid_resolution": 3}
        r = httpx.post(f"{BASE_URL}/api/regional-scan", json=payload, timeout=90)
        assert r.status_code == 200

    def test_response_has_success_and_data(self):
        payload = {"latitude": 17.986, "longitude": 79.519, "radius_km": 5.0, "grid_resolution": 3}
        r = httpx.post(f"{BASE_URL}/api/regional-scan", json=payload, timeout=90)
        body = r.json()
        assert body.get("success") is True
        assert "data" in body


class TestContractUploadImage:
    """POST /api/upload-rooftop-image"""

    def test_invalid_content_type_returns_400(self):
        fake_pdf = io.BytesIO(b"%PDF-1.4 fake content")
        r = httpx.post(
            f"{BASE_URL}/api/upload-rooftop-image",
            files={"file": ("test.pdf", fake_pdf, "application/pdf")},
            timeout=30
        )
        assert r.status_code == 400

    def test_jpeg_upload_returns_200(self):
        # Minimal valid JPEG header (1x1 white pixel)
        jpeg_bytes = bytes([
            0xFF,0xD8,0xFF,0xE0,0x00,0x10,0x4A,0x46,0x49,0x46,0x00,0x01,
            0x01,0x00,0x00,0x01,0x00,0x01,0x00,0x00,0xFF,0xDB,0x00,0x43,
            0x00,0x08,0x06,0x06,0x07,0x06,0x05,0x08,0x07,0x07,0x07,0x09,
            0x09,0x08,0x0A,0x0C,0x14,0x0D,0x0C,0x0B,0x0B,0x0C,0x19,0x12,
            0x13,0x0F,0x14,0x1D,0x1A,0x1F,0x1E,0x1D,0x1A,0x1C,0x1C,0x20,
            0x24,0x2E,0x27,0x20,0x22,0x2C,0x23,0x1C,0x1C,0x28,0x37,0x29,
            0x2C,0x30,0x31,0x34,0x34,0x34,0x1F,0x27,0x39,0x3D,0x38,0x32,
            0x3C,0x2E,0x33,0x34,0x32,0xFF,0xD9
        ])
        r = httpx.post(
            f"{BASE_URL}/api/upload-rooftop-image",
            files={"file": ("roof.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")},
            timeout=30
        )
        # Should return 200 (image processed) or 400 (invalid image content, not type)
        assert r.status_code in (200, 400)

    def test_oversized_file_returns_413(self):
        big_data = io.BytesIO(b"\xFF\xD8" + b"X" * (16 * 1024 * 1024))  # 16 MB
        r = httpx.post(
            f"{BASE_URL}/api/upload-rooftop-image",
            files={"file": ("big.jpg", big_data, "image/jpeg")},
            timeout=60
        )
        assert r.status_code == 413


# --------------------------------------------------------------------------- #
# TASK 2 — Backend Correctness & Validation
# --------------------------------------------------------------------------- #

class TestInputValidation:
    """Pydantic validation — out-of-range values must return 422."""

    @pytest.mark.parametrize("field,value", [
        ("latitude", 91.0),           # > 90
        ("latitude", -91.0),          # < -90
        ("longitude", 181.0),         # > 180
        ("longitude", -181.0),        # < -180
        ("area_m2", 0),               # must be > 0
        ("area_m2", 10_000_001),      # exceeds max
        ("monthly_consumption_kwh", 0),
        ("monthly_consumption_kwh", 10_000_001),
        ("tariff_inr_per_kwh", 0),
        ("tariff_inr_per_kwh", 1001),
        ("desired_backup_hours", -1),
        ("desired_backup_hours", 25),  # > 24
        ("neighbor_height_m", -1),
        ("neighbor_height_m", 201),   # > 200
        ("neighbor_distance_m", -1),
        ("neighbor_distance_m", 501), # > 500
    ])
    def test_out_of_range_returns_422(self, field, value):
        payload = {**VALID_SITE_PAYLOAD, field: value}
        r = httpx.post(f"{BASE_URL}/api/analyze-site", json=payload, timeout=30)
        assert r.status_code == 422, f"Expected 422 for {field}={value}, got {r.status_code}"

    @pytest.mark.parametrize("bad_cat", [
        "unknown_type", "RESIDENTIAL_ROOFTOP", "rooftop", "'; DROP TABLE; --",
        "<script>alert(1)</script>", "../etc/passwd", ""
    ])
    def test_invalid_site_category_returns_422(self, bad_cat):
        payload = {**VALID_SITE_PAYLOAD, "site_category": bad_cat}
        r = httpx.post(f"{BASE_URL}/api/analyze-site", json=payload, timeout=30)
        assert r.status_code == 422, f"Expected 422 for site_category='{bad_cat}'"

    @pytest.mark.parametrize("bad_dir", [
        "northwest", "NE", "Up", "'; DROP;", "<img>", ""
    ])
    def test_invalid_neighbor_direction_returns_422(self, bad_dir):
        payload = {**VALID_SITE_PAYLOAD, "neighbor_direction": bad_dir}
        r = httpx.post(f"{BASE_URL}/api/analyze-site", json=payload, timeout=30)
        assert r.status_code == 422, f"Expected 422 for neighbor_direction='{bad_dir}'"

    def test_regional_scan_radius_too_large_returns_422(self):
        payload = {"latitude": 17.986, "longitude": 79.519, "radius_km": 51.0, "grid_resolution": 3}
        r = httpx.post(f"{BASE_URL}/api/regional-scan", json=payload, timeout=30)
        assert r.status_code == 422

    def test_regional_scan_grid_too_fine_returns_422(self):
        payload = {"latitude": 17.986, "longitude": 79.519, "radius_km": 5.0, "grid_resolution": 10}
        r = httpx.post(f"{BASE_URL}/api/regional-scan", json=payload, timeout=30)
        assert r.status_code == 422


class TestErrorHandling:
    """Error responses must not leak internal stack traces."""

    def test_error_body_does_not_contain_traceback(self):
        # Send an invalid payload to trigger a validation error
        r = httpx.post(f"{BASE_URL}/api/analyze-site", json={"latitude": 999}, timeout=30)
        body = r.text
        assert "Traceback" not in body
        assert "File \"" not in body

    def test_404_for_unknown_route(self):
        r = httpx.get(f"{BASE_URL}/api/nonexistent", timeout=10)
        assert r.status_code == 404

    def test_health_endpoint_returns_ok(self):
        r = httpx.get(f"{BASE_URL}/api/health", timeout=10)
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


# --------------------------------------------------------------------------- #
# TASK 3 — Security Tests (OWASP oriented)
# --------------------------------------------------------------------------- #

class TestCORSSecurity:
    """CORS must not send credentials with wildcard origin."""

    def test_cors_no_credentials_header(self):
        r = httpx.options(
            f"{BASE_URL}/api/analyze-site",
            headers={"Origin": "http://evil.com", "Access-Control-Request-Method": "POST"},
            timeout=10
        )
        # allow-credentials: false means no Access-Control-Allow-Credentials: true
        assert r.headers.get("access-control-allow-credentials", "false").lower() != "true"


class TestXSSAndInjection:
    """Verify XSS/injection payloads are rejected by validation, not reflected."""

    XSS_PAYLOADS = [
        "<script>alert(1)</script>",
        "'; DROP TABLE sites; --",
        "${7*7}",
        "{{7*7}}",
        "../../../etc/passwd",
    ]

    @pytest.mark.parametrize("payload", XSS_PAYLOADS)
    def test_xss_in_site_category_returns_422(self, payload):
        r = httpx.post(
            f"{BASE_URL}/api/analyze-site",
            json={**VALID_SITE_PAYLOAD, "site_category": payload},
            timeout=30
        )
        assert r.status_code == 422

    @pytest.mark.parametrize("payload", XSS_PAYLOADS)
    def test_xss_in_neighbor_direction_returns_422(self, payload):
        r = httpx.post(
            f"{BASE_URL}/api/analyze-site",
            json={**VALID_SITE_PAYLOAD, "neighbor_direction": payload},
            timeout=30
        )
        assert r.status_code == 422


class TestFileUploadSecurity:
    """File upload endpoint security checks."""

    def test_zip_bomb_content_type_rejected(self):
        r = httpx.post(
            f"{BASE_URL}/api/upload-rooftop-image",
            files={"file": ("bomb.zip", io.BytesIO(b"PK\x03\x04fake"), "application/zip")},
            timeout=15
        )
        assert r.status_code == 400

    def test_html_file_rejected(self):
        html = b"<html><script>alert(1)</script></html>"
        r = httpx.post(
            f"{BASE_URL}/api/upload-rooftop-image",
            files={"file": ("xss.html", io.BytesIO(html), "text/html")},
            timeout=15
        )
        assert r.status_code == 400

    def test_filename_with_path_traversal_handled(self):
        # Even with a path-traversal filename, backend should sanitize using Path().name
        jpeg_min = bytes([0xFF, 0xD8, 0xFF, 0xD9])
        r = httpx.post(
            f"{BASE_URL}/api/upload-rooftop-image",
            files={"file": ("../../etc/passwd.jpg", io.BytesIO(jpeg_min), "image/jpeg")},
            timeout=15
        )
        # Should return 200 or 400 (invalid image), never expose the traversal path
        assert r.status_code in (200, 400)
        if r.status_code == 200:
            assert "../../" not in r.json().get("filename", "")
            assert "etc" not in r.json().get("filename", "")


# --------------------------------------------------------------------------- #
# TASK 4 — End-to-End Happy-Path Flows
# --------------------------------------------------------------------------- #

class TestEndToEndHappyPaths:
    """Full user flows: input → API → expected key fields in response."""

    def test_solar_dominated_site(self):
        """High-GHI, low-wind inland site → expect Solar PV in verdict."""
        payload = {**VALID_SITE_PAYLOAD, "latitude": 23.0, "longitude": 72.5}
        r = httpx.post(f"{BASE_URL}/api/analyze-site", json=payload, timeout=60)
        assert r.status_code == 200
        verdict = r.json()["recommendation"]["verdict"]
        assert "Solar" in verdict or "Hybrid" in verdict

    def test_bess_sized_nonzero(self):
        """BESS must always size to > 0 kWh for any valid input."""
        r = httpx.post(f"{BASE_URL}/api/analyze-site", json=VALID_SITE_PAYLOAD, timeout=60)
        assert r.status_code == 200
        assert r.json()["bess_storage"]["installed_capacity_kwh"] > 0

    def test_rooftop_shadow_analysis_present_and_valid(self):
        """Shadow analysis must include unshaded area ≤ total area."""
        r = httpx.post(f"{BASE_URL}/api/analyze-site", json=VALID_SITE_PAYLOAD, timeout=60)
        assert r.status_code == 200
        shadow = r.json()["rooftop_shadow_analysis"]
        unshaded = shadow["effective_unshaded_solar_area_m2"]
        assert 0 < unshaded <= VALID_SITE_PAYLOAD["area_m2"]

    def test_different_site_categories_all_succeed(self):
        """All 5 valid site categories must return 200."""
        categories = [
            "residential_rooftop", "commercial_building",
            "farmland_agri", "open_barren_land", "hillcrest_ridge"
        ]
        for cat in categories:
            payload = {**VALID_SITE_PAYLOAD, "site_category": cat}
            r = httpx.post(f"{BASE_URL}/api/analyze-site", json=payload, timeout=60)
            assert r.status_code == 200, f"Category '{cat}' failed with {r.status_code}"

    def test_total_capex_equals_sum_of_parts(self):
        """total_turnkey_capex_inr must equal gen_capex + bess_capex."""
        r = httpx.post(f"{BASE_URL}/api/analyze-site", json=VALID_SITE_PAYLOAD, timeout=60)
        assert r.status_code == 200
        cb = r.json()["total_capex_breakdown"]
        expected = cb["generation_capex_inr"] + cb["bess_battery_capex_inr"]
        assert abs(cb["total_turnkey_capex_inr"] - expected) < 1  # allow rounding error of Re 1

    def test_annual_yield_positive(self):
        """Hybrid annual generation must be > 0 kWh."""
        r = httpx.post(f"{BASE_URL}/api/analyze-site", json=VALID_SITE_PAYLOAD, timeout=60)
        assert r.status_code == 200
        annual = r.json()["energy_yield"]["hybrid_system"]["annual_generation_kwh"]
        assert annual > 0
