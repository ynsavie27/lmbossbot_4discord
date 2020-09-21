import sqlite3

conn = sqlite3.connect('lmbbot.sqlite3')
c = conn.cursor()
c.execute('create table bosspop(No_ INTEGER PRIMARY KEY, ChID INTEGER, BossID TEXT, EndTime INTEGER, PopTime INTEGER, AddText TEXT, MsgSendFlg INTEGER, DisableFlg INTEGER)')
