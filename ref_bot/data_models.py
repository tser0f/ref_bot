import datetime
from sqlalchemy import Table, Column, ForeignKey, Integer, String, DateTime, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Data_Base = declarative_base()

class Tag(Data_Base):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    articles = relationship("Article", secondary='article_tags', back_populates="tags")

article_tag_association = Table('article_tags', Data_Base.metadata,
        Column('article_id', Integer, ForeignKey('articles.id')),
        Column('tag_id', Integer, ForeignKey('tags.id'))
        )
#class ArticleTag(Data_Base):
    #__tablename__ = 'article_tags'
    #article_id = Column(Integer, ForeignKey('articles.id'))
    #tag_id = Column(Integer, ForeignKey('tags.id'))
    #__table_args__ = (
    #        PrimaryKeyConstraint('article_id'),
    #        {},
    #    )


class Article(Data_Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    url = Column(String(250))
    
    tags = relationship(Tag, secondary='article_tags', back_populates="articles")
    
    title = Column(String(250))
    description = Column(String(250))
    created = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now) 
    discord_guild_id = Column(Integer)
    discord_message_id = Column(Integer)
    discord_user_id = Column(Integer)
    discord_channel_id = Column(Integer)
