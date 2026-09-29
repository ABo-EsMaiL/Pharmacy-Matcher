import sys
sys.path.insert(0, r'd:\AI_Engineer\Pharmacy-agy')
import openpyxl, json
from src.extract.pdf_reader import parse_structured_result
from src.match.text_match import normalize_text
from datetime import datetime

# 1. Load original 0913.xlsx
wb_orig = openpyxl.load_workbook('d:/AI_Engineer/Pharmacy-agy/data/processes/PROC-002/input_shortages/0913.xlsx')
ws_orig = wb_orig['ورقة2']

shortages_by_row = {}
for r in range(7, ws_orig.max_row + 1):
    c = ws_orig.cell(r, 1).value
    n = ws_orig.cell(r, 2).value
    d = ws_orig.cell(r, 3).value
    q = ws_orig.cell(r, 4).value
    if n:
        shortages_by_row[r] = {
            "row": r,
            "client": c or "ص ايه شكر/الحدين 3",
            "name": str(n).strip(),
            "date": d or datetime(2026, 9, 13, 0, 0),
            "qty": q or 1
        }

# 2. Load Amr items
amr_data = json.load(open('d:/AI_Engineer/Pharmacy-agy/data/processes/PROC-002/input_warehouses/جملة العمروووو.json', encoding='utf-8'))
amr_items = [i['item_name_raw'] for i in parse_structured_result(amr_data, 'amr')]

# 3. Load Salam items
salam_data = json.load(open('d:/AI_Engineer/Pharmacy-agy/data/processes/PROC-002/input_warehouses/السلام شبين.json', encoding='utf-8'))
salam_items = [i['item_name_raw'] for i in parse_structured_result(salam_data, 'salam')]

print(f"Loaded {len(shortages_by_row)} shortages from 0913.xlsx")
print(f"Loaded {len(amr_items)} Amr warehouse items")
print(f"Loaded {len(salam_items)} Salam warehouse items")

# Known direct matches from 0913.xlsx for Amr:
# Row 854: افيروكوكسيب90مجم20قرص س ج <-> افيرو كوكسـيب 90مجم-32ب
# Row 394: امبوفير 5امبول س ج <-> امبوفير حقن جديد
# Row 957: ستيمولان امبول <-> ستيمولان 400مجم كبسول
# Row 646: بانثينول النيل2%كريم وسط <-> بانثينول كريم كبير سعر قديم باكو 25
# Row 150: ليفوفلوكساسين750مجم 5قرص س ج <-> ليفوفلوكساسين 750 فيال باكو 12 كرتونه 144
# Row 568: لبن هيرو بيبي 2 <-> هيرو 222 نيوترادينس 384
amr_known_rows = [854, 394, 957, 646, 150, 568]

# Known direct matches from 0913.xlsx for Salam:
salam_known_rows = [
    399, 451, 450, 611, 490, 680, 205, 505, 127, 330, 
    154, 974, 512, 920, 697, 16, 482, 217, 339, 237, 
    593, 229, 7, 572, 89, 321, 65, 402, 366, 758,
    444, 470, 682, 750, 807
]

# Ensure uniqueness
amr_rows_selected = list(dict.fromkeys(amr_known_rows))
salam_rows_selected = [r for r in list(dict.fromkeys(salam_known_rows)) if r not in amr_rows_selected]

print(f"Unique matching rows found in 0913.xlsx for Amr: {len(amr_rows_selected)}")
print(f"Unique matching rows found in 0913.xlsx for Salam: {len(salam_rows_selected)}")
