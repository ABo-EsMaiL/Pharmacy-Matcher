import sys
from pathlib import Path
sys.path.insert(0, str(Path(r'd:\AI_Engineer\Pharmacy-agy')))

from src.extract.pdf_reader import extract_items_from_pdf
from src.fast_match.search import FastCandidateFinder, extract_brand_tokens, extract_form_group
from rapidfuzz import fuzz

wh_items = extract_items_from_pdf(Path(r'data/processes/PROC-001/input_warehouses/جملة العمروووو.pdf'), api_key="")
print(f"Amr items ({len(wh_items)}):")
for item in wh_items:
    print("  ", item["item_name_raw"])

req = "امبوفير 5امبول س ج"
req_b = extract_brand_tokens(req)
req_f = extract_form_group(req)
print(f"\nReq: '{req}' | Brand: '{req_b}' | Form: '{req_f}'")

for item in wh_items:
    cand = item["item_name_raw"]
    cand_b = extract_brand_tokens(cand)
    cand_f = extract_form_group(cand)
    sim = fuzz.ratio(req_b, cand_b)
    print(f"Cand: '{cand}' | Brand: '{cand_b}' | Form: '{cand_f}' | Sim: {sim}% | Form match: {req_f == cand_f}")
