import pandas as pd
import openpyxl

p7_path = "data/processes/PROC-007/results_PROC-007.xlsx"
p8_path = "data/processes/PROC-008/results_PROC-008.xlsx"

wb7 = openpyxl.load_workbook(p7_path, data_only=True)
wb8 = openpyxl.load_workbook(p8_path, data_only=True)

warehouse_sheets = [s for s in wb7.sheetnames if s not in ["ملخص", "يحتاج مراجعة", "لم يُعثر عليه"]]

# Build dictionary of item -> status & details for P7 and P8
def extract_all_items(filepath):
    xls = pd.ExcelFile(filepath)
    matches = {} # item -> (sheet, warehouse_drug, note)
    for sheet in warehouse_sheets:
        df = pd.read_excel(xls, sheet_name=sheet)
        col_req = df.columns[0]
        col_wh = df.columns[1]
        for _, row in df.iterrows():
            req = str(row[col_req]).strip()
            wh = str(row[col_wh]).strip()
            if req and req != "nan":
                matches[req] = ("مطابقة", sheet, wh)
                
    # Review
    df_rev = pd.read_excel(xls, sheet_name="يحتاج مراجعة")
    col_req = df_rev.columns[1] # اسم الصنف المطلوب
    col_wh = df_rev.columns[2]  # اسم المرشح في المخزن
    col_wh_name = df_rev.columns[3] # المخزن
    col_reason = df_rev.columns[4] # السبب
    for _, row in df_rev.iterrows():
        req = str(row[col_req]).strip()
        wh = str(row[col_wh]).strip()
        wh_n = str(row[col_wh_name]).strip()
        rsn = str(row[col_reason]).strip()
        if req and req != "nan":
            # If already matched in another sheet, note it
            if req not in matches:
                matches[req] = ("مراجعة", wh_n, f"{wh} | {rsn}")
            else:
                pass # Already matched
                
    # Not found
    df_nf = pd.read_excel(xls, sheet_name="لم يُعثر عليه")
    col_req = df_nf.columns[0]
    for _, row in df_nf.iterrows():
        req = str(row[col_req]).strip()
        if req and req != "nan" and req not in matches:
            matches[req] = ("لم يعثر عليه", "0913.xlsx", "")
            
    return matches

items_p7 = extract_all_items(p7_path)
items_p8 = extract_all_items(p8_path)

all_keys = set(items_p7.keys()) | set(items_p8.keys())

diffs = []
for k in all_keys:
    st7 = items_p7.get(k, ("غير موجود", "", ""))
    st8 = items_p8.get(k, ("غير موجود", "", ""))
    if st7[0] != st8[0] or (st7[0] == "مطابقة" and st8[0] == "مطابقة" and (st7[1] != st8[1] or st7[2] != st8[2])):
        diffs.append((k, st7, st8))

print(f"Total differences found: {len(diffs)}")

with open("scratch_diffs.txt", "w", encoding="utf-8") as f:
    f.write(f"Total differences found: {len(diffs)}\n\n")
    for k, st7, st8 in sorted(diffs, key=lambda x: (x[1][0], x[2][0])):
        f.write(f"الصنف: [{k}]\n")
        f.write(f"   PROC-007: الحالة={st7[0]} | المخزن={st7[1]} | التفاصيل={st7[2]}\n")
        f.write(f"   PROC-008: الحالة={st8[0]} | المخزن={st8[1]} | التفاصيل={st8[2]}\n")
        f.write("-" * 80 + "\n")
print("Saved to scratch_diffs.txt")

