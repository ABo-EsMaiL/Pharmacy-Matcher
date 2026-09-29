import os
from pathlib import Path

root = Path(r"D:\AI_Engineer\Pharmacy-agy-vision")
for py_file in root.rglob("*.py"):
    if ".git" in py_file.parts or ".vision_cache" in py_file.parts or "__pycache__" in py_file.parts:
        continue
    try:
        content = py_file.read_text(encoding="utf-8")
        lines = content.splitlines()
        for idx, line in enumerate(lines):
            if "timeout" in line.lower() and ("requests" in line or "post" in line or "get(" in line or "read_timeout" in line or "timeout=" in line):
                print(f"{py_file.relative_to(root)}:{idx+1}: {line.strip()[:100]}")
    except Exception:
        pass
