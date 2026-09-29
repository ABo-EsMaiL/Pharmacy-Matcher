import os
import inspect
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

print("Type of client.jobs:", type(client.jobs))
print("Signature of delete:", inspect.signature(client.jobs.delete))
print("Doc of delete:", client.jobs.delete.__doc__)
