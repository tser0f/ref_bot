
from configparser import ConfigParser
from ref_bot.data_models import Data_Base
from sqlalchemy import create_engine

bot_config = ConfigParser()
bot_config.read('config.dev.ini')

engine = create_engine(bot_config.get('sqlalchemy', 'connection_string'))
Data_Base.metadata.create_all(engine)
