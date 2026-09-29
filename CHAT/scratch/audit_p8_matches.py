import pandas as pd
import openpyxl

p8_path = "data/processes/PROC-008/results_PROC-008.xlsx"
wb8 = openpyxl.load_workbook(p8_path, data_only=True)
warehouse_sheets = [s for s in wb8.sheetnames if s not in ["ملخص", "يحتاج مراجعة", "لم يُعثر عليه"]]

with open("scratch_p8_matches_audit.txt", "w", encoding="utf-8") as f:
    for sheet in warehouse_sheets:
        df = pd.read_excel(p8_path, sheet_name=sheet)
        col_req = df.columns[0]
        col_wh = df.columns[1]
        f.write(f"\n==================== {sheet} ({len(df)} أصناف) ====================\n")
        for idx, row in df.iterrows():
            req = str(row[col_req]).strip()
            wh = str(row[col_wh]).strip()
            f.write(f"{idx+1}. المطلوب: [{req}]  <--->  المخزن: [{wh}]\n")

print("Audit written to scratch_p8_matches_audit.txt")
