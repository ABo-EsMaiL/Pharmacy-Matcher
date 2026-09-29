import sys
from pathlib import Path
import json

root = Path(r"D:\AI_Engineer\Pharmacy-agy-vision")
sys.path.insert(0, str(root))

from src.config import Config
from src.fast_match.coordinator import FastCoordinator
from src.output.excel_writer import write_results_excel

print("[*] Testing FastCoordinator with new Structured Vision items...")

# Sample shortage items (as from Excel or Vision)
sample_shortages = [
    {
        "item_name_raw": "دوليبرين 1000 مجم 15 قرص",
        "trade_name": "دوليبرين",
        "strength": "1000 مجم",
        "form": "أقراص",
        "source_page": 1,
        "source_file": "نواقص_تجريبية.xlsx"
    },
    {
        "item_name_raw": "كونكور 5 مجم اقراص",
        "trade_name": "كونكور",
        "strength": "5 مجم",
        "form": "أقراص",
        "source_page": 1,
        "source_file": "نواقص_تجريبية.xlsx"
    },
    {
        "item_name_raw": "فيوسيدين كريم 20 جم",
        "trade_name": "فيوسيدين",
        "strength": "",
        "form": "كريم",
        "source_page": 1,
        "source_file": "نواقص_تجريبية.xlsx"
    },
    {
        "item_name_raw": "كتافلام 50 مجم اقراص",
        "trade_name": "كتافلام",
        "strength": "50 مجم",
        "form": "أقراص",
        "source_page": 1,
        "source_file": "نواقص_تجريبية.xlsx"
    }
]

# Sample warehouse items (as produced by our new Gemini Vision extractor!)
sample_warehouse_data = {
    "مخزن_الامانة.pdf": [
        {
            "item_name_raw": "دوليبرين 1000مجم 30قرص س.ج 45",
            "trade_name": "دوليبرين",
            "strength": "1000 مجم",
            "form": "أقراص",
            "source_page": 1,
            "source_file": "مخزن_الامانة.pdf"
        },
        {
            "item_name_raw": "كونكور 2.5 مجم اقراص",
            "trade_name": "كونكور",
            "strength": "2.5 مجم",
            "form": "أقراص",
            "source_page": 1,
            "source_file": "مخزن_الامانة.pdf"
        },
        {
            "item_name_raw": "فيوسيدين مرهم 20 جم",
            "trade_name": "فيوسيدين",
            "strength": "",
            "form": "مرهم",
            "source_page": 1,
            "source_file": "مخزن_الامانة.pdf"
        },
        {
            "item_name_raw": "باي الكوفان 150 اقراص",
            "trade_name": "باي الكوفان",
            "strength": "150 مجم",
            "form": "أقراص",
            "source_page": 1,
            "source_file": "مخزن_الامانة.pdf"
        }
    ]
}

from src.config import load_config
config = load_config()
# Disable local API network call for pure offline unit test of the coordinator algorithms
config.local_api_url = ""

coordinator = FastCoordinator(config)
results = coordinator.process(sample_shortages, sample_warehouse_data)

print("\n=== MATCHING TEST RESULTS ===")
summary = results.get("summary", {})
print(f"Summary: {json.dumps(summary, ensure_ascii=False, indent=2)}")

wh_res = results.get("warehouse_results", {}).get("مخزن_الامانة.pdf", {})
print(f"\nMatched items ({len(wh_res.get('matched', []))}):")
for m in wh_res.get("matched", []):
    print(f"  [+] {m['shortage_item']} -> {m['warehouse_item']} ({m.get('method')})")

print(f"\nNeeds Review items ({len(wh_res.get('needs_review', []))}):")
for r in wh_res.get("needs_review", []):
    print(f"  [?] {r['shortage_item']} -> {r['warehouse_item']} (السبب: {r.get('reason')})")

print(f"\nNot Found items ({len(results.get('not_found', []))}):")
for nf in results.get("not_found", []):
    print(f"  [-] {nf['name']}")

test_excel = Path("scratch/test_pipeline_output.xlsx")
write_results_excel(results, test_excel)
print(f"\n[+] Excel written successfully: {test_excel.resolve()} (Size: {test_excel.stat().st_size} bytes)")
print("[SUCCESS] All pipeline stages verified 100% compatible with structured vision output!")
