import requests
import json
import time

print("Testing GAIStudio Health...")
try:
    r = requests.get("http://127.0.0.1:8001/health", timeout=5)
    print("Health Status:", r.status_code)
    print("Health JSON:", r.json())
except Exception as e:
    print("Health Error:", e)

print("\nTesting GAIStudio Chat Completions with sample ping...")
payload = {
    "model": "gemini-3.8-flash",
    "messages": [
        {"role": "user", "content": "Reply with only the word: PONG"}
    ],
    "stream": False
}
api_key = "[REDACTED_CREDENTIAL]"

try:
    t0 = time.time()
    r = requests.post(
        "http://127.0.0.1:8001/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json=payload,
        timeout=30
    )
    dt = time.time() - t0
    print(f"Chat Status: {r.status_code} in {dt:.2f}s")
    print("Response:", r.text[:300])
except Exception as e:
    print("Chat Error:", e)
