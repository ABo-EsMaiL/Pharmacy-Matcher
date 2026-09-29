import pypdf
from pathlib import Path

pdf_path = Path(r"d:\AI_Engineer\Pharmacy-agy\data\processes\PROC-001\input_warehouses\الهضبة الاثنين نقدى0.pdf")
if not pdf_path.exists():
    pdf_path = Path(r"d:\AI_Engineer\Pharmacy\الهضبة الاثنين نقدى0.pdf")

print("File:", pdf_path, "Size:", pdf_path.stat().st_size)

reader = pypdf.PdfReader(str(pdf_path))
print("Total pages:", len(reader.pages))

text_sample = ""
for i, page in enumerate(reader.pages[:5]):
    t = page.extract_text() or ""
    print(f"Page {i+1} text length: {len(t)}")
    if t.strip() and not text_sample:
        text_sample = t[:300]

print("Sample text from page 1:")
print(repr(text_sample))
