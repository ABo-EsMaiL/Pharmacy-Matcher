import pandas as pd
import openpyxl

p7_path = "data/processes/PROC-007/results_PROC-007.xlsx"
p8_path = "data/processes/PROC-008/results_PROC-008.xlsx"

wb7 = openpyxl.load_workbook(p7_path, data_only=True)
warehouse_sheets = [s for s in wb7.sheetnames if s not in ["ملخص", "يحتاج مراجعة", "لم يُعثر عليه"]]

def get_item_map(filepath):
    xls = pd.ExcelFile(filepath)
    item_map = {}
    
    # 1. Matches
    for s in warehouse_sheets:
        df = pd.read_excel(xls, sheet_name=s)
        for _, row in df.iterrows():
            req = str(row[df.columns[0]]).strip()
            wh = str(row[df.columns[1]]).strip()
            if req and req != "nan":
                item_map[req] = {"status": "مطابقة", "warehouse": s, "target": wh, "reason": ""}
                
    # 2. Review
    df_rev = pd.read_excel(xls, sheet_name="يحتاج مراجعة")
    for _, row in df_rev.iterrows():
        req = str(row[df_rev.columns[1]]).strip()
        wh = str(row[df_rev.columns[2]]).strip()
        wh_n = str(row[df_rev.columns[3]]).strip()
        rsn = str(row[df_rev.columns[4]]).strip()
        if req and req != "nan" and req not in item_map:
            item_map[req] = {"status": "مراجعة", "warehouse": wh_n, "target": wh, "reason": rsn}
            
    # 3. Not Found
    df_nf = pd.read_excel(xls, sheet_name="لم يُعثر عليه")
    for _, row in df_nf.iterrows():
        req = str(row[df_nf.columns[0]]).strip()
        if req and req != "nan" and req not in item_map:
            item_map[req] = {"status": "لم يعثر عليه", "warehouse": "-", "target": "-", "reason": ""}
            
    return item_map

m7 = get_item_map(p7_path)
m8 = get_item_map(p8_path)

all_reqs = set(m7.keys()) | set(m8.keys())

categories = {
    "مطابقة -> مراجعة": [],
    "مطابقة -> لم يعثر عليه": [],
    "مطابقة -> مطابقة (مخزن مختلف)": [],
    "مراجعة -> مطابقة": [],
    "مراجعة -> لم يعثر عليه": [],
    "لم يعثر عليه -> مطابقة": [],
    "لم يعثر عليه -> مراجعة": [],
    "متطابق تماماً في الاثنين": []
}

for req in sorted(all_reqs):
    i7 = m7.get(req, {"status": "غير موجود", "warehouse": "-", "target": "-", "reason": ""})
    i8 = m8.get(req, {"status": "غير موجود", "warehouse": "-", "target": "-", "reason": ""})
    
    s7, s8 = i7["status"], i8["status"]
    if s7 == "مطابقة" and s8 == "مطابقة":
        if i7["warehouse"] != i8["warehouse"] or i7["target"] != i8["target"]:
            categories["مطابقة -> مطابقة (مخزن مختلف)"].append((req, i7, i8))
        else:
            categories["متطابق تماماً في الاثنين"].append((req, i7, i8))
    elif s7 == "مطابقة" and s8 == "مراجعة":
        categories["مطابقة -> مراجعة"].append((req, i7, i8))
    elif s7 == "مطابقة" and s8 == "لم يعثر عليه":
        categories["مطابقة -> لم يعثر عليه"].append((req, i7, i8))
    elif s7 == "مراجعة" and s8 == "مطابقة":
        categories["مراجعة -> مطابقة"].append((req, i7, i8))
    elif s7 == "مراجعة" and s8 == "لم يعثر عليه":
        categories["مراجعة -> لم يعثر عليه"].append((req, i7, i8))
    elif s7 == "لم يعثر عليه" and s8 == "مطابقة":
        categories["لم يعثر عليه -> مطابقة"].append((req, i7, i8))
    elif s7 == "لم يعثر عليه" and s8 == "مراجعة":
        categories["لم يعثر عليه -> مراجعة"].append((req, i7, i8))

with open("scratch_cat.txt", "w", encoding="utf-8") as f:
    f.write("=== STATISTICAL BREAKDOWN ===\n")
    for cat, lst in categories.items():
        f.write(f"{cat}: {len(lst)} صنف\n")

    f.write("\n" + "="*80 + "\n")
    for cat in ["مطابقة -> مراجعة", "مطابقة -> لم يعثر عليه", "مطابقة -> مطابقة (مخزن مختلف)", "مراجعة -> مطابقة", "مراجعة -> لم يعثر عليه", "لم يعثر عليه -> مطابقة", "لم يعثر عليه -> مراجعة"]:
        lst = categories[cat]
        if not lst:
            continue
        f.write(f"\n### {cat} ({len(lst)} صنف):\n")
        for req, i7, i8 in lst:
            f.write(f"  * الصنف: [{req}]\n")
            f.write(f"    - في PROC-007: {i7['status']} ({i7['warehouse']}) -> [{i7['target']}]\n")
            f.write(f"    - في PROC-008: {i8['status']} ({i8['warehouse']}) -> [{i8['target']}]\n")

print("Saved to scratch_cat.txt")

