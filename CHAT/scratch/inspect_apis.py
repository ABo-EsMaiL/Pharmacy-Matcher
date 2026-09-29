import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(r"d:\AI_Engineer\Pharmacy-agy\.env")
load_dotenv(env_path)
api_key = os.getenv("UNSTRUCTURED_API_KEY")

from unstructured_transform_client._generated.api.jobs_api import JobsApi
from unstructured_transform_client._generated.api.upload_api import UploadApi
from unstructured_transform_client._generated.api.extract_api import ExtractApi
from unstructured_transform_client._generated.api.parse_api import ParseApi

for cls in [JobsApi, UploadApi, ExtractApi, ParseApi]:
    print(cls.__name__, [m for m in dir(cls) if not m.startswith('_')])

# Also inspect openapi spec or endpoints in package
pkg_dir = Path(r"D:\miniconda3\envs\venv\Lib\site-packages\unstructured_transform_client")
print("\nFiles in package:")
for p in pkg_dir.glob("**/*"):
    if p.suffix in [".json", ".yaml", ".yml"]:
        print(p.name)
