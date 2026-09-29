import sys
sys.path.insert(0, 'd:/AI_Engineer/Pharmacy-agy')
from src.config import load_config
from src.extract.excel_reader import read_excel, extract_item_names
from src.extract.pdf_reader import extract_items_from_pdf
from src.fast_match.search import FastCandidateFinder
from pathlib import Path

config = load_config()

# Read shortages
shortages_raw = read_excel(Path('data/processes/PROC-002/input_shortages/0913.xlsx'))
shortages = extract_item_names(shortages_raw, 'أسم الصنف')

# Deduplicate
unique_shortages = {}
for item in shortages:
    name = item.get("item_name_raw", "")
    if name and name not in unique_shortages:
        unique_shortages[name] = item
deduped_shortages = list(unique_shortages.values())

# Read Amro
amro_path = Path('data/processes/PROC-002/input_warehouses/جملة العمروووو.pdf')
amro_items = extract_items_from_pdf(amro_path, config.unstructured_api_key)

print(f"Amro total items: {len(amro_items)}")
for i, it in enumerate(amro_items, 1):
    print(f"  {i}. {it['item_name_raw']}")

# Finder
finder = FastCandidateFinder(amro_items)
candidates_by_shortage, auto_matches = finder.find_candidates_for_batch(deduped_shortages, top_k=5)

print(f"\nAuto matches in Amro: {len(auto_matches)}")
print(f"Items with candidates in Amro: {len(candidates_by_shortage)}")

for req_name, cands in candidates_by_shortage.items():
    if 'امبوفير' in req_name or 'بانثينول' in req_name or 'افيرو' in req_name:
        print(f"\nShortage: '{req_name}'")
        for c in cands:
            print(f"  -> Candidate: '{c['item_name_raw']}' (score: {c['score']:.2f})")
