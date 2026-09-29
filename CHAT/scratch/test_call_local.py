import sys
import json
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, r"d:\AI_Engineer\Pharmacy-agy")
load_dotenv(r"d:\AI_Engineer\Pharmacy-agy\.env")

from src.fast_match.coordinator import FastCoordinator, SYSTEM_PROMPT
from src.config import load_config

config = load_config()
coord = FastCoordinator(config)

sample_inputs = {
    "cases": [
        {
            "case_id": "Q00001",
            "requested_name": "فولتارين 75 حقن",
            "candidates": [
                {"id": "WH0001", "name": "فولتارين 75 مجم 3 امبول"},
                {"id": "WH0002", "name": "كيتولاك 30 مجم حقن"}
            ]
        },
        {
            "case_id": "Q00002",
            "requested_name": "بنادول ازرق",
            "candidates": [
                {"id": "WH0003", "name": "بانادول ادفانس 24 قرص"},
                {"id": "WH0004", "name": "بانادول اكسترا 24 قرص"}
            ]
        }
    ]
}

print("Testing _call_local_api directly...")
try:
    res = coord._call_local_api(sample_inputs)
    print("Success! Result:")
    print(json.dumps(res, ensure_ascii=False, indent=2))
except Exception as e:
    import traceback
    print("Failed with error:", e)
    traceback.print_exc()
