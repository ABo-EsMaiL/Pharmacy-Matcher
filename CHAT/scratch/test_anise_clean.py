import sys
from pathlib import Path
sys.path.insert(0, str(Path(r'd:\AI_Engineer\Pharmacy-agy')))

import json
import requests as http_requests
from src.fast_match.coordinator import SYSTEM_PROMPT

cases = [{'case_id': 'Q1', 'requested_name': 'ينسون ايزيس س ج', 'candidates': [{'id': 'W1', 'name': 'زيس ينسون 12 فلتر صغير ج/باكو 6'}]}]
resp = http_requests.post('http://127.0.0.1:8000/v1/chat/completions',
    headers={'Authorization': 'Bearer [REDACTED_CREDENTIAL]'},
    json={'model': 'gpt-4o', 'messages': [{'role': 'system', 'content': SYSTEM_PROMPT}, {'role': 'user', 'content': json.dumps({'cases': cases}, ensure_ascii=False)}]},
    timeout=60
)
print(resp.json()['choices'][0]['message']['content'])
