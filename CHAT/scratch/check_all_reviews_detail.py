import openpyxl

wb = openpyxl.load_workbook(r'D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-001\results_PROC-001.xlsx')
ws = wb['يحتاج مراجعة']
rows = list(ws.iter_rows(values_only=True))[1:]

print("="*80)
print(f"ALL {len(rows)} ITEMS IN 'يحتاج مراجعة':")
print("="*80)

for i, r in enumerate(rows, 1):
    req = r[1]
    wh = r[2]
    src = r[3]
    reason = r[4]
    print(f"{i:3d}. [{src}] '{req}'  <--->  '{wh}'")
    print(f"     السبب: {reason}\n")
