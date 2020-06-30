import ref_bot.cog.articlerefs
import importlib

from configparser import ConfigParser
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

bot_config = ConfigParser()
bot_config.read('config.dev.ini')


@commands.command()
async def hello(ctx):
    await ctx.send('Hello {0.display_name}.'.format(ctx.author))

def setup_dbsession():
    engine = create_engine(bot_config.get('sqlalchemy', 'connection_string'))    
    
    sessionm = sessionmaker()
    sessionm.configure(bind=engine)
    return sessionm()

def setup(bot):
    print('I am being loaded!!! o.O!')

    dbsession = setup_dbsession()
    importlib.reload(ref_bot.cog.articlerefs)
    bot.add_cog(ref_bot.cog.articlerefs.ArticleRefs(bot, dbsession))

    #bot.add_command(hello)

def teardown(bot):
    print('I am being unloaded!')
    bot.remove_cog('ArticleRefs')
