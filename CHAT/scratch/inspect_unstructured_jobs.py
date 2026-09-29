import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(r"d:\AI_Engineer\Pharmacy-agy\.env")
load_dotenv(env_path)
api_key = os.getenv("UNSTRUCTURED_API_KEY")
print(f"API key loaded: {api_key[:6]}...")

from unstructured_transform_client import TransformClient

client = TransformClient(
    api_key=api_key,
    server_url="https://transform.unstructured.io"
)

print("\n--- Listing Jobs on Unstructured Server ---")
try:
    jobs = list(client.jobs.iterate())
    print(f"Total jobs found: {len(jobs)}")
    for j in jobs:
        source = getattr(j, "source", None)
        fname = getattr(source, "filename", None) if source else None
        jid = getattr(j, "id", None)
        status = getattr(j, "status", None)
        created = getattr(j, "created_at", None)
        print(f"Job ID: {jid} | File: {fname} | Status: {status} | Created: {created}")
except Exception as e:
    print("Error listing jobs:", e)

print("\n--- Client APIs ---")
print("JobsApi methods:", [m for m in dir(client.jobs) if not m.startswith("_")])
