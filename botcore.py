import settings
#import configparser
#import datetime
#import sqlite3
#import json
#from collections import OrderedDict

# discordのライブラリをインポート
import discord
from discord.ext import commands
#from discord.ext import tasks

# botオブジェクトを生成
bot = commands.Bot(command_prefix='!')

### Bot管理クラス(コグ)定義
class BotMan(commands.Cog):

    # 初期処理
    def __init__(self, bot):
        # botオブジェクトを取得
        self.bot = bot
        
    # コマンド定義reload(管理)
    @commands.command()
    async def reload(self, ctx, arg1='all'):
        # 管理Chのみ有効
        if ctx.channel.id != settings.CTRL_CHANNEL_ID:
            return
        
        # 引数に応じて各エクステンションをリロード
        if arg1 == 'all':
            bot.reload_extension('lmbbot')
            await ctx.send('Bot Reloaded All Extensions.')
        elif arg1 == 'lmbbot':
            bot.reload_extension(arg1)
            await ctx.send('Bot Reloaded [' + arg1 + '] Extension.')
        else:
            await ctx.send(arg1 +' is Unknown Extension Name.')

# botが起動したとき
@bot.event
async def on_ready():
    # Bot管理コグを追加
    bot.add_cog(BotMan(bot))
    
    # 各機能エクステンションをロード
    bot.load_extension('lmbbot')    #ボスbot
    
    # bot管理チャンネルオブジェクトを取得
    ctrl_ch = bot.get_channel(settings.CTRL_CHANNEL_ID)
    # 管理Chへ起動Msg送信
    await ctrl_ch.send('bot start')
    # 起動
    print('寝てた')

# botの起動
bot.run(settings.TOKEN)
