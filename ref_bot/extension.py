import ref_bot.cog.articlerefs
import importlib

from configparser import ConfigParser
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

bot_config = ConfigParser()
bot_config.read('config.dev.ini')


def setup_dbsession():
    engine = create_engine(bot_config.get('sqlalchemy', 'connection_string'))    
    
    sessionm = sessionmaker()
    sessionm.configure(bind=engine)
    return sessionm()

def setup(bot):
    print('ref_bot extension loading.')

    dbsession = setup_dbsession()
    importlib.reload(ref_bot.cog.articlerefs)
    bot.remove_command('help')
    bot.add_cog(ref_bot.cog.articlerefs.ArticleRefs(bot, dbsession))

    #bot.add_command(hello)

def teardown(bot):
    print('ref_bot extension unloading')
    bot.remove_cog('ArticleRefs')
