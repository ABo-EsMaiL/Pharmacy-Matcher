import sys
import json
import requests as http_requests
from pathlib import Path
sys.path.insert(0, str(Path(r'd:\AI_Engineer\Pharmacy-agy')))
from src.fast_match.coordinator import SYSTEM_PROMPT

cases = [{
    "case_id": "Q001",
    "requested_name": "امبوفير 5امبول س ج",
    "candidates": [{"id": "W-0001", "name": "امبوفير حقن جديد"}]
}]

resp = http_requests.post("http://127.0.0.1:8000/v1/chat/completions",
    headers={"Authorization": "Bearer [REDACTED_CREDENTIAL]"},
    json={
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps({"cases": cases}, ensure_ascii=False)}
        ]
    }
)

print("Status:", resp.status_code)
print("Response:", resp.json()["choices"][0]["message"]["content"])
