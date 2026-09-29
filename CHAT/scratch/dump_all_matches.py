import sys
sys.path.insert(0, ".")
import openpyxl

wb = openpyxl.load_workbook('data/processes/PROC-009/results_PROC-009.xlsx', data_only=True)

print("=== ALL MATCHES IN PROC-009 ===")
for sheet in wb.sheetnames:
    if sheet in ['ملخص', 'لم يُعثر عليه', 'يحتاج مراجعة']:
        continue
    ws = wb[sheet]
    for r in ws.iter_rows(min_row=2, values_only=True):
        req = str(r[0] or '')
        wh = str(r[1] or '')
        conf = str(r[2] or '')
        # print specific interesting patterns
        print(f"[{sheet}] '{req}'  ==>  '{wh}'")
