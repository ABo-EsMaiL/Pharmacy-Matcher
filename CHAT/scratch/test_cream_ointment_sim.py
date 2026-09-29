import sys
from pathlib import Path
sys.path.insert(0, str(Path(r'd:\AI_Engineer\Pharmacy-agy')))

from src.extract.excel_reader import read_excel, extract_item_names
from src.extract.pdf_reader import extract_items_from_pdf
from src.fast_match.search import FastCandidateFinder, extract_brand_tokens, extract_form_group

shortages_raw = extract_item_names(read_excel(Path(r'data/processes/PROC-001/input_shortages/0913.xlsx')))
unique_shortages = {}
for s in shortages_raw:
    n = s.get("item_name_raw", "")
    if n and n not in unique_shortages:
        unique_shortages[n] = s
shortage_names = list(unique_shortages.keys())

# Test Makroumi
wh_items = extract_items_from_pdf(Path(r'data/processes/PROC-001/input_warehouses/المكرومي المنصورة.pdf'), api_key="")
wh_catalog = [{"id": f"W-{i:05}", "name": item["item_name_raw"]} for i, item in enumerate(wh_items)]

finder = FastCandidateFinder()
finder.fit(wh_catalog)

# Check Betaderm ointment
b_cands = finder.search("بيتاديرم مرهم س ج")
print("Betaderm ointment candidates in Makroumi:")
for c in b_cands:
    print("  ", c["name"], "score:", c["score"])

# Check Zidamicin ointment / Garamycin
z_cands = finder.search("زادميسن20مجم مرهم/جاراميسين")
print("\nZidamicin candidates in Makroumi:")
for c in z_cands:
    print("  ", c["name"], "score:", c["score"])
