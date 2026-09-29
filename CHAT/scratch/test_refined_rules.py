import sys
sys.path.insert(0, 'd:/AI_Engineer/Pharmacy-agy')
from src.config import load_config
from src.fast_match.coordinator import FastCoordinator
import json

config = load_config()
coord = FastCoordinator(config)

test_cases = [
    {
        "case_id": "T1",
        "requested_name": "لاكتيز 15 ملل نقط 750مجم",
        "candidates": [{"item_id": "C1", "name": "لاكتيز نقط بالفم ٥ مل ١٩٠"}]
    },
    {
        "case_id": "T2",
        "requested_name": "كويتابين 25مجم 30قرص س ج",
        "candidates": [{"item_id": "C2", "name": "کوتیاپین اقراص"}]
    },
    {
        "case_id": "T3",
        "requested_name": "نانازوكسيد500مجم18قرص س ج",
        "candidates": [{"item_id": "C3", "name": "نازروکسید اقراص"}]
    },
    {
        "case_id": "T4",
        "requested_name": "امبوفير 5امبول س ج",
        "candidates": [{"item_id": "C4", "name": "امبوفير حقن جديد"}]
    },
    {
        "case_id": "T5",
        "requested_name": "افيروكوكسيب90مجم20قرص س ج",
        "candidates": [{"item_id": "C5", "name": "افيرو كوكسبيب 90مجم-32ب"}]
    }
]

batch_res = coord._call_local_api({"cases": test_cases})
print("TEST RESULTS:")
print(json.dumps(batch_res, ensure_ascii=False, indent=2))
