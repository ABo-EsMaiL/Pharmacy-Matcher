from pathlib import Path
import os
import sys
import json
from dotenv import load_dotenv

sys.path.insert(0, r"d:\AI_Engineer\Pharmacy-agy")
load_dotenv(r"d:\AI_Engineer\Pharmacy-agy\.env")

from src.extract.pdf_reader import extract_items_from_pdf
from src.config import load_config

config = load_config()

pdf_file = Path(r"d:\AI_Engineer\Pharmacy-agy\data\processes\PROC-001\input_warehouses\الهضبة الاثنين نقدى0.pdf")

items = extract_items_from_pdf(
    pdf_file,
    api_key=config.unstructured_api_key,
    base_url=config.unstructured_base_url,
    gemini_api_key=config.gemini_api_key,
    profile="balanced"
)

print(f"Hadaba extracted items: {len(items)}")
if items:
    print(f"First 5 items:")
    for it in items[:5]:
        print(" ", it)
