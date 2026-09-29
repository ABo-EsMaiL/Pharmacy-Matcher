import pandas as pd
from pathlib import Path

p7 = pd.read_excel("data/processes/PROC-007/results_PROC-007.xlsx", sheet_name="يحتاج مراجعة")
p8 = pd.read_excel("data/processes/PROC-008/results_PROC-008.xlsx", sheet_name="يحتاج مراجعة")

print("P7 Review Columns:", p7.columns.tolist())
print("P7 Review Count:", len(p7))
print("P8 Review Columns:", p8.columns.tolist())
print("P8 Review Count:", len(p8))

print("\nP7 Review first 5:")
print(p7.head())

print("\nP8 Review first 5:")
print(p8.head())
