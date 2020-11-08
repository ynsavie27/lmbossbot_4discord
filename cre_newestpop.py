import sqlite3

conn = sqlite3.connect('lmbbot.sqlite3')
c = conn.cursor()
c.execute('create table newestpop(ChID INTEGER, BossID TEXT, PopMin INTEGER, IntvlMin INTEGER, AddText TEXT, SendMsgCnt INTEGER, DisableFlg INTEGER)')
