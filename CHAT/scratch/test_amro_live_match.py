import sys
sys.path.insert(0, 'd:/AI_Engineer/Pharmacy-agy')
from src.config import load_config
from src.extract.excel_reader import read_excel, extract_item_names
from src.extract.pdf_reader import extract_items_from_pdf
from src.fast_match.coordinator import FastCoordinator
from pathlib import Path

config = load_config()

shortages_raw = read_excel(Path('data/processes/PROC-002/input_shortages/0913.xlsx'))
shortages = extract_item_names(shortages_raw, 'أسم الصنف')

unique_shortages = {}
for item in shortages:
    name = item.get("item_name_raw", "")
    if name and name not in unique_shortages:
        unique_shortages[name] = item
deduped_shortages = list(unique_shortages.values())

amro_path = Path('data/processes/PROC-002/input_warehouses/جملة العمروووو.pdf')
amro_items = extract_items_from_pdf(amro_path, config.unstructured_api_key)

coordinator = FastCoordinator(config)
res = coordinator._match_warehouse(deduped_shortages, amro_items, "جملة العمروووو.pdf")
print("Amro Result now:")
print("Matched:", res["matched"])
print("Review:", res["needs_review"])
