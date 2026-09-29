import os
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(r"d:\AI_Engineer\Pharmacy-agy\.env")
api_key = os.getenv("UNSTRUCTURED_API_KEY")

from unstructured_transform_client import TransformClient

c = TransformClient(api_key=api_key, server_url="https://transform.unstructured.io")
j = c.jobs.get("0e0bbc06-828d-4f69-87c7-e92dbd95df73")
md = j.result.markdown
print(f"Markdown length: {len(md)} characters")

# Extract table rows
rows = re.findall(r"<tr>(.*?)</tr>", md, re.DOTALL)
print(f"Total rows found: {len(rows)}")

items = []
name_col_idx = 1 # default

for i, r in enumerate(rows):
    cells = [re.sub(r"<.*?>", "", c).strip() for c in re.findall(r"<t[dh].*?>(.*?)</t[dh]>", r, re.DOTALL)]
    if i == 0:
        print("Header cells:", cells)
        for idx, col in enumerate(cells):
            if any(k in col for k in ["اسم", "صنف", "name", "item", "description"]):
                name_col_idx = idx
                break
        print(f"Name column index detected: {name_col_idx}")
    else:
        if len(cells) > name_col_idx:
            item_name = cells[name_col_idx]
            if item_name and not item_name.isdigit() and len(item_name) > 2:
                items.append(item_name)

print(f"Extracted {len(items)} items from Markdown table!")
print("Sample items:")
for it in items[:10]:
    print(" -", it)
