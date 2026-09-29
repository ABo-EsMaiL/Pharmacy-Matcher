import sys
from pathlib import Path
sys.path.insert(0, str(Path(r'd:\AI_Engineer\Pharmacy-agy')))

from src.extract.excel_reader import read_excel, extract_item_names
from src.extract.pdf_reader import extract_items_from_pdf
from src.fast_match.search import FastCandidateFinder

shortages_raw = extract_item_names(read_excel(Path(r'data/processes/PROC-001/input_shortages/0913.xlsx')))
unique_shortages = {}
for s in shortages_raw:
    n = s.get("item_name_raw", "")
    if n and n not in unique_shortages:
        unique_shortages[n] = s
shortage_names = list(unique_shortages.keys())

wh_items = extract_items_from_pdf(Path(r'data/processes/PROC-001/input_warehouses/السلام شبين.pdf'), api_key="")
wh_input = [{"id": f"wh_{i}", "name": item["item_name_raw"]} for i, item in enumerate(wh_items)]

finder = FastCandidateFinder()
finder.fit(wh_input)

print(f"Total unique shortages: {len(shortage_names)}")
print(f"Warehouse items: {len(wh_items)}")

for threshold in [0.10, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]:
    count = 0
    for name in shortage_names:
        cands = finder.search(name, top_k=5)
        filtered = [c for c in cands if c["score"] >= threshold]
        if filtered:
            count += 1
    print(f"Threshold {threshold:.2f}: {count} shortage items have candidates")
