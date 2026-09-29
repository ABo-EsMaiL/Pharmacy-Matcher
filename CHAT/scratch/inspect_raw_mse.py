import requests
import json
import re

url = "http://127.0.0.1:8000/v1/chat/completions"
api_key = "[REDACTED_CREDENTIAL]"

body = {
    "model": "gpt-4o",
    "messages": [
        {"role": "user", "content": "Return a JSON: {\"status\": \"ok\"}"}
    ]
}

r = requests.post(url, headers={"Authorization": f"Bearer {api_key}"}, json=body, timeout=30)
print("Status:", r.status_code)
print("Raw response json:")
try:
    data = r.json()
    print("Keys:", data.keys())
    content = data["choices"][0]["message"]["content"]
    print("Content repr:")
    print(repr(content))
    print("Content raw:")
    print(content)
except Exception as e:
    print("Error parsing response:", e)
    print("Response text:", r.text[:500])
