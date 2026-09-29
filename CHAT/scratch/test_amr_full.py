import sys
from pathlib import Path
sys.path.insert(0, str(Path(r'd:\AI_Engineer\Pharmacy-agy')))

import json
import requests as http_requests
from src.extract.excel_reader import read_excel, extract_item_names
from src.extract.pdf_reader import extract_items_from_pdf
from src.fast_match.search import FastCandidateFinder
from src.fast_match.coordinator import SYSTEM_PROMPT

shortages_raw = extract_item_names(read_excel(Path(r'data/processes/PROC-001/input_shortages/0913.xlsx')))
unique_shortages = {}
for s in shortages_raw:
    n = s.get("item_name_raw", "")
    if n and n not in unique_shortages:
        unique_shortages[n] = s

wh_items = extract_items_from_pdf(Path(r'data/processes/PROC-001/input_warehouses/جملة العمروووو.pdf'), api_key="")
wh_catalog = [{"id": f"W-{i:05}", "name": item["item_name_raw"]} for i, item in enumerate(wh_items)]
catalog_by_id = {item["id"]: item["name"] for item in wh_catalog}

finder = FastCandidateFinder()
finder.fit(wh_catalog)

llm_cases = []
for idx, req in enumerate(unique_shortages.keys()):
    cands = finder.search(req, top_k=5)
    if cands:
        llm_cases.append({
            "case_id": f"Q{idx:05}",
            "requested_name": req,
            "candidates": [{"id": c["id"], "name": c["name"]} for c in cands[:3]]
        })

print(f"Total cases for Amr: {len(llm_cases)}")
# Check ampover case
amp_case = [c for c in llm_cases if "امبوفير" in c["requested_name"]]
print("Ampover case:", amp_case)

resp = http_requests.post("http://127.0.0.1:8000/v1/chat/completions",
    headers={"Authorization": "Bearer [REDACTED_CREDENTIAL]"},
    json={
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps({"cases": llm_cases}, ensure_ascii=False)}
        ]
    },
    timeout=120
)

print("Response status:", resp.status_code)
content = resp.json()["choices"][0]["message"]["content"]
print("LLM Content:", content)
