import openpyxl

wb6 = openpyxl.load_workbook(r'D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-006\results_PROC-006.xlsx', data_only=True)
ws = wb6['السلام شبين.pdf']
for r in range(1, 4):
    print(f"Row {r}: {[c.value for c in ws[r]]}")
