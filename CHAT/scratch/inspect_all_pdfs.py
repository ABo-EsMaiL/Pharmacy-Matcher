import pypdf
from pathlib import Path

wh_dir = Path(r"d:\AI_Engineer\Pharmacy-agy\data\processes\PROC-001\input_warehouses")
for pdf_file in wh_dir.glob("*.pdf"):
    reader = pypdf.PdfReader(str(pdf_file))
    print(f"{pdf_file.name}: {len(reader.pages)} pages, {pdf_file.stat().st_size / 1024:.1f} KB")
