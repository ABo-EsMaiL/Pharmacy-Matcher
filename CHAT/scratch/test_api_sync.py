import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"D:\AI_Engineer\Pharmacy-agy")
sys.path.insert(0, str(PROJECT_ROOT))

from desktop_app.backend import API

def test_api():
    api = API()
    hist = json.loads(api.get_history())
    p14 = next(p for p in hist if p['id'] == 'PROC-014')
    print("History PROC-014:", {
        "id": p14["id"],
        "status": p14["status"],
        "matched": p14["matched_count"],
        "not_found": p14["not_found_count"],
        "review": p14["review_count"]
    })

    det = json.loads(api.get_process_details('PROC-014'))
    print("Details PROC-014:", {
        "id": det["id"],
        "status": det["status"],
        "matched": det["matched_count"],
        "not_found": det["not_found_count"],
        "review": det["review_count"]
    })

if __name__ == "__main__":
    test_api()
