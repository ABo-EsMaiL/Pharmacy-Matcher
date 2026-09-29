import sys
sys.path.insert(0, r"D:\AI_Engineer\Pharmacy-agy")
from src.fast_match.search import FastCandidateFinder
import json
from pathlib import Path
from src.extract.pdf_reader import parse_structured_result

cache_file = Path(r"D:\AI_Engineer\Pharmacy-agy\data\processes\data\.unstructured_cache\a4f524fd75cf223f927a228ad87319f0_extract.json")
data = json.loads(cache_file.read_text(encoding="utf-8"))
items = parse_structured_result(data, "الهضبة الاثنين نقدى0.pdf")

wh_items = [{"id": f"W_{i}", "name": it["item_name_raw"]} for i, it in enumerate(items)]
finder = FastCandidateFinder()
finder.fit(wh_items)

cands = finder.search("كويتابين 25مجم 30قرص س ج", top_k=6)
print("Candidates found for 'كويتابين 25مجم 30قرص س ج':")
for c in cands:
    print(f"  - {c['id']}: '{c['name']}' (Score: {c['score']:.3f}, Brand Sim: {c['brand_sim']})")
