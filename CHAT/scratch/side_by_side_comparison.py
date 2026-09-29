import json
import difflib

with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\gemini_dom_items.json", "r", encoding="utf-8") as f:
    gemini_items = [it["item_name_raw"].strip() for it in json.load(f)]

import sys
from pathlib import Path
sys.path.insert(0, str(Path("D:/AI_Engineer/Pharmacy-agy")))
from src.extract.pdf_reader import _get_file_hash, parse_structured_result

pdf_path = Path(r"D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-015\input_warehouses\المكرومي المنصورة.pdf")
h = _get_file_hash(pdf_path)
cache_file = Path(r"D:\AI_Engineer\Pharmacy-agy\data\processes\data\.unstructured_cache") / f"{h}_extract.json"

with open(cache_file, "r", encoding="utf-8") as f:
    unstruct_raw = json.load(f)

unstruct_items = [it["item_name_raw"].strip() for it in parse_structured_result(unstruct_raw, pdf_path.name) if it.get("source_page") == 1]

print(f"Gemini Page 1 items count: {len(gemini_items)}")
print(f"Unstructured Page 1 items count: {len(unstruct_items)}")

# Match each Gemini item to best Unstructured item
comparisons = []
for g in gemini_items:
    best_u = None
    best_sim = 0
    for u in unstruct_items:
        sim = difflib.SequenceMatcher(None, g, u).ratio()
        if sim > best_sim:
            best_sim = sim
            best_u = u
    comparisons.append({
        "gemini": g,
        "unstructured": best_u,
        "similarity": best_sim
    })

# Sort by lowest similarity to find where Unstructured failed the hardest
comparisons.sort(key=lambda x: x["similarity"])

print("\n--- 25 BIGGEST DIFFERENCES (Where Unstructured corrupted the drug name) ---")
for i, c in enumerate(comparisons[:25], 1):
    print(f"\n{i}. [SIM: {int(c['similarity']*100)}%]")
    print(f"   Gemini:       '{c['gemini']}'")
    print(f"   Unstructured: '{c['unstructured']}'")

# Look at specific pharmaceutical brand errors
with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\page1_detailed_comparison.json", "w", encoding="utf-8") as out:
    json.dump(comparisons, out, ensure_ascii=False, indent=2)
