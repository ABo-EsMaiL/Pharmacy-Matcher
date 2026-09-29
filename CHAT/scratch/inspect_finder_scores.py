import sys
sys.path.insert(0, ".")
from src.fast_match.search import FastCandidateFinder
from src.extract.file_handler import read_input_files
from pathlib import Path

wh_files = list(Path("data/processes/PROC-008/input_warehouses").glob("*.*"))
if not wh_files:
    wh_files = list(Path("data/warehouses").glob("*.*"))

from src.config import load_config
config = load_config()

print(f"Found {len(wh_files)} warehouse files.")
wh_data = read_input_files(wh_files, role="warehouse", api_key=config.unstructured_api_key)

target_items = [
    ("سكينورين كريم", "الهضبة الاثنين نقدى0.pdf"),
    ("زنكترون 30كبسولة س ج", "مخزن الحياة فارم اسكندريه-170.p"),
    ("بالموكورت  25. مجم امبول س ج", "السلام شبين.pdf"),
    ("كارنيفيتا ادفانس للرجال30كيس س ج", "مخزن الحياة فارم اسكندريه-170.p"),
    ("ب ك ميرز كبسول س ج", "الهضبة الاثنين نقدى0.pdf"),
    ("سينوبريل كواقراص س ج", "الهضبة الاثنين نقدى0.pdf"),
    ("تادالاندرو5جم30قرص", "الهضبة الاثنين نقدى0.pdf"),
    ("هيرو دي3+كي2 نقط", "كيور فارما خاص.pdf")
]

for target, target_wh in target_items:
    # Find the warehouse
    matched_wh_key = None
    for k in wh_data.keys():
        if target_wh[:8] in k:
            matched_wh_key = k
            break
            
    if not matched_wh_key:
        print(f"Warehouse {target_wh} not found!")
        continue
        
    items = wh_data[matched_wh_key]
    finder = FastCandidateFinder()
    wh_catalog = [{"id": f"W-{i:05}", "name": item.get("item_name_raw", "")} for i, item in enumerate(items)]
    finder.fit(wh_catalog)
    
    top_candidates = finder.search(target, top_k=5)
    print(f"\n--- Item: [{target}] in [{matched_wh_key}] ---")
    for c in top_candidates[:3]:
        print(f"   Candidate: [{c['name']}] | Score: {c['score']:.3f} | BrandSim: {c.get('brand_sim', 0)}")
