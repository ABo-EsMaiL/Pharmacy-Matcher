import sys
from pathlib import Path
sys.path.insert(0, str(Path("D:/AI_Engineer/Pharmacy-agy")))
import json
from src.extract.pdf_reader import _get_file_hash, parse_structured_result

pdf_path = Path(r"D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-015\input_warehouses\المكرومي المنصورة.pdf")
h = _get_file_hash(pdf_path)
cache_file = Path(r"D:\AI_Engineer\Pharmacy-agy\data\processes\data\.unstructured_cache") / f"{h}_extract.json"

with open(cache_file, "r", encoding="utf-8") as f:
    unstruct_raw = json.load(f)

unstruct_items = parse_structured_result(unstruct_raw, pdf_path.name)
print(f"Unstructured Total Items for {pdf_path.name}: {len(unstruct_items)}")

# Check page distribution in Unstructured
unstruct_by_page = {}
for it in unstruct_items:
    p = it.get("source_page", 1)
    unstruct_by_page[p] = unstruct_by_page.get(p, 0) + 1

print("Unstructured items by page:", unstruct_by_page)

# Load Gemini Page 1 items
with open(r"C:\Users\kakak\.gemini\antigravity\brain\916274de-7f92-49fc-a0a8-d291664b474a\scratch\gemini_dom_items.json", "r", encoding="utf-8") as f:
    gemini_items = json.load(f)

print(f"Gemini Page 1 Items Extracted: {len(gemini_items)}")
print("\nFirst 10 Gemini Page 1 items:")
for it in gemini_items[:10]:
    print(" ", it.get("item_name_raw"))

print("\nLast 10 Gemini Page 1 items:")
for it in gemini_items[-10:]:
    print(" ", it.get("item_name_raw"))

# Unstructured Page 1 items
unstruct_p1 = [it for it in unstruct_items if it.get("source_page") == 1]
print(f"\nUnstructured Page 1 Items count: {len(unstruct_p1)}")
print("\nFirst 10 Unstructured Page 1 items:")
for it in unstruct_p1[:10]:
    print(" ", it.get("item_name_raw"))

print("\nLast 10 Unstructured Page 1 items:")
for it in unstruct_p1[-10:]:
    print(" ", it.get("item_name_raw"))
