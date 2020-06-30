# ref bot.py
from configparser import ConfigParser
import discord
from discord.ext import commands

# read in the bot_config
bot_config = ConfigParser()
bot_config.read('config.dev.ini')
bot = commands.Bot(command_prefix=bot_config.get('discord', 'command_prefix') + ' ')

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
bot.run(bot_config.get('discord', 'token'))
