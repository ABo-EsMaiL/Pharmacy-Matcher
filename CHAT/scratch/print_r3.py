import openpyxl

wb3 = openpyxl.load_workbook('d:/AI_Engineer/Pharmacy-agy/data/processes/PROC-003/results_PROC-003.xlsx')
ws = wb3['يحتاج مراجعة']
rows = list(ws.iter_rows(values_only=True))
print("Headers:", rows[0])
for idx, r in enumerate(rows[1:], 1):
    print(f"{idx}. Shortage: '{r[1]}' | Cand: '{r[2]}' | WH: '{r[3]}' | Reason: '{r[4]}'")
