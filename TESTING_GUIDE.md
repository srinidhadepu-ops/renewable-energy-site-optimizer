# Renewable Energy Site Selection & Optimization Engine — Testing & Operational Guide

This document details the exact PowerShell commands, environment configuration, and verification steps required to validate data quality, benchmark ML models, run the test suite, and run the client-server application.

---

## 1. Environment & Prerequisites

- **Host OS**: Microsoft Windows (Windows 10 / 11)
- **Shell**: Windows PowerShell (or Windows Terminal)
- **Base Python**: Python 3.14+ (Installed at `C:\Users\DELL\OneDrive\Desktop\AI\backend\venv`)
- **Root Directory**: `C:\Users\DELL\OneDrive\Desktop\AI`

### Virtual Environment Activation

Open PowerShell and navigate to the project root:

```powershell
Set-Location "C:\Users\DELL\OneDrive\Desktop\AI"
```

To activate the virtual environment in your current shell:

```powershell
.\backend\venv\Scripts\Activate.ps1
```

*(Alternatively, you can directly run Python executables using `.\backend\venv\Scripts\python.exe` without script execution policy restrictions).*

---

## 2. Dependency Verification

Check installed packages against requirements:

```powershell
.\backend\venv\Scripts\python.exe -m pip list
```

Ensure core packages are installed:
```powershell
.\backend\venv\Scripts\python.exe -m pip install fastapi uvicorn pydantic requests pandas numpy pillow httpx pytest
```

---

## 3. Data Pipeline & Weather Quality Verification

To audit the meteorological datasets (`daily_weather.csv`, `hourly_wind.csv`, and `weather_data.csv`) for missing values, sentinels, and physical boundary violations:

```powershell
Set-Location "C:\Users\DELL\OneDrive\Desktop\AI"
.\backend\venv\Scripts\python.exe scripts\validate_weather_data.py
```

### Expected Output:
- Scans rows, column counts, missing value percentages, and physical plausibility.
- Calculates circular mean wind direction ($\theta_{mean}$).
- Generates `reports/data_quality_results.json` and `reports/data_quality_report.md`.

---

## 4. Machine Learning Evaluation & Latency Benchmarks

To train the chronological autoregressive forecasting models (solar irradiance and wind speed), compare against domain persistence baselines, and profile execution latency across 100 trials:

```powershell
Set-Location "C:\Users\DELL\OneDrive\Desktop\AI"
.\backend\venv\Scripts\python.exe scripts\evaluate_model.py
```

### Expected Output:
- **Solar GHI Forecasting**: RMSE $\approx 1.07\ kWh/m^2/day$ ($R^2 \approx 0.20$), outperforming baseline persistence ($RMSE = 1.23$, $R^2 = -0.05$).
- **Hourly Wind Forecasting**: RMSE $\approx 0.56\ m/s$ ($R^2 \approx 0.86$), tracking diurnal cycles.
- **Computational Benchmark**: Cold-start latency $\approx 112\ ms$, median warm latency $\approx 107\ ms$, throughput $\approx 9.3\ \text{exec/sec}$, peak memory $\approx 1.23\ MB$.
- Generates `reports/model_metrics.json` and `reports/model_performance_report.md`.

---

## 5. Automated pytest Test Suite

Run all automated contract, security, boundary, and end-to-end integration tests:

```powershell
Set-Location "C:\Users\DELL\OneDrive\Desktop\AI"
.\backend\venv\Scripts\python.exe -m pytest tests\ -v --tb=short
```

### Targeted Test Commands:

- **Run only API contract verification tests**:
  ```powershell
  .\backend\venv\Scripts\python.exe -m pytest tests\test_api.py -k "TestContract" -v
  ```

- **Run only OWASP security and input sanitization tests**:
  ```powershell
  .\backend\venv\Scripts\python.exe -m pytest tests\test_api.py -k "Security or XSS or Upload" -v
  ```

- **Run happy-path end-to-end flows**:
  ```powershell
  .\backend\venv\Scripts\python.exe -m pytest tests\test_api.py -k "TestEndToEnd" -v
  ```

---

## 6. Static Code & Dependency Security Auditing

Run local security tools to inspect vulnerabilities:

```powershell
Set-Location "C:\Users\DELL\OneDrive\Desktop\AI"

# 1. Bandit Static AST Security Scanner
.\backend\venv\Scripts\python.exe -m bandit -r backend\ -x backend\venv

# 2. Pip Dependency Vulnerability Audit
.\backend\venv\Scripts\pip-audit.exe

# 3. Semgrep Static Analysis (187 rules)
.\backend\venv\Scripts\semgrep.exe --config=p/python --config=p/secrets --exclude=venv backend\
```

---

## 7. Starting Backend & Launching Application

### Start the FastAPI Backend:

```powershell
Set-Location "C:\Users\DELL\OneDrive\Desktop\AI"
.\backend\venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

- API Base URL: `http://127.0.0.1:8000`
- Interactive Swagger Documentation: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/api/health`

### Launch the Frontend:

Open `C:\Users\DELL\OneDrive\Desktop\AI\index.html` in your web browser (Chrome, Edge, Firefox), or access:
```text
http://127.0.0.1:8000/
```
The FastAPI server serves `index.html` directly from the root path (`/`).

---

## 8. Troubleshooting & Common Issues

| Issue / Error Message | Probable Cause | Remediation |
| :--- | :--- | :--- |
| `TypeError: unsupported operand type(s) for -: 'float' and 'str'` | Positional parameter order mismatch in `analyze_rooftop_shading_and_placement`. | Ensure arguments are passed via explicit keywords (`total_area_m2=...`, `neighbor_distance_m=...`). Fixed in `rooftop_shadow_service.py`. |
| `ModuleNotFoundError: No module named 'backend'` | Running scripts from within a subfolder without setting PYTHONPATH. | Execute scripts from the project root (`C:\Users\DELL\OneDrive\Desktop\AI`), or ensure `sys.path.insert(0, str(PROJECT_ROOT))` is present. |
| `FileNotFoundError: Missing daily_weather.csv` | Weather data has not yet been fetched for any coordinate. | Run `.\backend\venv\Scripts\python.exe backend\services\weather_service.py` to seed baseline data. |
| Port 8000 already in use | Previous Uvicorn instance still running. | Run `Get-Process python | Stop-Process` in PowerShell, then re-launch Uvicorn. |
