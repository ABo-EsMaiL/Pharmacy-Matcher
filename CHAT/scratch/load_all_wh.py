import sys
sys.path.insert(0, r"D:\AI_Engineer\Pharmacy-agy")
from pathlib import Path
import json
from src.extract.pdf_reader import parse_structured_result

wh_folder = Path(r"D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-004\input_warehouses")
cache_dir = Path(r"D:\AI_Engineer\Pharmacy-agy\data\processes\data\.unstructured_cache")

import hashlib
def get_hash(fp):
    h = hashlib.md5()
    with open(fp, 'rb') as f:
        while b := f.read(65536):
            h.update(b)
    return h.hexdigest()

warehouse_data = {}
total_wh = 0

for pdf in wh_folder.glob("*.pdf"):
    fhash = get_hash(pdf)
    cfile = cache_dir / f"{fhash}_extract.json"
    if cfile.exists():
        with open(cfile, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = parse_structured_result(data, pdf.name)
        warehouse_data[pdf.name] = items
        total_wh += len(items)
        print(f"[+] Loaded {len(items)} items for {pdf.name}")
    else:
        print(f"[-] No cache for {pdf.name}")

print(f"Total warehouse items loaded: {total_wh}")
