import openpyxl
from rapidfuzz import fuzz
from pathlib import Path

wb6 = openpyxl.load_workbook(r'D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-006\results_PROC-006.xlsx', data_only=True)
ws_nf = wb6['لم يُعثر عليه']

not_found_names = [row[0] for row in ws_nf.iter_rows(min_row=2, values_only=True) if row[0]]

# Load all warehouse items from cache
cache_dir = Path(r"D:\AI_Engineer\Pharmacy-agy\data\.unstructured_cache")
import json

wh_catalogs = {}
for p in cache_dir.glob("*.json"):
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
            wh_catalogs[p.stem] = [item["name"] for item in data if "name" in item]
    except Exception:
        pass

print(f"Checking {len(not_found_names)} not found items against {sum(len(v) for v in wh_catalogs.values())} warehouse items across {len(wh_catalogs)} warehouses...")

high_potential_misses = []

for nf in not_found_names:
    for wh_name, items in wh_catalogs.items():
        for item in items:
            ratio = fuzz.ratio(nf, item)
            token_sort = fuzz.token_sort_ratio(nf, item)
            # Clean spaces
            clean_r = fuzz.ratio(nf.replace(' ', ''), item.replace(' ', ''))
            score = max(ratio, token_sort, clean_r)
            if score >= 80:
                high_potential_misses.append({
                    "shortage": nf,
                    "warehouse_item": item,
                    "warehouse": wh_name,
                    "score": score
                })

print(f"\nFound {len(high_potential_misses)} high potential pairs (score >= 80%):")
seen = set()
for m in sorted(high_potential_misses, key=lambda x: x["score"], reverse=True):
    key = (m["shortage"], m["warehouse_item"])
    if key not in seen:
        seen.add(key)
        print(f"[{m['score']}%] Shortage: '{m['shortage']}' <==> WH ({m['warehouse']}): '{m['warehouse_item']}'")
