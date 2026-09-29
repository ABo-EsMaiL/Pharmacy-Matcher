import requests
import json
import time

url = "http://127.0.0.1:8000/v1/chat/completions"
api_key = "[REDACTED_CREDENTIAL]"

def test_items(count):
    cases = []
    for i in range(count):
        cases.append({
            "case_id": f"Q{i+1:05}",
            "requested_name": f"سيتال 500 مجم اقراص {i+1}",
            "candidates": [
                {"id": f"WH{i+1:05}_1", "name": f"سيتال اقراص 500 مجم باكو {i+1}"},
                {"id": f"WH{i+1:05}_2", "name": f"بارامول 500 مجم اقراص {i+1}"}
            ]
        })
    body = {
        "model": "gpt-4o",
        "messages": [
            {"role": "user", "content": "Return ONLY JSON with results key for matches: " + json.dumps({"cases": cases}, ensure_ascii=False)}
        ]
    }
    payload_kb = len(json.dumps(body, ensure_ascii=False).encode('utf-8')) / 1024
    print(f"\nTesting count={count} (Payload: {payload_kb:.1f} KB)...")
    t0 = time.time()
    try:
        r = requests.post(url, headers={"Authorization": f"Bearer {api_key}"}, json=body, timeout=60)
        elapsed = time.time() - t0
        content = r.json()["choices"][0]["message"]["content"]
        if "[ChatGPT returned" in content:
            print(f"FAILED in {elapsed:.1f}s: {content.strip()}")
            return False
        else:
            print(f"SUCCESS in {elapsed:.1f}s! Response length: {len(content)} chars")
            print("Preview:", repr(content[:150]))
            return True
    except Exception as e:
        print(f"Exception: {e}")
        return False

for c in [80, 100, 120]:
    test_items(c)
    time.sleep(5)
