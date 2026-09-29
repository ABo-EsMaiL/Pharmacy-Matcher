import sys
sys.path.insert(0, ".")
import openpyxl
from rapidfuzz import fuzz
from src.fast_match.search import extract_brand_tokens

wb = openpyxl.load_workbook('data/processes/PROC-009/results_PROC-009.xlsx', data_only=True)
ws_rev = wb['يحتاج مراجعة']

rows = []
for r in ws_rev.iter_rows(min_row=2, values_only=True):
    req = str(r[1] or '').strip()
    wh = str(r[2] or '').strip()
    wh_name = str(r[3] or '').strip()
    reason = str(r[4] or '').strip()
    if req and wh:
        rows.append((req, wh, wh_name, reason))

print(f"Total review pairs in PROC-009: {len(rows)}")

# If we filter by brand similarity
for threshold in [85, 80, 75, 70]:
    kept = []
    dropped = []
    for req, wh, wh_name, reason in rows:
        b_r = extract_brand_tokens(req)
        b_w = extract_brand_tokens(wh)
        sim = max(
            fuzz.ratio(b_r, b_w),
            fuzz.token_sort_ratio(b_r, b_w),
            fuzz.ratio(b_r.replace(' ', ''), b_w.replace(' ', ''))
        )
        # Check first token similarity
        w_r = b_r.split()
        w_w = b_w.split()
        if w_r and w_w and (w_r[0] == w_w[0] or fuzz.ratio(w_r[0], w_w[0]) >= 85):
            sim = max(sim, 85)
            
        if sim >= threshold:
            kept.append((sim, req, wh, wh_name))
        else:
            dropped.append((sim, req, wh, wh_name))
            
    print(f"\n--- Threshold >= {threshold}% ---")
    print(f"Kept in Review: {len(kept)}")
    print(f"Filtered out (Not Found in this WH): {len(dropped)}")
    print("Sample kept:")
    for sim, req, wh, wh_name in kept[:5]:
        print(f"  [{sim}%] {req} vs {wh} ({wh_name})")
