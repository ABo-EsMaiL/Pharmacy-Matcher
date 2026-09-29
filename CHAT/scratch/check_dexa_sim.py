import sys
sys.path.insert(0, r"D:\AI_Engineer\Pharmacy-agy")
from src.fast_match.search import FastCandidateFinder, normalize_for_search
import json
from pathlib import Path
from src.extract.pdf_reader import parse_structured_result
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

cache_file = Path(r"D:\AI_Engineer\Pharmacy-agy\data\processes\data\.unstructured_cache\ebc3fcf9fdcc6cb525f174254a00f5d5_extract.json")
data = json.loads(cache_file.read_text(encoding="utf-8"))
items = parse_structured_result(data, "السلام شبين.pdf")

wh_items = [{"id": f"W_{i}", "name": it["item_name_raw"]} for i, it in enumerate(items)]
finder = FastCandidateFinder()
finder.fit(wh_items)

q = "ديكساتوبرين مرهم س ج"
q_norm = normalize_for_search(q)
q_vec = finder.vectorizer.transform([q_norm])
sims = cosine_similarity(q_vec, finder.matrix).flatten()

# Find 'ديكسا'
for i, name in enumerate(finder.original_names):
    if "ديكسا" in name or "توبيرين" in name or "توبرين" in name:
        rank = int(np.sum(sims > sims[i])) + 1
        print(f"Item W_{i}: '{name}'")
        print(f"  Norm: '{finder.corpus[i]}'")
        print(f"  Cosine Sim: {sims[i]:.4f} (Rank #{rank} out of {len(items)})")

print("\nTop 10 indices by cosine sim:")
for idx in np.argsort(sims)[-10:][::-1]:
    print(f"  - W_{idx}: '{finder.original_names[idx]}' (Sim: {sims[idx]:.4f})")

cands = finder.search("ديكساتوبرين مرهم س ج", top_k=6)
print("\ncands from finder.search:")
for c in cands:
    print("  -", c)
