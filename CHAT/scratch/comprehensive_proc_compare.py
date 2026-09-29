import openpyxl
import json

file1 = 'd:/AI_Engineer/Pharmacy-agy/data/processes/PROC-001/results_PROC-001.xlsx'
file2 = 'd:/AI_Engineer/Pharmacy-agy/data/processes/PROC-002/results_PROC-002.xlsx'

wb1 = openpyxl.load_workbook(file1)
wb2 = openpyxl.load_workbook(file2)

def extract_rows(wb, sheet_name):
    if sheet_name not in wb.sheetnames:
        return []
    ws = wb[sheet_name]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    headers = [str(c).strip() if c is not None else "" for c in rows[0]]
    data = []
    for r in rows[1:]:
        row_dict = {headers[i]: r[i] for i in range(min(len(headers), len(r)))}
        data.append(row_dict)
    return data

# 1. Summary comparison
print("=================== 1. ملخص (SUMMARY) ===================")
summary1 = extract_rows(wb1, 'ملخص')
summary2 = extract_rows(wb2, 'ملخص')
print("PROC-001 Summary:")
for row in summary1:
    print(" ", row)
print("\nPROC-002 Summary:")
for row in summary2:
    print(" ", row)

# 2. Review Sheet comparison
print("\n=================== 2. يحتاج مراجعة (NEEDS REVIEW) ===================")
r1 = extract_rows(wb1, 'يحتاج مراجعة')
r2 = extract_rows(wb2, 'يحتاج مراجعة')
print(f"PROC-001 Reviews count: {len(r1)}")
print(f"PROC-002 Reviews count: {len(r2)}")

r1_dict = {(x.get('اسم الصنف المطلوب', '') or x.get('صنف النواقص', '') or list(x.values())[0]): x for x in r1}
r2_dict = {(x.get('اسم الصنف المطلوب', '') or x.get('صنف النواقص', '') or list(x.values())[0]): x for x in r2}

print("\n--- Items in PROC-001 Reviews that are NOT in PROC-002 Reviews ---")
for k, v in r1.items() if hasattr(r1, 'items') else enumerate(r1):
    # let's print all r1 items
    pass

print("PROC-001 all reviews:")
for idx, item in enumerate(r1, 1):
    print(f"  {idx}. {item}")

print("\nPROC-002 all reviews:")
for idx, item in enumerate(r2, 1):
    print(f"  {idx}. {item}")

# 3. Warehouse Matches comparison
wh_sheets = [s for s in wb1.sheetnames if s not in ['ملخص', 'لم يُعثر عليه', 'يحتاج مراجعة']]
print("\n=================== 3. MATCHES BY WAREHOUSE ===================")
m1_total = []
m2_total = []

for s in wh_sheets:
    m1_rows = extract_rows(wb1, s)
    # in wb2 sheet name might be truncated slightly or identical
    s2_match = s if s in wb2.sheetnames else [x for x in wb2.sheetnames if x[:15] == s[:15]][0]
    m2_rows = extract_rows(wb2, s2_match)
    print(f"Warehouse '{s}': PROC-001 had {len(m1_rows)} matches, PROC-002 has {len(m2_rows)} matches")
    for r in m1_rows:
        r['_wh'] = s
        m1_total.append(r)
    for r in m2_rows:
        r['_wh'] = s
        m2_total.append(r)

print(f"\nTotal Matched in PROC-001: {len(m1_total)}")
print(f"Total Matched in PROC-002: {len(m2_total)}")

# Let's find matches present in PROC-001 but missing in PROC-002
# What are the column names in matched sheets?
if m1_total:
    print("Match columns:", list(m1_total[0].keys()))

m1_keys = {}
for r in m1_total:
    # try candidate keys
    shortage = r.get('صنف النواقص') or r.get('اسم الصنف المطلوب') or r.get('اسم الصنف') or list(r.values())[0]
    cand = r.get('صنف المخزن المطابق') or r.get('الصنف المطابق') or list(r.values())[1]
    m1_keys[(shortage, r['_wh'])] = (cand, r)

m2_keys = {}
for r in m2_total:
    shortage = r.get('صنف النواقص') or r.get('اسم الصنف المطلوب') or r.get('اسم الصنف') or list(r.values())[0]
    cand = r.get('صنف المخزن المطابق') or r.get('الصنف المطابق') or list(r.values())[1]
    m2_keys[(shortage, r['_wh'])] = (cand, r)

dropped_matches = set(m1_keys.keys()) - set(m2_keys.keys())
new_matches = set(m2_keys.keys()) - set(m1_keys.keys())

print(f"\n--- MATCHES DROPPED ({len(dropped_matches)}) [In PROC-001 but NOT in PROC-002] ---")
for k in sorted(dropped_matches):
    cand, r = m1_keys[k]
    print(f"  * Warehouse: {k[1]} | Shortage: '{k[0]}' -> Was matched with: '{cand}'")

print(f"\n--- NEW MATCHES ADDED ({len(new_matches)}) [In PROC-002 but NOT in PROC-001] ---")
for k in sorted(new_matches):
    cand, r = m2_keys[k]
    print(f"  * Warehouse: {k[1]} | Shortage: '{k[0]}' -> Now matched with: '{cand}'")

# 4. Not Found comparison
print("\n=================== 4. لم يُعثر عليه (NOT FOUND) ===================")
nf1 = extract_rows(wb1, 'لم يُعثر عليه')
nf2 = extract_rows(wb2, 'لم يُعثر عليه')
print(f"PROC-001 Not found count: {len(nf1)}")
print(f"PROC-002 Not found count: {len(nf2)}")

nf1_names = {r.get('اسم الصنف') or list(r.values())[0] for r in nf1}
nf2_names = {r.get('اسم الصنف') or list(r.values())[0] for r in nf2}

now_not_found = nf2_names - nf1_names
print(f"\nItems newly in NOT FOUND in PROC-002 ({len(now_not_found)}):")
for name in sorted(now_not_found):
    print(f"  - {name}")
