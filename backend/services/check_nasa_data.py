
import requests

url = "https://power.larc.nasa.gov/api/temporal/hourly/point"

params = {
    "parameters": "WD10M,WS10M",
    "community": "RE",
    "longitude": 75.8577,
    "latitude": 22.7196,
    "start": "20260725",
    "end": "20260727",
    "format": "JSON",
    "time-standard": "UTC"
}

response = requests.get(url, params=params, timeout=60)

print("HTTP status:", response.status_code)
response.raise_for_status()

result = response.json()
parameters = result["properties"]["parameter"]

for name, values in parameters.items():
    print(f"\n{name}:")
    for timestamp, value in list(values.items())[:12]:
        print(timestamp, value)
