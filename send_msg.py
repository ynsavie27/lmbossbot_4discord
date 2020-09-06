#discordのライブラリをインポート
import discord
#自分のトークンにしてね
TOKEN = 'NzQ5NDkzNjMzNTQ3NTAxNTY5.X0syVw.Zh95SnG5-FVQUPy5vz_GeNmFKH0'

# 接続に必要なオブジェクトを作る
client = discord.Client()

gld = client.get_guild('748728816364421171')

#BOTが起動したとき
@client.event
async def on_ready():
    print('寝てた')
    print(client.guilds)
    print(gld.text_channels)
    

#BOTの起動
client.run(TOKEN)
