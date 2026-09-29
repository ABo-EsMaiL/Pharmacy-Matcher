import pypdf
from pathlib import Path

pdf_path = Path(r"d:\AI_Engineer\Pharmacy-agy\data\processes\PROC-001\input_warehouses\جملة العمروووو.pdf")
reader = pypdf.PdfReader(str(pdf_path))
print(f"Total pages: {len(reader.pages)}")
for idx, page in enumerate(reader.pages):
    print(f"--- PAGE {idx+1} ---")
    lines = page.extract_text().split("\n")
    for l in lines:
        if l.strip():
            print("LINE:", l.strip())
