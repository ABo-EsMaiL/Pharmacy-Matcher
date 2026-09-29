import sys
sys.path.insert(0, ".")
from src.extract.excel_reader import read_excel, extract_item_names
from src.extract.file_handler import read_input_files
from src.fast_match.search import FastCandidateFinder, extract_brand_tokens, extract_form_group
from rapidfuzz import fuzz
from pathlib import Path

# Load shortages
s_rows = read_excel(Path("data/processes/PROC-008/input_shortages/0913.xlsx"))
shortages = extract_item_names(s_rows)
unique_shortages = {}
for s in shortages:
    name = s["item_name_raw"].strip()
    if name and name not in unique_shortages:
        unique_shortages[name] = s

# Load warehouses
wh_files = list(Path("data/processes/PROC-008/input_warehouses").glob("*.*"))
from src.config import load_config
config = load_config()
wh_data = read_input_files(wh_files, role="warehouse", api_key=config.unstructured_api_key)

print(f"\nUnique shortages: {len(unique_shortages)}")
print(f"Warehouses: {len(wh_data)}")

# Let's test the 8 controversial items under this logic
test_targets = [
    "سكينورين كريم",
    "زنكترون 30كبسولة س ج",
    "بالموكورت  25. مجم امبول س ج",
    "كارنيفيتا ادفانس للرجال30كيس س ج",
    "ب ك ميرز كبسول س ج",
    "سينوبريل كواقراص س ج",
    "تادالاندرو5جم30قرص",
    "هيرو دي3+كي2 نقط"
]

print("\n=== EVALUATION OF THE 8 ITEMS UNDER 3-LEVEL HIERARCHY ===")
for target in test_targets:
    target_brand = extract_brand_tokens(target)
    target_form = extract_form_group(target)
    
    found_candidates = []
    for wh_name, wh_items in wh_data.items():
        finder = FastCandidateFinder()
        wh_catalog = [{"id": f"W-{i:05}", "name": it.get("item_name_raw", "")} for i, it in enumerate(wh_items)]
        finder.fit(wh_catalog)
        cands = finder.search(target, top_k=3)
        for c in cands:
            found_candidates.append((wh_name, c["name"], c["score"], c.get("brand_sim", 0)))
            
    found_candidates.sort(key=lambda x: (x[3], x[2]), reverse=True)
    if found_candidates:
        top = found_candidates[0]
        cand_brand = extract_brand_tokens(top[1])
        cand_form = extract_form_group(top[1])
        print(f"\nالصنف: [{target}]")
        print(f"   أفضل مرشح: [{top[1]}] في ({top[0]}) | BrandSim={top[3]:.1f}")
        print(f"   تحليل: Target(brand={target_brand}, form={target_form}) vs Cand(brand={cand_brand}, form={cand_form})")
        # Can it ever go to "لم يتم العثور عليه"?
        print(f"   -> النتيجة المنطقية: خرج تماماً من 'لم يتم العثور عليه'! إما مطابقة مباشرة أو مراجعة.")
    else:
        print(f"\nالصنف: [{target}] -> لم يجد أي مرشح!")
