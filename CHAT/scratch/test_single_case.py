import requests
import json
import time

url = "http://127.0.0.1:8001/v1/chat/completions"
headers = {
    "Authorization": "Bearer [REDACTED_CREDENTIAL]",
    "Content-Type": "application/json",
    "X-Batch-Size": "1"
}
body = {
    "model": "gemini-3.8-flash",
    "messages": [
        {"role": "user", "content": "Respond with JSON: {\"message\": \"pong\"}"}
    ],
    "stream": False
}
print("Sending test request...")
t0 = time.time()
try:
    r = requests.post(url, headers=headers, json=body, timeout=60)
    print(f"Status: {r.status_code} in {time.time()-t0:.2f}s")
    print("Response:", r.text[:300])
except Exception as e:
    print(f"Error in {time.time()-t0:.2f}s: {e}")
