import os
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(r"d:\AI_Engineer\Pharmacy-agy\.env")
api_key = os.getenv("UNSTRUCTURED_API_KEY")

from unstructured_transform_client import TransformClient

client = TransformClient(
    api_key=api_key,
    server_url="https://transform.unstructured.io"
)

schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Supplier Product Names",
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "item_name_raw": {"type": "string"},
                    "source_page": {"type": ["integer", "null"]}
                },
                "required": ["item_name_raw", "source_page"]
            }
        }
    },
    "required": ["items"],
    "additionalProperties": False
}

# Test with جملة العمروووو.pdf (1 page, 57KB)
test_pdf = Path(r"d:\AI_Engineer\Pharmacy-agy\data\processes\PROC-001\input_warehouses\جملة العمروووو.pdf")
print("Submitting with wait_seconds=0...")
t0 = time.time()
with open(test_pdf, "rb") as f:
    res = client.extract.from_document(
        input=f,
        schema=schema,
        profile="balanced",
        wait_seconds=0
    )

print(f"Returned in {time.time() - t0:.2f}s!")
print("Response type:", type(res))
if hasattr(res, "model_dump"):
    d = res.model_dump()
else:
    d = dict(res)
print("Data:", d)
