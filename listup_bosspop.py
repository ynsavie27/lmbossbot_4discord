import sqlite3

conn = sqlite3.connect('lmbbot.sqlite3')
c = conn.cursor()
c.execute('SELECT * FROM bosspop')
for row in c.fetchall():
    print(row)
