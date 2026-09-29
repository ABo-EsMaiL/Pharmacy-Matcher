import sys
sys.path.insert(0, ".")
import openpyxl

wb_old = openpyxl.load_workbook('data/processes/PROC-009/results_PROC-009.xlsx')
wb_new = openpyxl.load_workbook('data/processes/PROC-011/results_PROC-011.xlsx')

ws_rev_old = wb_old['يحتاج مراجعة']
old_rows = list(ws_rev_old.rows)[1:]

# Load new matches
new_matches = {}
for s in wb_new.sheetnames:
    if s in ['ملخص', 'لم يُعثر عليه', 'يحتاج مراجعة']:
        continue
    for r in list(wb_new[s].rows)[1:]:
        req = str(r[0].value or '').strip()
        wh = str(r[1].value or '').strip()
        if req:
            new_matches[req] = (wh, s)

# Load new review
new_reviews = {}
for r in list(wb_new['يحتاج مراجعة'].rows)[1:]:
    req = str(r[1].value or '').strip()
    cand = str(r[2].value or '').strip()
    wh = str(r[3].value or '').strip()
    reason = str(r[4].value or '').strip()
    if req:
        new_reviews[req] = (cand, wh, reason)

# Categorize old rows
matched_samples = []
stayed_rev_samples = []
rejected_strength_conflict = []
rejected_different_drug = []

from src.fast_match.coordinator import get_strength_pattern

for r in old_rows:
    req = str(r[1].value or '').strip()
    cand = str(r[2].value or '').strip()
    wh = str(r[3].value or '').strip()
    
    if req in new_matches:
        matched_samples.append((req, cand, new_matches[req]))
    elif req in new_reviews:
        stayed_rev_samples.append((req, cand, new_reviews[req]))
    else:
        s_req = get_strength_pattern(req)
        s_cand = get_strength_pattern(cand)
        if s_req and s_cand and s_req != s_cand:
            rejected_strength_conflict.append((req, cand, s_req, s_cand))
        else:
            rejected_different_drug.append((req, cand))

print(f"Total old review items analyzed: {len(old_rows)}")
print(f"1. Items now confirmed MATCHED in PROC-011: {len(matched_samples)}")
for req, cand, match in matched_samples[:8]:
    print(f"   * Req: '{req}'")
    print(f"     Old Cand: '{cand}'")
    print(f"     Now Matched with: '{match[0]}' in '{match[1]}'")
    print()

print(f"\n2. Items still kept in REVIEW (legitimate form differences): {len(stayed_rev_samples)}")
for req, cand, rev in stayed_rev_samples[:8]:
    print(f"   * Req: '{req}'")
    print(f"     Review Cand: '{rev[0]}' in '{rev[1]}'")
    print(f"     Reason: {rev[2]}")
    print()

print(f"\n3. Items rejected due to STRENGTH CONFLICT (التركيز خط أحمر): {len(rejected_strength_conflict)}")
for req, cand, sr, sc in rejected_strength_conflict[:10]:
    print(f"   * Req: '{req}' (Strength: {sr})")
    print(f"     Cand: '{cand}' (Strength: {sc})")
    print()

print(f"\n4. Items rejected due to DIFFERENT DRUG / NOT SAME BRAND: {len(rejected_different_drug)}")
for req, cand in rejected_different_drug[:10]:
    print(f"   * Req: '{req}' vs Cand: '{cand}'")
