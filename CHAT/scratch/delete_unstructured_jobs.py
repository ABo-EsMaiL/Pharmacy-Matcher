import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(r"d:\AI_Engineer\Pharmacy-agy\.env")
load_dotenv(env_path)
api_key = os.getenv("UNSTRUCTURED_API_KEY")

from unstructured_transform_client import TransformClient

client = TransformClient(
    api_key=api_key,
    server_url="https://transform.unstructured.io"
)

print("Fetching jobs on Unstructured server...")
jobs = list(client.jobs.iterate())
print(f"Found {len(jobs)} jobs to delete.")

deleted_count = 0
failed_count = 0

for j in jobs:
    jid = getattr(j, "id", None)
    source = getattr(j, "source", None)
    fname = getattr(source, "filename", None) if source else "unknown"
    if jid:
        try:
            print(f"Deleting job {jid} ({fname})...")
            client.jobs.delete(jid)
            deleted_count += 1
        except Exception as e:
            print(f"Failed to delete {jid}: {e}")
            failed_count += 1

print(f"\nDeleted: {deleted_count} | Failed: {failed_count}")

# Verify
remaining = list(client.jobs.iterate())
print(f"Remaining jobs on Unstructured server: {len(remaining)}")
