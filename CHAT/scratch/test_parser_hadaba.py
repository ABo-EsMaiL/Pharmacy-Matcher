import os
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(r"d:\AI_Engineer\Pharmacy-agy\.env")
api_key = os.getenv("UNSTRUCTURED_API_KEY")

from unstructured_transform_client import TransformClient

c = TransformClient(api_key=api_key, server_url="https://transform.unstructured.io")
j = c.jobs.get("0e0bbc06-828d-4f69-87c7-e92dbd95df73")
data = j.model_dump()

def parse_structured_result_test(result_data: dict, filename: str) -> list[dict]:
    items = []
    if not isinstance(result_data, dict):
        return items

    if "result" in result_data and isinstance(result_data["result"], dict):
        result_data = result_data["result"]

    extracted_data = result_data.get("extracted_data", [])
    if isinstance(extracted_data, list) and len(extracted_data) > 0:
        for block in extracted_data:
            data = block.get("data", {}) if isinstance(block, dict) else getattr(block, "data", {})
            if isinstance(data, dict) and "items" in data:
                for item in data.get("items", []):
                    if not isinstance(item, dict):
                        continue
                    name = item.get("item_name_raw")
                    if name:
                        items.append({
                            "item_name_raw": str(name).strip(),
                            "source_page": item.get("source_page"),
                            "source_file": filename
                        })

    if not items and "markdown" in result_data and result_data["markdown"]:
        md = str(result_data["markdown"])
        rows = re.findall(r"<tr>(.*?)</tr>", md, re.DOTALL | re.IGNORECASE)
        if rows:
            name_col_idx = 1
            header_cells = [re.sub(r"<.*?>", "", c).strip() for c in re.findall(r"<t[dh].*?>(.*?)</t[dh]>", rows[0], re.DOTALL | re.IGNORECASE)]
            for idx, col in enumerate(header_cells):
                col_lower = col.lower()
                if any(k in col_lower for k in ["اسم الصنف", "اسم الدواء", "item name", "product name", "description", "اسم"]):
                    if not any(nk in col_lower for nk in ["رقم", "كود", "code", "id", "number"]):
                        name_col_idx = idx
                        break

            for r in rows[1:]:
                cells = [re.sub(r"<.*?>", "", c).strip() for c in re.findall(r"<t[dh].*?>(.*?)</t[dh]>", r, re.DOTALL | re.IGNORECASE)]
                if len(cells) > name_col_idx:
                    val = cells[name_col_idx]
                    if val and not val.isdigit() and len(val) >= 2 and val not in header_cells:
                        items.append({
                            "item_name_raw": val,
                            "source_page": None,
                            "source_file": filename
                        })

    return items

items = parse_structured_result_test(data, "الهضبة الاثنين نقدى0.pdf")
print("Total items parsed:", len(items))
print("First 5:", [it["item_name_raw"] for it in items[:5]])
print("Last 5:", [it["item_name_raw"] for it in items[-5:]])
