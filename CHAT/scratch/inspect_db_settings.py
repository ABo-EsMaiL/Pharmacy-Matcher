import sqlite3
import json

conn = sqlite3.connect(r'D:\AI_Engineer\Pharmacy-agy-vision\desktop_app\history.db')
tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print("Tables:", tables)

for t in tables:
    tname = t[0]
    print(f"\n--- Table: {tname} ---")
    rows = conn.execute(f"SELECT * FROM {tname} LIMIT 5").fetchall()
    for r in rows:
        print(r)
