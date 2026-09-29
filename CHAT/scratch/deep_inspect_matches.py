import openpyxl

wb = openpyxl.load_workbook(r'D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-001\results_PROC-001.xlsx')

print("="*60)
print("ALL MATCHES IN WAREHOUSE SHEETS:")
print("="*60)

for sheet in wb.sheetnames:
    if sheet not in ['ملخص', 'لم يُعثر عليه', 'يحتاج مراجعة']:
        ws = wb[sheet]
        rows = list(ws.iter_rows(values_only=True))[1:]
        print(f"\n--- {sheet} ({len(rows)} matches) ---")
        for r in rows:
            print(f"  Req: '{r[0]}'  <===>  WH: '{r[1]}'  [{r[2]}]")

print("\n" + "="*60)
print("SAMPLE REVIEWS (First 30 rows of يحتاج مراجعة):")
print("="*60)
ws_rev = wb['يحتاج مراجعة']
rev_rows = list(ws_rev.iter_rows(values_only=True))[1:]
print(f"Total reviews: {len(rev_rows)}")
for i, r in enumerate(rev_rows[:40]):
    print(f"{i+1}. Req: '{r[1]}' | WH: '{r[2]}' | المخزن: '{r[3]}' | السبب: {r[4]}")
