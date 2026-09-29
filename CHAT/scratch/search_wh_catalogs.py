import json
import sys
from pathlib import Path

sys.path.insert(0, r"d:\AI_Engineer\Pharmacy-agy")
from src.extract.pdf_reader import parse_structured_result

wh_dir = Path(r"d:\AI_Engineer\Pharmacy-agy\data\processes\PROC-001\input_warehouses")

all_wh = {}
for p in wh_dir.glob("*.json"):
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = parse_structured_result(data, p.name)
    all_wh[p.stem] = [it["item_name_raw"] for it in items]
    print(f"{p.stem}: {len(items)} items")

search_queries = ["اسبرين", "ابيماج", "ابيمول", "فولتارين", "اوجمانتين", "سيتال"]
for q in search_queries:
    print(f"\nSearching for '{q}':")
    for wh_name, items in all_wh.items():
        matches = [it for it in items if q in it]
        if matches:
            print(f"  [{wh_name}] Found {len(matches)}: {matches[:3]}")
        else:
            print(f"  [{wh_name}] 0 matches")
