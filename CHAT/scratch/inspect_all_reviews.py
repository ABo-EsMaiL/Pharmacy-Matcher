import openpyxl

wb = openpyxl.load_workbook(r'D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-001\results_PROC-001.xlsx')
ws = wb['يحتاج مراجعة']

rows = list(ws.iter_rows(values_only=True))[1:]
print(f"Total reviews: {len(rows)}")

reasons = {}
for r in rows:
    reason = r[4]
    prefix = reason[:30] if reason else 'None'
    reasons[prefix] = reasons.get(prefix, 0) + 1

print("\nReason categories:")
for k, v in reasons.items():
    print(f"  {k}... : {v}")

print("\nSample reviews:")
for i, r in enumerate(rows[:25], 1):
    print(f"{i:2d}. Req: '{r[1]}' | WH: '{r[2]}' ({r[3]}) => {r[4]}")
