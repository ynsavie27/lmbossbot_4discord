import settings
import datetime
import sqlite3
#discordのライブラリをインポート
import discord
from discord.ext import tasks

# 接続に必要なオブジェクトを作る
client = discord.Client()

# # DB接続オブジェクトを生成
conn = sqlite3.connect('./lmbbot.sqlite3')
c = conn.cursor()

loop_sec = settings.LOOP_INTVL_SEC

@tasks.loop(seconds=loop_sec)
async def fetch_popdata():
    now = datetime.datetime.today()
    now_a10m = now + datetime.timedelta(minutes=10)
    print(now)
    c.execute("SELECT * FROM bosspop where ? <= PopTime AND PopTime <= ? AND MsgSendFlg = 0 AND DisableFlg = 0", (int(now.strftime("%y%m%d%H%M")), int(now_a10m.strftime("%y%m%d%H%M"))))
    res = c.fetchall()
    print(len(res))
    for row in res:
        print(row)
        send_channel = client.get_channel(row[1])
        await send_channel.send('もうすぐ ' + row[2] + ' pop ' + str(row[3])[6:8] + ':' + str(row[3])[8:])
        c.execute("UPDATE bosspop SET MsgSendFlg = 1 WHERE No_ = ?", (row[0],))
        conn.commit()

#BOTが起動したとき
@client.event
async def on_ready():
    # c.execute("SELECT * FROM bosspop")
    # ress = c.fetchall()
    print('寝てた')

#メッセージを受け取ったとき
@client.event
async def on_message(message):
    # Botだったら無視
    if message.author.bot:
        return
#    if message.content == '/hello':
#        await message.channel.send('hello')

    # コマンド解釈
    s_msg_list = message.content.split(' ') #半角スペースでメッセージを分割しリストに格納
    if len(s_msg_list) < 3:
        return
    
    if s_msg_list[0] == '/end':
        cycle_h = 0
        cycle_m = 0
        rand = ''
        bname = s_msg_list[1]
        
        if bname == 'てきこ' or bname == 'てっき' or bname == '敵子':
            cycle_m = 15
            rand = '(起きれば)'
        elif bname == 'ボスクライン' or bname == 'クライン':
            cycle_h = 1
        elif bname == 'ジャイアントワーム' or bname == 'ワーム':
            cycle_h = 2
            rand = '(ランダム)'
        elif bname == 'シャスキー緑' or bname == '緑シャス':
            cycle_h = 2
            rand = '(ランダム)'
        elif bname == 'シャスキー赤' or bname == '赤シャス':
            cycle_h = 2
            rand = '(ランダム)'
        elif bname == 'イフリート' or bname == 'イフ':
            cycle_h = 2
            rand = '(ランダム)'
        elif bname == 'ドレイク西' or bname == '西ドレ' or bname == '49ドレ':
            cycle_h = 2
        elif bname == 'ドレイク北' or bname == '北ドレ' or bname == '47ドレ':
            cycle_h = 2
        elif bname == 'カスパ' or bname == 'カスパーズ':
            cycle_h = 2
        elif bname == '巨大守護アリ' or bname == 'アリ' or bname == '蟻' or bname == 'あり':
            cycle_h = 2
            rand = '(ランダム)'
        elif bname == 'ガーストロード':
            cycle_h = 3
            rand = '(ランダム)'
        elif bname == 'スピリッド':
            cycle_h = 3
            rand = '(ランダム?)'
        elif bname == '山賊の親分' or bname == '親分':
            cycle_h = 3
        elif bname == 'ダークハイエルダー' or bname == 'エルダー' or bname == 'ハイエルダー':
            cycle_h = 3
        elif bname == 'ジャイアントクロコダイル' or bname == 'クロコ' or bname == 'ワニ':
            cycle_h = 3
        elif bname == 'マーヨ':
            cycle_h = 3
            rand = '(ランダム)'
        elif bname == 'ドレイク中央' or bname == '中央ドレ' or bname == '46ドレ':
            cycle_h = 3
        elif bname == 'ドレイク東' or bname == '48ドレ' or bname == '東ドレ':
            cycle_h = 3
        elif bname == '疾風の巨大ドレイク' or bname == 'デカドレ' or bname == '大ドレ':
            cycle_h = 3
            rand = '(ランダム)'
        elif bname == 'アルフィア':
            cycle_h = 4
        elif bname == 'ドッペルゲンガーボス' or bname == 'ドッペ' or bname == 'ドッペボス':
            cycle_h = 4
            rand = '(ランダム)'
        elif bname == '古代巨人' or bname == 'ジャイアント' or bname == 'エンシェントジャイアント':
            cycle_h = 5
            rand = '(ランダム)'
        elif bname == 'マンボラビット' or bname == 'マンボ':
            cycle_h = 6
        elif bname == '深淵の主':
            cycle_h = 6
        elif bname == '監視者デーモン' or bname == '青デーモン':
            cycle_h = 6
        elif bname == 'デスナイト' or bname == 'DK':
            cycle_h = 7
            rand = '(ランダム)'
        elif bname == 'フェニックス' or bname == 'フェニ':
            cycle_h = 7
            rand = '(ランダム)'
        elif bname == 'リカント':
            cycle_h = 8
            rand = '(ランダム)'
        elif bname == 'カーツ':
            cycle_h = 10
            rand = '(ランダム)'
        else:
            await message.channel.send('不明なボス名')
            return
        
        etimes = s_msg_list[2]
        errmsg = '不正な時刻指定'
        
        if len(etimes) == 4:
            if etimes.isdecimal():
                ehour = int(etimes[:2])
                emin = int(etimes[2:])
                if 0 <= ehour and ehour < 24 and 0 <= emin and emin < 60:
                    tdy = datetime.datetime.today()
                    edaytime = tdy.replace(hour=ehour, minute=emin, second=0, microsecond=0)
                    if tdy < edaytime:
                        edaytime = edaytime + datetime.timedelta(days=-1)
                    errmsg = ''
        
        if len(errmsg) > 0:
            await message.channel.send(errmsg)
            return
        
        if cycle_h > 0 or cycle_m > 0:
            poptime = edaytime + datetime.timedelta(hours=cycle_h, minutes=cycle_m)

            ch_id = message.channel.id
            boss_id = bname
            end_time = int(edaytime.strftime("%y%m%d%H%M"))
            pop_time = int(poptime.strftime("%y%m%d%H%M"))
            addtext = ""
            msgsendflg = 0
            disableflg = 0

            #DB書き込み
            c.execute("INSERT INTO bosspop(ChID, BossID, EndTime, PopTime, AddText, MsgSendFlg, DisableFlg) VALUES (?, ?, ?, ?, ?, ?, ?)", (ch_id, boss_id, end_time, pop_time, addtext, msgsendflg, disableflg))
            conn.commit()
            # try:
            #     conn.commit()
            # except sqlite3.Error as er:
            #     print(er.message)

            # for row in c.execute('SELECT * FROM bosspop'):
            #     print(row)
            
            await message.channel.send(bname + ' Next Pop ' + poptime.strftime("%m/%d %H:%M") + rand)
            #print(str(message.channel.id))

            # conn.close()

        else:
            return
        
    else:
        return

fetch_popdata.start()

#BOTの起動
client.run(settings.TOKEN)
