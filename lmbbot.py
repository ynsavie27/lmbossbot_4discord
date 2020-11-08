import settings
import configparser
import datetime
import sqlite3
import json
from collections import OrderedDict

# discordのライブラリをインポート
import discord
from discord.ext import commands
from discord.ext import tasks

# DB接続オブジェクトを生成
conn = sqlite3.connect('./lmbbot.sqlite3')
c = conn.cursor()

# config = configparser.ConfigParser()
# config.read('./default.ini')

### ボスマスタロード関数
def bossmst_load(jsonpass):
    # ボスマスタJSONファイルを読み込み
    with open(jsonpass, 'r', encoding='utf-8') as f:
        bossmst = json.load(f, object_pairs_hook=OrderedDict)
        ### ボスマスタレイアウト
        # bossmst[ボスIDのテキスト]={
        #     'intvl_min':分数,
        #     'pop_time':時刻'YYMM'のリスト,
        #     'duration_min':分数,
        #     'pop_rate':数値(0-100%),
        #     'pop_place':テキスト,
        #     'name':ボス名のリスト,
        #     'note':テキスト,
        #     'disable_flg':数値(0以外なら無効)
        # }
    # ボスマスタを返す
    return(bossmst)

### ボス名→ボスID変換用辞書変数の生成関数
# key:ボス名、値:ボスID
def get_bossname2id_dic(bossmst):
    bossname2id = {}
    # 引数のボスマスタ辞書変数の全キー(ボスID)を取得・処理
    for bid in bossmst.keys():
        # ボスIDに設定されているボス名リストを取得
        bnamelist = bossmst[bid].get('name')
        # ボス名を全処理
        for bname in bnamelist:
            # 各ボス名をキーとして、対応するボスIDを値に格納
            bossname2id[bname] = bid
    # 変換用辞書を返す
    return(bossname2id)
    
### LineageM用ボスbotクラス定義
class LmBBot(commands.Cog):
    
    # 初期処理
    def __init__(self, bot):
        # botオブジェクトを取得
        self.bot = bot
        
        # 既定のボスマスタをロード
        self.boss_mst = bossmst_load('./boss_mst.json')
        # ボス名→ID変換用辞書変数を取得
        self.boss_name2id = get_bossname2id_dic(self.boss_mst)
        
        # 起算日付
        self.base_date = datetime.datetime.strptime('2020/01/01', '%Y/%m/%d')
        # 最初の予告メッセージを含めた最大メッセージ送信回数
        self.max_msgsend = 3
    
#    # コマンド定義ping
#    @commands.command()
#    async def ping(self, ctx):
#        await ctx.send('pong!')
    
    # コマンド定義end
    @commands.command()
    async def end(self, ctx, arg1='', arg2='', arg3=''):
        # 引き数チェック
        if len(arg1) <= 0 or len(arg2) <= 0:
            return
        
        # ボス名チェック・ボスID取得
        bname = arg1
        bid = self.boss_name2id.get(bname)
        if bid == None:
            await ctx.send('不明なボス名')
            return
        
        # 時刻形式チェック（"HHMM"形式か）
        etimes = arg2
        errmsg = '不正な時刻指定(正=hhmm)'
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
            await ctx.send(errmsg)
            return
        
        # ボスマスタから各種情報取得
        boss_info = self.boss_mst[bid]
        intvl_h = boss_info['intvl_min'] // 60
        intvl_m = boss_info['intvl_min'] % 60
        rand = ''
        if boss_info['pop_rate'] < 100:
            rand = '(ランダム)'
        note = boss_info['note']
        
        if intvl_h > 0 or intvl_m > 0:
            poptime = edaytime + datetime.timedelta(hours=intvl_h, minutes=intvl_m)
            ch_id = ctx.channel.id
            end_time = int(edaytime.strftime("%y%m%d%H%M"))
            pop_time = int(poptime.strftime("%y%m%d%H%M"))
            addtext = arg3.strip()
            
            # 同一チャンネル同一ボスの既存の有効データを無効化(上書きフラグ=2)
            c.execute(
                "UPDATE bosspop SET DisableFlg = 2 WHERE ChID = ? AND BossID = ? AND MsgSendFlg = 0 AND DisableFlg = 0",
                (ch_id, bid)
            )
            
            # bosspopテーブルにpop情報を新規挿入
            c.execute(
                "INSERT INTO bosspop(ChID, BossID, EndTime, PopTime, AddText, MsgSendFlg, DisableFlg) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (ch_id, bid, end_time, pop_time, addtext, 0, 0)
            )
            
            ### pass後pop予測用のデータを更新
            # 起算日付(base_date)からのpoptimeの経過分数を計算
            pop_td = poptime - self.base_date
            popmin = int(pop_td.total_seconds() // 60)
            # 既存データの有無確認
            c.execute(
                "SELECT * FROM newestpop WHERE ChID = ? AND BossID = ?",
                (ch_id, bid)
            )
            # 取得件数判定
            res = c.fetchall()
            if len(res) < 1:
                # 既存データがなければ新規挿入
                c.execute(
                    "INSERT INTO newestpop(ChID, BossID, PopMin, IntvlMin, AddText, SendMsgCnt, DisableFlg) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (ch_id, bid, popmin, boss_info['intvl_min'], addtext, 0, 0)
                )
            else:
                # 既存データがあれば更新
                c.execute(
                    "UPDATE newestpop SET PopMin = ?, IntvlMin = ?, AddText = ?, SendMsgCnt = 0, DisableFlg = 0 WHERE ChID = ? AND BossID = ?",
                    (popmin, boss_info['intvl_min'], addtext, ch_id, bid)
                )
            
            # DBコミット
            conn.commit()
            # try:
            #     conn.commit()
            # except sqlite3.Error as er:
            #     print(er.message)
            
            # end報告元チャンネルへメッセージ返信
            addstr = ''
            if len(addtext) > 0:
                addstr = ' 備考:' + addtext
            # Msg送信
            await ctx.send(bname + ' Next Pop ' + poptime.strftime("%m/%d %H:%M") + rand + note + addstr)
            
        else:
        # ボスマスタのintvl_minが0の場合、何もしない
            return
    
    # ループ処理
    @tasks.loop(seconds=settings.LOOP_INTVL_SEC)
    async def fetch_popdata(self):
    ### POPデータフェッチ・予告(予測)メッセージ送信
        # bot管理チャンネルオブジェクトを取得
        ctrl_ch = self.bot.get_channel(settings.CTRL_CHANNEL_ID)
        
        # POPデータ取得期間を計算
        now = datetime.datetime.today()
        now_a10m = now + datetime.timedelta(minutes=10)
        
        # 起算日付(base_date)からの現在時刻とその10分後の経過分数を計算(pop予測処理用)
        now_td = now - self.base_date
        now_a10m_td = now_a10m - self.base_date
        now_min = int(now_td.total_seconds() // 60)
        now_a10m_min = int(now_a10m_td.total_seconds() // 60)
        
        #POPデータを取得
        ### bosspopテーブルレイアウト
        # [0]No_ INTEGER, [1]ChID INTEGER, [2]BossID TEXT,
        # [3]EndTime INTEGER, [4]PopTime INTEGER, [5]AddText TEXT,
        # [6]MsgSendFlg INTEGER, [7]DisableFlg INTEGER
        c.execute(
            "SELECT * FROM bosspop WHERE ? <= PopTime AND PopTime <= ? AND MsgSendFlg = 0 AND DisableFlg = 0",
            (int(now.strftime("%y%m%d%H%M")), int(now_a10m.strftime("%y%m%d%H%M")))
        )
        
        # 取得結果を処理
        res = c.fetchall()
        # print(len(res))
        for row in res:
            # print(row)
            if settings.DEBUG:
                # 管理ChへMsg送信
                await ctrl_ch.send('POPデータ取得: ' + str(row))
            
            # ボスマスタからボス情報取得
            bossinfo = self.boss_mst.get(row[2])
            
            # ボスマスタ取得成否判定
            if bossinfo == None:
            # マスタ取得失敗
                errmsg = 'RowNo.' + str(row[0]) + ':BossID[' + row[2] + '] is None.'
                print(errmsg)
                # 管理ChへMsg送信
                await ctrl_ch.send(errmsg)
                # 元レコードに無効フラグを立てる
                c.execute("UPDATE bosspop SET DisableFlg = 3 WHERE No_ = ?", (row[0],))
            
            else:
            # マスタ取得成功
                # 送信メッセージ構築
                msg_txt = '【ボス予告】もうすぐ ' + bossinfo['name'][0]
                msg_txt += ' がPOP! ' + str(row[4])[6:8] + ':' + str(row[4])[8:]
                if bossinfo['pop_rate'] < 100:
                    msg_txt += '(ランダム)'
                if bossinfo['note'] != '':
                    msg_txt += bossinfo['note']
                if bossinfo['pop_place'] != '':
                    msg_txt += ' ＠' + bossinfo['pop_place']
                if row[5] != '':
                    msg_txt += '\n備考:' + row[5]
                
                # 送信先チャンネルオブジェクトを取得
                send_channel = self.bot.get_channel(row[1])
                # POP予告メッセージ送信
                await send_channel.send(msg_txt)
                
                # 当該メッセージ元レコードの送信フラグを立てる
                c.execute(
                    "UPDATE bosspop SET MsgSendFlg = 1 WHERE No_ = ?",
                    (row[0],)
                )
                
                if settings.DEBUG:
                    # 管理ChへMsg送信
                    msg = 'sendmsg to [' + send_channel.name + ']:\n「' + msg_txt + '」'
                    await ctrl_ch.send(msg)
                
            # DBコミット
            conn.commit()
            
        ### pass後pop予測メッセージ処理
#        # debug
#        print(str(now_a10m) + ', ' + str(now_a10m_min))
#        c.execute("SELECT * FROM newestpop")
#        dres = c.fetchall()
#        for drow in dres:
#            print(drow)
#        # debug
        for i in range(1, self.max_msgsend):
            # pop予測対象データを取得
            ### newestpopテーブルレイアウト
            # [0]ChID INTEGER, [1]BossID TEXT, [2]PopMin INTEGER,
            # [3]IntvlMin INTEGER, [4]AddText TEXT,
            # [5]SendMsgCnt INTEGER, [6]DisableFlg INTEGER
            c.execute(
                "SELECT * FROM newestpop WHERE ? >= PopMin + IntvlMin * ? AND PopMin + IntvlMin * ? > ? AND ? > SendMsgCnt AND DisableFlg = 0",
                (now_a10m_min, i, i, now_min, i)
            )
            # 取得結果を処理
            res = c.fetchall()
            for row in res:
#                print(str(row))
                if settings.DEBUG:
                    # 管理ChへMsg送信
                    await ctrl_ch.send(str(i) + 'pass後POP予測データ取得:' + str(row))
                
                # ボスマスタからボス情報取得
                bossinfo = self.boss_mst.get(row[1])
                
                # ボスマスタ取得成否判定
                if bossinfo == None:
                # マスタ取得失敗
                    errmsg = 'BossID[' + row[1] + '] is None.'
                    print(errmsg)
                    # 管理ChへMsg送信
                    await ctrl_ch.send(errmsg)
                    
                    # 元レコードに無効フラグを立てる
                    c.execute("UPDATE newestpop SET DisableFlg = 3 WHERE ChID = ? AND BossID = ?", (row[0], row[1]))
                
                else:
                # マスタ取得成功
                    # pop時刻計算(起算日付に「PopMin + IntvlMin * i」分加算)
                    add_min = row[2] + row[3] * i
                    poptime = self.base_date + datetime.timedelta(minutes=add_min)
                    
                    # 送信メッセージ構築
                    msg_txt = '【ボス予測:' + str(i) + 'pass】もうすぐ ' + bossinfo['name'][0]
                    msg_txt += ' がPOP! ' + poptime.strftime("%H:%M")
                    if bossinfo['pop_rate'] < 100:
                        msg_txt += '(ランダム)'
                    if bossinfo['note'] != '':
                        msg_txt += bossinfo['note']
                    if bossinfo['pop_place'] != '':
                        msg_txt += ' ＠' + bossinfo['pop_place']
                    if row[4] != '':
                        msg_txt += '\n備考:' + row[4]
                    
                    # 送信先チャンネルオブジェクトを取得
                    send_channel = self.bot.get_channel(row[0])
                    # POP予測メッセージ送信
                    await send_channel.send(msg_txt)
                    
                    # 元レコードのメッセージ送信カウンターを更新
                    c.execute(
                        "UPDATE newestpop SET SendMsgCnt = ? WHERE ChID = ? AND BossID = ?",
                        (i, row[0], row[1])
                    )
                    
                # DBコミット
                conn.commit()

# Cogセットアップ処理
def setup(bot):
    # LmBBotクラスを追加
    bot.add_cog(LmBBot(bot))
    
    # POPデータフェッチループ処理を開始
    bbot = bot.get_cog('LmBBot')
    bbot.fetch_popdata.start()
    
    print('lmbbot:Setup Done.')
    