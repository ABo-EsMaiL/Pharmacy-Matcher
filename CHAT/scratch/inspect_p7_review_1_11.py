import openpyxl

wb7 = openpyxl.load_workbook(r'D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-007\results_PROC-007.xlsx', data_only=True)
ws = wb7['يحتاج مراجعة']

print("="*70)
print("ITEMS 1 TO 11 IN 'يحتاج مراجعة' (PROC-007):")
print("="*70)

for i in range(2, 13):
    row = [c.value for c in ws[i]]
    req = row[1]
    cand = row[2]
    wh = row[3]
    reason = row[4] if len(row) > 4 else ""
    print(f"{i-1:2d}. المطلوب: {req}")
    print(f"    المرشح:  {cand} ({wh})")
    print(f"    السبب:   {reason}")
