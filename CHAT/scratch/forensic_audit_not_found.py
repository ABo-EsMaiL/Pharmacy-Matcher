import openpyxl
import os
import glob
from rapidfuzz import fuzz

P14_PATH = r"D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-014\results_PROC-014.xlsx"
WH_DIR = r"D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-014\input_warehouses"

# Also load from cache in dist_production or temp
import pickle

def load_all_warehouses():
    # Load warehouse items from the cache or PDF readers
    # Let's inspect data/processes/PROC-014/input_warehouses
    wh_files = glob.glob(os.path.join(WH_DIR, "*.pdf"))
    print("Warehouse PDF files:", [os.path.basename(f) for f in wh_files])
    
    # We can read all warehouse items from the coordinator cache or from the results sheets
    wb = openpyxl.load_workbook(P14_PATH, data_only=True)
    wh_sheets = [s for s in wb.sheetnames if s not in ['ملخص', 'لم يُعثر عليه', 'يحتاج مراجعة']]
    
    return wb

def main():
    wb = openpyxl.load_workbook(P14_PATH, data_only=True)
    ws_nf = wb['لم يُعثر عليه']
    nf_rows = list(ws_nf.iter_rows(values_only=True))
    headers = nf_rows[0]
    nf_items = [str(r[0]).strip() for r in nf_rows[1:] if r and r[0]]
    
    print(f"Total Not Found items in PROC-014: {len(nf_items)}")
    
    # Let's find warehouse items from all cached pickle or by inspecting coordinator
    # Let's load warehouse catalogs
    import sys
    sys.path.insert(0, r"D:\AI_Engineer\Pharmacy-agy")
    from src.extract.file_handler import read_input_files
    from src.match.text_match import normalize_text
    
    # Load settings
    import json
    settings_path = r"D:\AI_Engineer\Pharmacy-agy\data\settings.json"
    with open(settings_path, "r", encoding="utf-8") as f:
        settings = json.load(f)
    api_key = settings.get("unstructured_api_key")
    
    wh_dir = r"D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-014\input_warehouses"
    wh_files = [os.path.join(wh_dir, f) for f in os.listdir(wh_dir) if f.endswith('.pdf')]
    
    wh_data = read_input_files(wh_files, role='warehouse', api_key=api_key)
    print("Loaded warehouse catalogs:")
    total_wh_items = 0
    all_wh_by_file = {}
    for fname, items in wh_data.items():
        base = os.path.basename(fname)
        clean_items = [it.get("item_name_raw", "").strip() for it in items if it.get("item_name_raw")]
        all_wh_by_file[base] = clean_items
        total_wh_items += len(clean_items)
        print(f"  - {base}: {len(clean_items)} items")
    print(f"Total warehouse items: {total_wh_items}")
    
    # Now, for each item in Not Found, search for the best candidate in each warehouse!
    print("\n" + "=" * 80)
    print("DEEP SCAN: CHECKING NOT-FOUND ITEMS FOR MISSED MATCHES")
    print("=" * 80)
    
    suspicious_misses = []
    
    for shortage in nf_items:
        norm_s = normalize_text(shortage)
        best_cand = None
        best_score = 0
        best_wh = None
        
        for wh_name, items in all_wh_by_file.items():
            for item in items:
                norm_i = normalize_text(item)
                score = max(
                    fuzz.ratio(norm_s, norm_i),
                    fuzz.token_sort_ratio(norm_s, norm_i),
                    fuzz.token_set_ratio(norm_s, norm_i)
                )
                if score > best_score:
                    best_score = score
                    best_cand = item
                    best_wh = wh_name
                    
        # If score is very high (>= 75), it's highly suspicious that it might be a true match or review!
        if best_score >= 70:
            suspicious_misses.append({
                "shortage": shortage,
                "wh_name": best_wh,
                "wh_item": best_cand,
                "score": best_score
            })
            
    print(f"Found {len(suspicious_misses)} suspicious candidates with score >= 70% in Not Found items:")
    # Sort by score descending
    suspicious_misses.sort(key=lambda x: x["score"], reverse=True)
    for idx, m in enumerate(suspicious_misses, 1):
        print(f"{idx:02d}. Score: {m['score']:.1f}% | WH: [{m['wh_name']}]")
        print(f"    Shortage: '{m['shortage']}'")
        print(f"    WH Item:  '{m['wh_item']}'\n")

if __name__ == "__main__":
    main()
