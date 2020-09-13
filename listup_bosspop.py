import sqlite3

conn = sqlite3.connect('lmbbot.sqlite3')
c = conn.cursor()
c.execute('SELECT * FROM bosspop')
res = c.fetchall()
print(len(res))
for row in res:
    print(row)
