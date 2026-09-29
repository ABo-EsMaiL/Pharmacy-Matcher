import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(r"d:\AI_Engineer\Pharmacy-agy\.env")
gemini_key = os.getenv("GEMINI_API_KEY")

from google import genai
from google.genai import types

client = genai.Client(api_key=gemini_key)
pdf_path = Path(r"d:\AI_Engineer\Pharmacy-agy\data\processes\PROC-001\input_warehouses\جملة العمروووو.pdf")

with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

prompt = """
Extract all drug product names from this pharmacy invoice. 
Preserve the correct Arabic drug names, dosage forms and strengths.
Return JSON: {"items": [{"item_name_raw": "...", "source_page": 1}]}
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
data = json.loads(response.text)
items = data.get("items", [])
print(f"Gemini extracted items: {len(items)}")
for it in items:
    print(" ", it)
