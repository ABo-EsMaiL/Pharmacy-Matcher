from pathlib import Path
import os
import sys
import time
from dotenv import load_dotenv

sys.path.insert(0, r"d:\AI_Engineer\Pharmacy-agy")
load_dotenv(r"d:\AI_Engineer\Pharmacy-agy\.env")

from src.extract.file_handler import read_input_files
from src.config import load_config

config = load_config()

pdf_dir = Path(r"d:\AI_Engineer\Pharmacy-agy\data\processes\PROC-001\input_warehouses")
test_files = [
    pdf_dir / "السلام شبين.pdf",
    pdf_dir / "المكرومي المنصورة.pdf",
]

print(f"Testing parallel extraction on {len(test_files)} files...")
start = time.time()
res = read_input_files(
    test_files,
    role="warehouse",
    api_key=config.unstructured_api_key,
    base_url=config.unstructured_base_url,
    gemini_api_key=config.gemini_api_key,
    profile="balanced"
)
elapsed = time.time() - start
print(f"Extraction finished in {elapsed:.2f}s")
for k, v in res.items():
    print(f"  {k}: {len(v)} items")
