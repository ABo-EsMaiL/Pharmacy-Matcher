import time
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(r"d:\AI_Engineer\Pharmacy-agy\.env")
gemini_key = os.getenv("GEMINI_API_KEY")

from google import genai
from google.genai import types

client = genai.Client(api_key=gemini_key)

pdf_path = Path(r"d:\AI_Engineer\Pharmacy-agy\data\processes\PROC-001\input_warehouses\الهضبة الاثنين نقدى0.pdf")
if not pdf_path.exists():
    pdf_path = Path(r"d:\AI_Engineer\Pharmacy\الهضبة الاثنين نقدى0.pdf")

print(f"Testing Gemini extraction on: {pdf_path.name} ({pdf_path.stat().st_size / 1024:.1f} KB)")
start_time = time.time()

with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

prompt = """
Extract all drug product names from this pharmacy invoice/catalog PDF.
Return a clean JSON object with a single key 'items', which is a list of objects:
{"items": [{"item_name_raw": "...", "source_page": 1}, ...]}
Do not summarize. Extract every drug entry exactly as written.
"""

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=[
        types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
        prompt
    ],
    config=types.GenerateContentConfig(
        response_mime_type="application/json"
    )
)

elapsed = time.time() - start_time
print(f"Gemini completed in {elapsed:.2f} seconds!")
import json
data = json.loads(response.text)
items = data.get("items", [])
print(f"Extracted {len(items)} items!")
if items:
    print("First 3 items:", items[:3])
    print("Last 3 items:", items[-3:])
