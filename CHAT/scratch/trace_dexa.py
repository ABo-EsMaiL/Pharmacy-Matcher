import sys
sys.path.insert(0, r"D:\AI_Engineer\Pharmacy-agy")
from src.fast_match.search import FastCandidateFinder
import json
from pathlib import Path
from src.extract.pdf_reader import parse_structured_result

# Load shebin items
cache_file = Path(r"D:\AI_Engineer\Pharmacy-agy\data\processes\data\.unstructured_cache\d0c1443b3b0a6e2287def7b8f4816fc0_extract.json")
data = json.loads(cache_file.read_text(encoding="utf-8"))
items = parse_structured_result(data, "السلام شبين.pdf")

wh_items = [{"id": f"W_{i}", "name": it["item_name_raw"]} for i, it in enumerate(items)]
finder = FastCandidateFinder()
finder.fit(wh_items)

cands = finder.search("ديكساتوبرين مرهم س ج", top_k=6)
print("Candidates found for 'ديكساتوبرين مرهم س ج':")
for c in cands:
    print(f"  - {c['id']}: '{c['name']}' (Score: {c['score']:.3f}, Brand Sim: {c['brand_sim']})")
