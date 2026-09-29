import time
import requests

for i in range(30):
    try:
        r = requests.get("http://127.0.0.1:8001/health", timeout=2)
        if r.status_code == 200:
            data = r.json()
            print("HEALTH:", data)
            if data.get("browser_ready"):
                print("Browser is ready!")
                break
    except Exception as e:
        print(f"Waiting for server... ({e})")
    time.sleep(2)
