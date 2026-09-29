import json
from pathlib import Path

cache_dir = Path(r"D:\AI_Engineer\Pharmacy-agy\data\.unstructured_cache")
cache_files = list(cache_dir.glob("*.json"))
print(f"Found {len(cache_files)} cache files:")
total_wh_items = 0
for cf in cache_files:
    data = json.loads(cf.read_text(encoding="utf-8"))
    items = data.get("items", [])
    print(f"  - {cf.name}: {len(items)} items")
    total_wh_items += len(items)

print(f"Total warehouse items in cache: {total_wh_items}")
