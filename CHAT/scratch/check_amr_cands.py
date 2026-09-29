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

wh_items = extract_items_from_pdf(Path(r'data/processes/PROC-001/input_warehouses/جملة العمروووو.pdf'), api_key="")
wh_catalog = [{"id": f"W-{i:05}", "name": item["item_name_raw"]} for i, item in enumerate(wh_items)]

finder = FastCandidateFinder()
finder.fit(wh_catalog)

ampover_sent = False
for req in unique_shortages.keys():
    cands = finder.search(req, top_k=5)
    if "امبوفير" in req:
        print(f"Req '{req}': cands = {cands}")
        if cands:
            ampover_sent = True

print("Was Ampover sent to LLM?", ampover_sent)
