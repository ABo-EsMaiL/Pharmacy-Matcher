import openpyxl

wb = openpyxl.load_workbook(r'D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-001\results_PROC-001.xlsx')
ws_rev = wb['يحتاج مراجعة']
rev_rows = list(ws_rev.iter_rows(values_only=True))[1:]

print(f"Total reviews in sheet: {len(rev_rows)}")
for i, r in enumerate(rev_rows, 1):
    print(f"{i:2d}. Warehouse: [{r[3]}]")
    print(f"    المطلوب: '{r[1]}'")
    print(f"    المخزن : '{r[2]}'")
    print(f"    السبب  : {r[4]}\n")
