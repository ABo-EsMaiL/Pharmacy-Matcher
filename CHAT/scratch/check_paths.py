import requests
import os
from dotenv import load_dotenv

load_dotenv(r"d:\AI_Engineer\Pharmacy-agy\.env")
api_key = os.getenv("UNSTRUCTURED_API_KEY")

headers = {
    "unstructured-api-key": api_key,
    "Accept": "application/json"
}

paths = [
    "/api/v2/files",
    "/api/v2/file",
    "/api/v2/uploads",
    "/api/v2/upload",
    "/api/v2/sources",
    "/api/v2/source_files",
    "/api/v2/documents",
    "/api/v2/recent_files",
    "/api/v2/recent",
    "/api/v2/user",
    "/api/v2/users/me",
    "/api/v2/me",
    "/api/v1/jobs",
    "/api/v1/files",
    "/api/v1/upload",
    "/api/files",
    "/api/uploads",
    "/api/jobs",
    "/api/recent",
    "/api/recent_files"
]

for p in paths:
    url = f"https://transform.unstructured.io{p}"
    try:
        r = requests.get(url, headers=headers, timeout=3)
        if r.status_code != 404:
            print(f"{r.status_code} -> {url}")
            print("   ", r.text[:200])
    except Exception as e:
        pass
print("Done checking paths.")
