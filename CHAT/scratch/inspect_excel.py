import openpyxl

wb = openpyxl.load_workbook(r"D:\AI_Engineer\Pharmacy-agy\data\test_shortages_200.xlsx", read_only=True)
sheet = wb.active
print("Sheet title:", sheet.title)
for i, r in enumerate(sheet.iter_rows(values_only=True)):
    if i < 8:
        print(f"Row {i}: {r}")
