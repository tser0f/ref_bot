# ref bot.py
import discord
from discord.ext import commands
import conf

bot = commands.Bot(command_prefix=conf.ini_config.get('discord', 'command_prefix') + ' ')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command()
async def reload(ctx):
    if ctx.message.author.guild_permissions.administrator:
        bot.reload_extension('ref_bot.extension')
        await ctx.send('Reloaded.')
    else:
        await ctx.send('Access Denied.')

bot.load_extension('ref_bot.extension')
bot.run(conf.ini_config.get('discord', 'token'))
