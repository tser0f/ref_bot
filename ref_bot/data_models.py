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

class ArticleTag(Data_Base):
    __tablename__ = 'article_tags'
    article_id = Column(Integer, ForeignKey('articles.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('tags.id'), primary_key=True)

class Article(Data_Base):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    url = Column(String(250))
    
    tags = relationship(Tag, secondary='article_tags', back_populates="articles")
    
    title = Column(String(250))
    description = Column(String(250))
    created = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), default=datetime.datetime.now, onupdate=datetime.datetime.now) 
   
    owners = relationship('ArticleOwner', back_populates="article")
    
    def resolve_existing_tags(self, db_session):
        resolved_tags = []
        for tag_i in set(self.tags):
            tag_db_obj = db_session.query(Tag).filter(Tag.name==tag_i.name).first()

            if tag_db_obj is None:
                db_session.add(tag_i)
                resolved_tags.append(tag_i)
            else:
                resolved_tags.append(tag_db_obj)

        self.tags = resolved_tags


    def find_owners(self, article_owner):
        out_owners = []
        for owner in self.owners:
            
            match = True
            if article_owner.discord_user_id:
                match = match and (owner.discord_user_id == article_owner.discord_user_id)

            if article_owner.discord_guild_id:
                match = match and (owner.discord_guild_id == article_owner.discord_guild_id)
                
            if article_owner.discord_channel_id:
                match = match and (owner.discord_channel_id == article_owner.discord_channel_id)

            if match:
                out_owners.append(owner)

        return out_owners
    #discord_guild_id = Column(Integer)
    #discord_message_id = Column(Integer)
    #discord_user_id = Column(Integer)
    #discord_channel_id = Column(Integer)

class ArticleOwner(Data_Base):
    __tablename__ = 'article_owners'
    article_id = Column(Integer, ForeignKey('articles.id'), primary_key=True)
    discord_user_id = Column(Integer, primary_key=True)
    discord_channel_id = Column(Integer, primary_key=True)
    discord_message_id = Column(Integer, primary_key=True)
    discord_guild_id = Column(Integer, primary_key=True)

    article = relationship(Article, back_populates="owners")



