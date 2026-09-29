import sys
sys.path.insert(0, r"D:\AI_Engineer\Pharmacy-agy")
import json
from pathlib import Path
from src.extract.pdf_reader import parse_structured_result
from src.extract.excel_reader import read_excel, extract_item_names
from src.fast_match.search import FastCandidateFinder

# Load shortages
excel_path = Path(r"D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-004\input_shortages\0913.xlsx")
shortage_rows = read_excel(excel_path)
shortages_raw = extract_item_names(shortage_rows)
unique_shortages = {}
for item in shortages_raw:
    name = item.get("item_name_raw", "")
    if name and name not in unique_shortages:
        unique_shortages[name] = item
deduped_shortages = list(unique_shortages.values())

# Load El Hadaba
cache_file = Path(r"D:\AI_Engineer\Pharmacy-agy\data\processes\data\.unstructured_cache\a4f524fd75cf223f927a228ad87319f0_extract.json")
data = json.loads(cache_file.read_text(encoding="utf-8"))
items = parse_structured_result(data, "الهضبة الاثنين نقدى0.pdf")
wh_items = [{"id": f"W_{i}", "name": it["item_name_raw"]} for i, it in enumerate(items)]

finder = FastCandidateFinder()
finder.fit(wh_items)

llm_cases = []
for idx, s_item in enumerate(deduped_shortages):
    name = s_item["item_name_raw"]
    cands = finder.search(name, top_k=6)
    if cands:
        llm_cases.append({
            "idx": idx,
            "case_id": f"Q{idx:05}",
            "requested_name": name,
            "candidates": [{"id": c["id"], "name": c["name"]} for c in cands[:3]]
        })

batch_size = 75
batch_3 = llm_cases[150:225]
print(f"Batch 3 has {len(batch_3)} cases:")
for i, c in enumerate(batch_3[:15]):
    print(f"[{i+1}] {c['case_id']}: '{c['requested_name']}'")
    print(f"     Top Cand: '{c['candidates'][0]['name']}'\n")
