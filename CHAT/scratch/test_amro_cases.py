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

unique_shortages = {}
for item in shortages:
    name = item.get("item_name_raw", "")
    if name and name not in unique_shortages:
        unique_shortages[name] = item
deduped_shortages = list(unique_shortages.values())

amro_path = Path('data/processes/PROC-002/input_warehouses/جملة العمروووو.pdf')
amro_items = extract_items_from_pdf(amro_path, config.unstructured_api_key)

finder = FastCandidateFinder()
wh_catalog = [{"id": f"W-{i:05}", "name": item.get("item_name_raw", "")} for i, item in enumerate(amro_items)]
finder.fit(wh_catalog)

print("=== ALL AMRO CANDIDATES FOR KEY SHORTAGES ===")
for item in deduped_shortages:
    name = item.get("item_name_raw", "")
    cands = finder.search(name, top_k=3)
    if not cands:
        continue
    best = cands[0]
    if any(k in name for k in ['امبوفير', 'بانثينول', 'افيرو', 'ايزوتريتينوين', 'بانادول']):
        print(f"Shortage: '{name}'")
        for c in cands:
            print(f"  -> Cand: '{c['name']}' (score: {c['score']:.2f}, brand_sim: {c.get('brand_sim', 0):.2f})")
