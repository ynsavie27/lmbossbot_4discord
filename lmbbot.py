import datetime
#discordのライブラリをインポート
import discord
#自分のトークンにしてね
TOKEN = 'NzQ5NDkzNjMzNTQ3NTAxNTY5.X0syVw.Zh95SnG5-FVQUPy5vz_GeNmFKH0'

# 接続に必要なオブジェクトを作る
client = discord.Client()

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
    
    if s_msg_list[0] == '/bend':
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
            await message.channel.send('Unknown Boss Name')
            return
        
        etimes = s_msg_list[2]
        errmsg = 'Wrong Time Format'
        
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
            await message.channel.send(bname + ' Next Pop ' + poptime.strftime("%Y/%m/%d %H:%M") + rand)
        else:
            return
        
    else:
        return

#BOTの起動
client.run(TOKEN)
