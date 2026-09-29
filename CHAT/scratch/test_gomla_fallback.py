from pathlib import Path
import sys
from dotenv import load_dotenv

sys.path.insert(0, r"d:\AI_Engineer\Pharmacy-agy")
load_dotenv(r"d:\AI_Engineer\Pharmacy-agy\.env")

from src.extract.pdf_reader import extract_items_from_pdf
from src.config import load_config

config = load_config()

pdf_file = Path(r"d:\AI_Engineer\Pharmacy-agy\data\processes\PROC-001\input_warehouses\جملة العمروووو.pdf")

# Remove any existing json cache for gomla to test the live fallback
cache_file = Path(r"d:\AI_Engineer\Pharmacy-agy\data\.unstructured_cache") / "c7b508f7ce1669255653b6fa0f9ea1fc_extract.json"
if cache_file.exists():
    cache_file.unlink()

items = extract_items_from_pdf(
    pdf_file,
    api_key=config.unstructured_api_key,
    base_url=config.unstructured_base_url,
    gemini_api_key=config.gemini_api_key,
    profile="balanced"
)

print(f"\nFinal extracted items count: {len(items)}")
for it in items:
    print("  ", it)
