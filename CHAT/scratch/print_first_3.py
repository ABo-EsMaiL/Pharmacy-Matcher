import openpyxl

wb6 = openpyxl.load_workbook(r'D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-006\results_PROC-006.xlsx', data_only=True)
first_sheets = ['مخزن الحياة فارم اسكندريه-170.p', 'جملة العمروووو.pdf', 'السلام شبين.pdf']

for s in first_sheets:
    ws = wb6[s]
    rows = list(ws.iter_rows(min_row=2, values_only=True))
    print(f"\n--- {s} ({len(rows)} matches) ---")
    for idx, r in enumerate(rows, 1):
        print(f"  {idx:2d}. {r[0]}  ==>  {r[1]}")
