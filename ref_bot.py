# ref bot.py
import discord
from discord.ext import commands
import conf
import logging

#setup logging
logger = logging.getLogger('discord')
logger.setLevel(conf.ini_config.get('discord', 'log_level'))
handler = logging.FileHandler(filename=conf.ini_config.get('discord', 'log_filename'), encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

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
