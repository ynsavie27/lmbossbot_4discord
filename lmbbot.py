import datetime
import sqlite3
#discordのライブラリをインポート
import discord
#自分のトークンにしてね
TOKEN = 'NzQ5NDkzNjMzNTQ3NTAxNTY5.X0syVw.Zh95SnG5-FVQUPy5vz_GeNmFKH0'

# 接続に必要なオブジェクトを作る
client = discord.Client()

# DB接続オブジェクトを生成
conn = sqlite3.connect('lmbbot.sqlite3')
c = conn.cursor()

#BOTが起動したとき
@client.event
async def on_ready():
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
        
        if bname == 'てきこ':
            cycle_m = 10
            rand = '(起きれば)'
        elif bname == 'アルフィア':
            cycle_h = 4
        elif bname == 'イフリート':
            cycle_h = 2
            rand = '(ランダム)'
        elif bname == 'ガーストロード':
            cycle_h = 3
            rand = '(ランダム)'
        elif bname == 'カーツ':
            cycle_h = 10
            rand = '(ランダム)'
        elif bname == 'カスパ':
            cycle_h = 2
        elif bname == '監視者デーモン':
            cycle_h = 6
        elif bname == '巨大守護アリ':
            cycle_h = 2
            rand = '(ランダム)'
        elif bname == '古代巨人':
            cycle_h = 5
            rand = '(ランダム)'
        elif bname == '山賊の親分':
            cycle_h = 3
        elif bname == 'ジャイアントクロコダイル':
            cycle_h = 3
        elif bname == 'ジャイアントドレイク':
            cycle_h = 3
            rand = '(ランダム)'
        elif bname == 'ジャイアントワーム':
            cycle_h = 2
            rand = '(ランダム)'
        elif bname == 'シャスキー赤':
            cycle_h = 2
            rand = '(ランダム)'
        elif bname == 'シャスキー緑':
            cycle_h = 2
            rand = '(ランダム)'
        elif bname == 'スピリッド':
            cycle_h = 3
            rand = '(ランダム?)'
        elif bname == 'ダークハイエルダー':
            cycle_h = 3
        elif bname == 'デスナイト':
            cycle_h = 7
            rand = '(ランダム)'
        elif bname == 'ドッペルゲンガーボス':
            cycle_h = 4
            rand = '(ランダム)'
        elif bname == 'ドレイク西':
            cycle_h = 2
        elif bname == 'ドレイク中央':
            cycle_h = 3
        elif bname == 'ドレイク東':
            cycle_h = 3
        elif bname == 'フェニックス':
            cycle_h = 7
            rand = '(ランダム)'
        elif bname == 'ボスクライン':
            cycle_h = 1
        elif bname == 'マーヨ':
            cycle_h = 3
            rand = '(ランダム)'
        elif bname == 'リカント':
            cycle_h = 8
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
            pop_time = poptime.strftime("%Y%m%d%H%M")
            addtext = ""
            msgsendflg = 0
            disableflg = 0

            #DB書き込み
            c.execute("INSERT INTO bosspop(Ch_ID, Boss_ID, Pop_Time, AddText, MsgSendFlg, DisableFlg) VALUES (?, ?, ?, ?, ?, ?)",
                                          (ch_id, boss_id, pop_time, addtext, msgsendflg, disableflg))
            conn.commit

            for row in c.execute('SELECT * FROM bosspop'):
                print(row)
            
            conn.close

            await message.channel.send(bname + ' Next Pop ' + poptime.strftime("%Y/%m/%d %H:%M") + rand)
            #print(str(message.channel.id))
        else:
            return
        
    else:
        return

#BOTの起動
client.run(TOKEN)
