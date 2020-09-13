import sqlite3

conn = sqlite3.connect('lmbbot.sqlite3')
c = conn.cursor()
c.execute('create table bosspop(No_ INTEGER PRIMARY KEY, Ch_ID INTEGER, Boss_ID TEXT, Pop_Time INTEGER, AddText TEXT, MsgSendFlg INTEGER, DisableFlg INTEGER)')