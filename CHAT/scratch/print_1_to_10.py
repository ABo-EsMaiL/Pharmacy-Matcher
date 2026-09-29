import openpyxl

wb6 = openpyxl.load_workbook(r'D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-006\results_PROC-006.xlsx', data_only=True)
ws = wb6['يحتاج مراجعة']

print("=== ITEMS 1 TO 10 IN 'يحتاج مراجعة' (PROC-006) ===")
for i in range(2, 12):
    row = [c.value for c in ws[i]]
    print(f"{i-1:2d}. المطلوب: {row[1]}")
    print(f"    المرشح:  {row[2]} ({row[3]})")
    print(f"    السبب:   {row[4]}")
