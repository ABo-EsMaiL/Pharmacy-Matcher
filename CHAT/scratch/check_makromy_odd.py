import openpyxl

wb6 = openpyxl.load_workbook(r'D:\AI_Engineer\Pharmacy-agy\data\processes\PROC-006\results_PROC-006.xlsx', data_only=True)
ws = wb6['المكرومي المنصورة.pdf']

for row in ws.iter_rows(min_row=2, values_only=True):
    if any(k in str(row[0]) for k in ['ابيكوتيل', 'برونكوفين']):
        print(f"Shortage: '{row[0]}' | Warehouse: '{row[1]}' | Grade: '{row[2]}'")
