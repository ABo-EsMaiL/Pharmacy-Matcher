import sqlite3, json
conn = sqlite3.connect(':memory:')
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute('create table test(id integer)')
c.execute('insert into test values(1)')
c.execute('select * from test')
rows = [dict(row) for row in c.fetchall()]
print(json.dumps(rows))
