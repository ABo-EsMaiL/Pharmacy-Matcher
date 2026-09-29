import openpyxl
import json
from pathlib import Path
from rapidfuzz import fuzz
import sys
sys.path.insert(0, r"D:\AI_Engineer\Pharmacy-agy")
from src.extract.pdf_reader import parse_structured_result
from src.fast_match.coordinator import extract_brand_tokens

cache_dir = Path(r"D:\AI_Engineer\Pharmacy-agy\data\processes\data\.unstructured_cache")

wh_files = {
    "السلام شبين": "ebc3fcf9fdcc6cb525f174254a00f5d5_extract.json",
    "المكرومي المنصورة": "74a49179bf3b521749a23af2e245c686_extract.json",
    "الهضبة الاثنين": "e73a8ca2ebcd549dffb5c91934ada9be_extract.json",
    "جملة العمروووو": "b05e9145cb816a75e8b2d6ff44abeca4_extract.json",
    "كيور فارما خاص": "a4f524fd75cf223f927a228ad87319f0_extract.json",
    "مخزن الحياة فارم": "d0c1443b3b0a6e2287def7b8f4816fc0_extract.json",
}

warehouse_catalogs = {}
for wh_name, filename in wh_files.items():
    filepath = cache_dir / filename
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = parse_structured_result(data, wh_name)
        warehouse_catalogs[wh_name] = items
        print(f"Loaded {len(items)} items for {wh_name}")

wb6 = openpyxl.load_workbook(r'D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-006\results_PROC-006.xlsx', data_only=True)
ws_nf = wb6['لم يُعثر عليه']
not_found_names = [row[0] for row in ws_nf.iter_rows(min_row=2, values_only=True) if row[0]]

potential = []
for nf in not_found_names:
    b_nf = extract_brand_tokens(nf)
    if not b_nf or len(b_nf) < 3:
        continue
    for wh_name, items in warehouse_catalogs.items():
        for item in items:
            name = item.get("item_name_raw", "")
            b_wh = extract_brand_tokens(name)
            if not b_wh or len(b_wh) < 3:
                continue
            r = fuzz.ratio(b_nf, b_wh)
            if r >= 78:
                potential.append({
                    "shortage": nf,
                    "b_nf": b_nf,
                    "warehouse": wh_name,
                    "wh_item": name,
                    "b_wh": b_wh,
                    "score": r
                })

print(f"\nPotential brand matches (score >= 78%): {len(potential)}")
seen = set()
for m in sorted(potential, key=lambda x: x["score"], reverse=True):
    key = (m["shortage"], m["wh_item"])
    if key not in seen:
        seen.add(key)
        print(f"[{m['score']}%] Shortage: '{m['shortage']}' <==> WH ({m['warehouse']}): '{m['wh_item']}'")
