import openpyxl

wb = openpyxl.load_workbook(r"D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-014\results_PROC-014.xlsx", data_only=True)
ws = wb['يحتاج مراجعة']
for i, r in enumerate(ws.iter_rows(values_only=True)):
    print(f"Row {i}: {r}")
