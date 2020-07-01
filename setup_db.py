import conf
from ref_bot.data_models import Data_Base
from sqlalchemy import create_engine

engine = create_engine(conf.ini_config.get('sqlalchemy', 'connection_string'))
Data_Base.metadata.create_all(engine)
