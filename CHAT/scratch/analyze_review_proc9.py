import sys
sys.path.insert(0, ".")
import openpyxl
from rapidfuzz import fuzz
from src.fast_match.search import extract_brand_tokens

wb = openpyxl.load_workbook('data/processes/PROC-009/results_PROC-009.xlsx', data_only=True)
ws_rev = wb['يحتاج مراجعة']

rows = []
for r in ws_rev.iter_rows(min_row=2, values_only=True):
    # col 1: Decision, 2: Shortage, 3: Warehouse, 4: Wh Name, 5: Reason
    req = str(r[1] or '')
    wh = str(r[2] or '')
    wh_name = str(r[3] or '')
    reason = str(r[4] or '')
    if req and wh:
        rows.append((req, wh, wh_name, reason))

print(f"Total unique shortage-warehouse review pairs in sheet: {len(rows)}")

# Let's inspect the brand similarity distribution of these pairs
b_sims = []
for req, wh, wh_name, reason in rows:
    b_req = extract_brand_tokens(req)
    b_wh = extract_brand_tokens(wh)
    sim = fuzz.ratio(b_req, b_wh)
    b_sims.append((sim, req, wh, wh_name, reason))

b_sims.sort(reverse=True, key=lambda x: x[0])

print("\n--- High Brand Similarity (sim >= 75) [Likely Real Review / Strength difference / OCR error]: ---")
high_sim = [x for x in b_sims if x[0] >= 75]
print(f"Count: {len(high_sim)}")
for sim, req, wh, wh_name, reason in high_sim[:25]:
    print(f"  [{sim}%] '{req}' vs '{wh}' ({wh_name})")

print("\n--- Moderate Brand Similarity (60 <= sim < 75): ---")
mid_sim = [x for x in b_sims if 60 <= x[0] < 75]
print(f"Count: {len(mid_sim)}")
for sim, req, wh, wh_name, reason in mid_sim[:20]:
    print(f"  [{sim}%] '{req}' vs '{wh}' ({wh_name})")

print("\n--- Low Brand Similarity (sim < 60) [Complete False Matches that leaked because of score >= 0.40]: ---")
low_sim = [x for x in b_sims if x[0] < 60]
print(f"Count: {len(low_sim)}")
for sim, req, wh, wh_name, reason in low_sim[:25]:
    print(f"  [{sim}%] '{req}' vs '{wh}' ({wh_name})")
