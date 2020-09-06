#discordのライブラリをインポート
import discord
#自分のトークンにしてね
TOKEN = 'NzQ5NDkzNjMzNTQ3NTAxNTY5.X0syVw.Zh95SnG5-FVQUPy5vz_GeNmFKH0'
CHANNEL_ID = 751985875868581888

# 接続に必要なオブジェクトを作る
client = discord.Client()

async def send_msg():
    channel = client.get_channel(CHANNEL_ID)
    await channel.send('hello')
    client.close 

#BOTが起動したとき
@client.event
async def on_ready():
    await send_msg()

#BOTの起動
client.run(TOKEN)
