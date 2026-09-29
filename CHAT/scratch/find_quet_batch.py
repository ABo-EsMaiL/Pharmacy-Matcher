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
            "name": name,
            "cands": cands
        })

print(f"Total llm_cases: {len(llm_cases)}")
for c in llm_cases:
    if "كويتابين" in c["name"]:
        batch_idx = llm_cases.index(c) // 75
        pos_in_batch = llm_cases.index(c) % 75
        print(f"Found case {c['case_id']}: '{c['name']}' in Batch {batch_idx + 1}, position {pos_in_batch}")
        print("Candidates:", c["cands"])
