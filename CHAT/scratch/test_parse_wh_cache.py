import sys
from pathlib import Path
sys.path.insert(0, str(Path("D:/AI_Engineer/Pharmacy-agy")))
import json
from src.extract.pdf_reader import _get_file_hash, parse_structured_result

wh_dir = Path("data/processes/PROC-015/input_warehouses")
cache_dir = Path("data/processes/data/.unstructured_cache")

for pdf in wh_dir.glob("*.pdf"):
    h = _get_file_hash(pdf)
    cfile = cache_dir / f"{h}_extract.json"
    if cfile.exists():
        with open(cfile, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = parse_structured_result(data, pdf.name)
        print(f"{pdf.name}: {len(items)} items parsed from cache.")
    else:
        print(f"{pdf.name}: cache NOT found (hash: {h})")
