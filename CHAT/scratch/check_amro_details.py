import sys
sys.path.insert(0, 'd:/AI_Engineer/Pharmacy-agy')
import json
from pathlib import Path
import openpyxl

cache_dir = Path("data/cache")
amro_cache = list(cache_dir.glob("*جملة العمرو*.json"))
print("Amro cache files:", amro_cache)
if amro_cache:
    with open(amro_cache[0], "r", encoding="utf-8") as f:
        amro_items = json.load(f)
    print(f"Total items in Amro cache: {len(amro_items)}")
    for idx, item in enumerate(amro_items, 1):
        print(f"  {idx}. {item.get('item_name_raw')}")

wb1 = openpyxl.load_workbook('d:/AI_Engineer/Pharmacy-agy/data/processes/PROC-001/results_PROC-001.xlsx')
ws_amro1 = wb1['جملة العمروووو.pdf']
rows = list(ws_amro1.iter_rows(values_only=True))
print("\nPROC-001 Amro sheet rows:")
for r in rows:
    print(" ", r)
