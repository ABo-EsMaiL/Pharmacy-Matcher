import hashlib
from pathlib import Path

wh_folder = Path(r"D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-004\input_warehouses")
for pdf in wh_folder.glob("*.pdf"):
    h = hashlib.md5(pdf.read_bytes()).hexdigest()
    print(f"{pdf.name} -> {h}")
