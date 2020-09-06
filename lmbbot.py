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
    now = datetime.datetime.today()
    # コマンド解釈
    s_msg_list = message.content.split(' ') #半角スペースでメッセージを分割しリストに格納
    if s_msg_list[0] == '/bend':
        if s_msg_list[1] == 'てきこ':
            await message.channel.send('てきこend')
        elif s_msg_list[1] == 'カスパ':
            poptime = now + datetime.timedelta(hours=2)
            await message.channel.send('カスパ Next Pop ' + poptime.strftime("%Y/%m/%d %H:%M"))
        else:
            return
    else:
        return

#BOTの起動
client.run(TOKEN)
