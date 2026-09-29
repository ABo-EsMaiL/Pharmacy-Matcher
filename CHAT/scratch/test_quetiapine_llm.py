import sys
sys.path.insert(0, r"D:\AI_Engineer\Pharmacy-agy")
import requests
import json
from src.config import load_config
from src.fast_match.coordinator import SYSTEM_PROMPT

config = load_config()

inputs = {
    "cases": [
        {
            "case_id": "Q001",
            "requested_name": "كويتابين 25مجم 30قرص س ج",
            "candidates": [{"id": "W_855", "name": "کوتیاپین 25 مج اقراص"}]
        },
        {
            "case_id": "Q002",
            "requested_name": "ديكساتوبرين مرهم س ج",
            "candidates": [{"id": "W_80", "name": "ديكسا توبيرين مرهم/ايكو"}]
        },
        {
            "case_id": "Q003",
            "requested_name": "فايركتا 3 شريط س ج",
            "candidates": [{"id": "W_500", "name": "فایرکلا 12 قرص/باکت 72"}]
        }
    ]
}

url = getattr(config, 'local_api_url', "http://127.0.0.1:8000/v1/chat/completions")
api_key = getattr(config, 'local_api_key', '[REDACTED_CREDENTIAL]')

body = {
    "model": "gpt-4o",
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(inputs, ensure_ascii=False)}
    ]
}

resp = requests.post(
    url,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json=body,
    timeout=60
)
print("Response status:", resp.status_code)
content = resp.json()["choices"][0]["message"]["content"]
print("Content:\n", content)
