import sys
sys.path.insert(0, ".")
import json
from src.config import load_config
from src.fast_match.coordinator import FastCoordinator
from src.extract.excel_reader import read_excel, extract_item_names
from src.extract.pdf_table_reader import read_pdf_table
from pathlib import Path

config = load_config()
coordinator = FastCoordinator(config)

# Check candidate generation for one of the items
shortage_file = Path("data/shortages/0913.xlsx")
s_rows = read_excel(shortage_file)
shortage_items = extract_item_names(s_rows)

wh_dir = Path("data/processes/PROC-008/warehouses") # or data/warehouses
if not wh_dir.exists():
    wh_dir = Path("data/warehouses")

wh_files = list(wh_dir.glob("*.pdf")) + list(wh_dir.glob("*.xlsx"))
warehouse_data = {}
for wf in wh_files:
    if wf.suffix.lower() == ".pdf":
        warehouse_data[wf.name] = read_pdf_table(wf)
    else:
        warehouse_data[wf.name] = extract_item_names(read_excel(wf))

print("Total shortage items:", len(shortage_items))
print("Warehouses loaded:", list(warehouse_data.keys()))

target_items = [
    "سكينورين كريم",
    "زنكترون 30كبسولة س ج",
    "بالموكورت  25. مجم امبول س ج",
    "كارنيفيتا ادفانس للرجال30كيس س ج",
    "ب ك ميرز كبسول س ج",
    "سينوبريل كواقراص س ج",
    "تادالاندرو5جم30قرص",
    "هيرو دي3+كي2 نقط"
]

# Let's inspect the candidate extraction logic from coordinator
# In coordinator:
unique_shortages = {}
for item in shortage_items:
    name = item["item_name_raw"].strip()
    if name and name not in unique_shortages:
        unique_shortages[name] = item

print("\n=== CANDIDATES IN PIPELINE FOR TARGET ITEMS ===")
from rapidfuzz import fuzz
from src.normalize.cleaner import normalize_for_matching

for wh_name, wh_items in warehouse_data.items():
    wh_clean = [
        {"raw": it["item_name_raw"], "clean": normalize_for_matching(it["item_name_raw"])}
        for it in wh_items
    ]
    for target in target_items:
        t_clean = normalize_for_matching(target)
        matches = []
        for w in wh_clean:
            score = fuzz.token_set_ratio(t_clean, w["clean"])
            if score >= 70:
                matches.append((w["raw"], score))
        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            print(f"[{target}] in [{wh_name}]: top candidate = {matches[0]}")
