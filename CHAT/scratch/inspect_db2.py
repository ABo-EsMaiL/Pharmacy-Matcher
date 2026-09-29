import sqlite3, json, sys
from pathlib import Path

DATA_DIR = Path('d:/AI_Engineer/Pharmacy-agy/data')
DB_PATH = DATA_DIR / 'history.db'

out_path = Path('C:/Users/kakak/.gemini/antigravity/brain/916274de-7f92-49fc-a0a8-d291664b474a/scratch/db_out.txt')

if not DB_PATH.exists():
    out_path.write_text("DB does not exist.")
    sys.exit(0)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute('SELECT * FROM processes')
rows = [dict(row) for row in c.fetchall()]

with open(out_path, 'w', encoding='utf-8') as f:
    for i, row in enumerate(rows):
        f.write(f"Row {i}:\n")
        for k, v in row.items():
            f.write(f"  {k}: {repr(v)}\n")
