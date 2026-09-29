import sqlite3

conn = sqlite3.connect('data/history.db')
cursor = conn.cursor()
cursor.execute('SELECT id, created_at, status, total_shortages, matched_count, review_count, not_found_count, output_file FROM processes')
rows = cursor.fetchall()
for r in rows:
    print(r)
