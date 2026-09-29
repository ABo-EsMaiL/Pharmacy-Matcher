import sqlite3, json, sys
from pathlib import Path

DATA_DIR = Path('d:/AI_Engineer/Pharmacy-agy/data')
DB_PATH = DATA_DIR / 'history.db'

if not DB_PATH.exists():
    print("DB does not exist.")
    sys.exit(0)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute('SELECT * FROM processes')
rows = [dict(row) for row in c.fetchall()]

for i, row in enumerate(rows):
    print(f"Row {i}:")
    for k, v in row.items():
        print(f"  {k}: {repr(v)}")
