import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(r"d:\AI_Engineer\Pharmacy-agy\.env")
api_key = os.getenv("UNSTRUCTURED_API_KEY")

headers = {
    "unstructured-api-key": api_key,
    "Accept": "application/json"
}

# Test various endpoints
base_urls = [
    "https://transform.unstructured.io",
    "https://transform.unstructured.io/api/v2"
]

endpoints = [
    "/files",
    "/api/v2/files",
    "/v2/files",
    "/uploads",
    "/api/v2/uploads",
    "/jobs",
    "/api/v2/jobs",
    "/documents",
    "/api/v2/documents",
    "/history",
    "/api/v2/history"
]

for base in ["https://transform.unstructured.io"]:
    for ep in endpoints:
        url = base + ep
        try:
            r = requests.get(url, headers=headers, timeout=5)
            print(f"GET {url} -> {r.status_code}")
            if r.status_code in [200, 201]:
                print("   Response:", r.text[:300])
        except Exception as e:
            print(f"GET {url} -> Error: {e}")
