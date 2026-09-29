import sys
sys.path.insert(0, ".")
import json
from pathlib import Path
from src.extract.excel_reader import read_excel, extract_item_names
from src.extract.pdf_reader import _get_file_hash, parse_structured_result
from src.fast_match.coordinator import is_safe_auto_match
from src.fast_match.search import FastCandidateFinder, normalize_text

proc_dir = Path("data/processes/PROC-009")
shortages_data = read_excel(proc_dir / "input_shortages" / "0913.xlsx")
shortage_items = extract_item_names(shortages_data, "أسم الصنف")

# Deduplicate
unique_shortages = {}
for item in shortage_items:
    name = item.get("item_name_raw", "")
    if name and name not in unique_shortages:
        unique_shortages[name] = item
deduped_shortages = list(unique_shortages.values())

wh_files = list((proc_dir / "input_warehouses").glob("*.pdf"))
cache_dir = Path("data/.unstructured_cache")

print(f"Loaded {len(deduped_shortages)} unique shortages and {len(wh_files)} warehouse files.")

total_auto = 0
for wh_file in wh_files:
    file_hash = _get_file_hash(wh_file)
    cache_file = cache_dir / f"{file_hash}_extract.json"
    if not cache_file.exists():
        print(f"Cache missing for {wh_file.name}")
        continue
    with open(cache_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    wh_items = parse_structured_result(data, wh_file.name)
    
    finder = FastCandidateFinder(wh_items)
    
    exact_count = 0
    auto_count = 0
    wh_norm = {normalize_text(item.get("item_name_raw", "")): item.get("item_name_raw", "") for item in wh_items}
    
    auto_samples = []
    for item in deduped_shortages:
        req = item["item_name_raw"]
        norm = normalize_text(req)
        if norm in wh_norm:
            exact_count += 1
        else:
            top_c = finder.search(req, top_k=6)
            if top_c:
                best_name = top_c[0]["name"]
                is_auto, reason = is_safe_auto_match(req, best_name)
                if is_auto:
                    auto_count += 1
                    if len(auto_samples) < 3:
                        auto_samples.append((req, best_name))
                    
    total_auto += (exact_count + auto_count)
    print(f"[{wh_file.name}] ({len(wh_items)} items) -> Exact: {exact_count}, Safe Auto-Match: {auto_count}")
    for r, b in auto_samples:
        print(f"    * '{r}' -> '{b}'")

print(f"\nTotal Deterministic Matches across all warehouses: {total_auto}")
