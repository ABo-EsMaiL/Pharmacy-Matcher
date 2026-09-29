import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, r"d:\AI_Engineer\Pharmacy-agy")
load_dotenv(r"d:\AI_Engineer\Pharmacy-agy\.env")

from src.fast_match.coordinator import FastCoordinator
from src.config import load_config
from src.extract.excel_reader import read_excel, extract_item_names
from src.extract.pdf_reader import extract_items_from_pdf

config = load_config()
coord = FastCoordinator(config)

# Load real shortage items
shortages_path = Path(r"d:\AI_Engineer\Pharmacy-agy\data\processes\PROC-001\input_shortages\0913.xlsx")
if not shortages_path.exists():
    shortages_path = list(Path(r"d:\AI_Engineer\Pharmacy-agy\data\processes").glob("**/input_shortages/*.xlsx"))[0]

rows = read_excel(shortages_path)
shortage_items = extract_item_names(rows, source_file=shortages_path.name)

# Load real warehouse items
wh_file = Path(r"d:\AI_Engineer\Pharmacy-agy\data\processes\PROC-001\input_warehouses\السلام شبين.pdf")
wh_items = extract_items_from_pdf(wh_file, config.unstructured_api_key, gemini_api_key=config.gemini_api_key)

print(f"Shortages: {len(shortage_items)}, WH items: {len(wh_items)}")

# Run process for just this warehouse
t0 = time.time()
res = coord.process(shortage_items[:200], {"السلام شبين.pdf": wh_items})
print(f"Completed in {time.time() - t0:.1f}s!")
print(f"Matched: {len(res['summary']['warehouses']['السلام شبين.pdf']['matched'])}")
print(f"Review: {len(res['summary']['warehouses']['السلام شبين.pdf']['needs_review'])}")
