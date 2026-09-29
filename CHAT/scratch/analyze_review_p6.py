import openpyxl

wb6 = openpyxl.load_workbook(r'D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-006\results_PROC-006.xlsx', data_only=True)
ws = wb6['يحتاج مراجعة']

print("=== ALL 33 ITEMS IN 'يحتاج مراجعة' (PROC-006) ===")
for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 1):
    req = row[1]
    cand = row[2]
    wh = row[3]
    reason = row[4] if len(row) > 4 else ""
    print(f"{i:2d}. المطلوب: {req}")
    print(f"    المرشح: {cand} ({wh})")
    print(f"    السبب:  {reason}")
