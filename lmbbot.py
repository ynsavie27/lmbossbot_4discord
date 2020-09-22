import settings
import datetime
import sqlite3
import json
from collections import OrderedDict

# discordのライブラリをインポート
import discord
from discord.ext import tasks

# 接続に必要なオブジェクトを生成
client = discord.Client()

# # bot管理チャンネルオブジェクト用変数を用意
# ctrl_ch = None

# DB接続オブジェクトを生成
conn = sqlite3.connect('./lmbbot.sqlite3')
c = conn.cursor()

# ボスマスタJSONファイルを読み込み
with open('./boss_mst.json', 'r', encoding='utf-8') as f:
    boss_mst = json.load(f, object_pairs_hook=OrderedDict)

### ボスマスタレイアウト
# boss_mst[ボスIDのテキスト]={
#     'intvl_min':分数,
#     'pop_time':時刻'YYMM'のリスト,
#     'duration_min':分数,
#     'pop_rate':数値(0-100%),
#     'pop_place':テキスト,
#     'name':ボス名のリスト,
#     'note':テキスト,
#     'disable_flg':数値(0以外なら無効)
# }

# ボス名からボスID取得用変数を生成
# key:ボス名、値:ボスIDの辞書
boss_name2id = {}
for bid in boss_mst.keys():
    bname_list = boss_mst[bid].get('name')
    for bname in bname_list:
        boss_name2id[bname] = bid

@tasks.loop(seconds=settings.LOOP_INTVL_SEC)
async def fetch_popdata():
    # bot管理チャンネルオブジェクトを取得
    ctrl_ch = client.get_channel(settings.CTRL_CHANNEL_ID)

    # POPデータ取得期間を計算
    now = datetime.datetime.today()
    now_a10m = now + datetime.timedelta(minutes=10)
    # print(now)

    ### bosspopテーブルレイアウト
    # [0]No_ INTEGER, [1]ChID INTEGER, [2]BossID TEXT,
    # [3]EndTime INTEGER, [4]PopTime INTEGER, [5]AddText TEXT,
    # [6]MsgSendFlg INTEGER, [7]DisableFlg INTEGER

    #POPデータを取得
    c.execute(
        "SELECT * FROM bosspop where ? <= PopTime AND PopTime <= ? AND MsgSendFlg = 0 AND DisableFlg = 0",
        (int(now.strftime("%y%m%d%H%M")), int(now_a10m.strftime("%y%m%d%H%M")))
    )

    res = c.fetchall()
    # print(len(res))
    for row in res:
        # print(row)

        if settings.DEBUG:
            # 管理ChへMsg送信
            await ctrl_ch.send('POPデータ取得: ' + str(row))

        # ボスマスタからボス情報取得
        bossinfo = boss_mst.get(row[2])

        # ボスマスタ取得成否判定
        if bossinfo == None:
            # マスタ取得失敗
            errmsg = 'RowNo.' + str(row[0]) + ':BossID[' + row[2] + '] is None.'
            print(errmsg)
            # 管理ChへMsg送信
            await ctrl_ch.send(errmsg)

            # 元レコードに無効フラグを立てる
            c.execute("UPDATE bosspop SET DisableFlg = 3 WHERE No_ = ?", (row[0],))
            conn.commit()
        else:
            # マスタ取得成功
            # 送信メッセージ構築
            msg_txt = '【ボス予告】もうすぐ ' + bossinfo['name'][0] + ' がPOP! ' + str(row[4])[6:8] + ':' + str(row[4])[8:]
            if bossinfo['pop_rate'] < 100:
                msg_txt += '(ランダム)'
            if bossinfo['note'] != '':
                msg_txt += bossinfo['note']
            if bossinfo['pop_place'] != '':
                msg_txt += ' @' + bossinfo['pop_place']
            if row[5] != '':
                msg_txt += '\n備考:' + row[5]
            
            # 送信先チャンネルオブジェクトを取得
            send_channel = client.get_channel(row[1])
            # POP予告メッセージ送信
            await send_channel.send(msg_txt)

            # 当該メッセージ元レコードの送信フラグを立てる
            c.execute("UPDATE bosspop SET MsgSendFlg = 1 WHERE No_ = ?", (row[0],))
            conn.commit()

            if settings.DEBUG:
                # 管理ChへMsg送信
                await ctrl_ch.send('sendmsg to [' + send_channel.name + ']: \n「' + msg_txt + '」')

# botが起動したとき
@client.event
async def on_ready():
    # bot管理チャンネルオブジェクトを取得
    ctrl_ch = client.get_channel(settings.CTRL_CHANNEL_ID)
    print('寝てた')
    # 管理ChへMsg送信
    await ctrl_ch.send('bot start')

# メッセージを受け取ったとき
@client.event
async def on_message(message):
    # Botだったら無視
    if message.author.bot:
        return

    # コマンド解釈
    # 先頭文字判定
    if message.content[0] != '/':
        return
    
    # 半角スペースでメッセージを分割しリストに格納
    s_msg_list = message.content.split(' ')

    # コマンド別処理
    if s_msg_list[0] == '/end':
    # end報告

        # 引き数不足なら無視
        if len(s_msg_list) < 3:
            return

        # ボス名チェック・ボスID取得
        bname = s_msg_list[1]
        bid = boss_name2id.get(bname)
        if bid == None:
            await message.channel.send('不明なボス名')
            return

        # 時刻形式チェック（"YYMM"形式か）
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
        
        # ボスマスタから各種情報取得
        boss_info = boss_mst[bid]
        intvl_h = boss_info['intvl_min'] // 60
        intvl_m = boss_info['intvl_min'] % 60
        rand = ''
        if boss_info['pop_rate'] < 100:
            rand = '(ランダム)'
        note = boss_info['note']

        if intvl_h > 0 or intvl_m > 0:
            poptime = edaytime + datetime.timedelta(hours=intvl_h, minutes=intvl_m)
            ch_id = message.channel.id
            end_time = int(edaytime.strftime("%y%m%d%H%M"))
            pop_time = int(poptime.strftime("%y%m%d%H%M"))
            addtext = ''
            if len(s_msg_list) > 3:
                addtext = s_msg_list[3].strip()

            # bosspopテーブルに書き込み
            c.execute(
                "INSERT INTO bosspop(ChID, BossID, EndTime, PopTime, AddText, MsgSendFlg, DisableFlg) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (ch_id, bid, end_time, pop_time, addtext, 0, 0)
            )
            conn.commit()
            # try:
            #     conn.commit()
            # except sqlite3.Error as er:
            #     print(er.message)
            
            addstr = ''
            if len(addtext) > 0:
                addstr = ' 備考:' + addtext
            # 報告元チャンネルにメッセージ返信
            await message.channel.send(bname + ' Next Pop ' + poptime.strftime("%m/%d %H:%M") + rand + note + addstr)
            #print(str(message.channel.id))
        else:
            return
    else:
        return

# POPデータ取得ループ処理を開始
fetch_popdata.start()

# botの起動
client.run(settings.TOKEN)
