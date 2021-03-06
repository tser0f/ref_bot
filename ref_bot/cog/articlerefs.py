import discord
from discord.ext import commands
from ref_bot.data_models import Article, Tag, ArticleOwner
from ref_bot.article_scraper import scrape_article

class ArticleRefs(commands.Cog):
    def __init__(self, bot, db_session):
        self.bot = bot
        self.db_session = db_session
        self._last_member = None

    def generate_embed(self, article):
            emb = discord.Embed(title=article.title, description=article.description, url=article.url)
            #emb.set_author(name=article.discord_user_id)

            emb.add_field(name='Id', value=article.id)
            emb.add_field(name='Tags', value=', '.join([str(tag.name) for tag in article.tags]))
            #emb.add_field(name='Added by', value='<@{0}>'.format(article.discord_user_id))
            #emb.add_field(name='Channel', value='<#{0}>'.format(article.discord_channel_id))
            
            #emb.add_field(name='Original request', value='[Link!](https://discordapp.com/channels/{0.discord_guild_id}/{0.discord_channel_id}/{0.discord_message_id})'.format(article))
            
            emb.set_footer(text='Created: {0.created} | Last updated: {0.last_updated}'.format(article))
            return emb

    @commands.command(name='help')
    async def show_help(self, ctx):

        emb = discord.Embed(title='Ref bot help',
                description='''Commands : 
                `!ref add <article_url> <tags...>` - Adds a new article
                `!ref find <keywords...>` - Searches for an article posted in the current channel using the specified keywords.
                `!ref find_all <keywords...>` - Same as !ref find but posted anywhere
                `!ref id <id>` - Gets the article with specified id
                `!ref delete <id>` - Removes the article with specified id
                `!ref tag <id> <+tag -tag...>` - Adds tags specified with `+` and removes tags specified with `-`
                `!ref update <id>` - Automatically update the article from the url
                `!ref owners <id>` - shows the users that added the articles to the channel

                Examples : 
                `!ref add https://site.com/articles/23 hashing crypto`
                `!ref find hash`
                `!ref tag 5 +passwords +practice -dolan`
                `!ref delete 8`
                ''')
        await ctx.send(embed=emb)

    @commands.command(name='add')
    async def add_article(self, ctx, url, *tags):
        url = url.strip()
        if url[0] == '<' and url[-1] == '>':
            url = url[1:-1]
        
        article_query = self.db_session.query(Article).filter_by(url=url)
        article_obj = article_query.first()
        is_new = False
        owners = []

        if article_obj is None:
            article_obj = Article(url=url) #, 
            is_new = True
            for tag in tags:
                article_obj.tags.append(Tag(name=tag))

            if scrape_article(article_obj) == False:
                await ctx.send('Error! Could not add the article')
                return
        else:
            owners = article_obj.find_owners(ArticleOwner(discord_channel_id=ctx.message.channel.id, discord_guild_id=ctx.guild.id))
        
        if len(owners) == 0:
            article_obj.owners.append(ArticleOwner(discord_user_id=ctx.author.id, discord_channel_id=ctx.message.channel.id, discord_message_id=ctx.message.id, discord_guild_id=ctx.guild.id))
        elif len(owners) == 1:
            await ctx.send('Article has already been added in this channel. It is currently owned by <@{0.discord_user_id}>.'.format(owners[0]))
            return
        else:
            await ctx.send('WARNING: Article {0} has multiple({1}) owners in this channel!'.format(article_obj.id, len(owners)))
            return

        article_obj.resolve_existing_tags(self.db_session)
        if is_new:
            self.db_session.add(article_obj)

        self.db_session.commit()

        await ctx.send('Article added successfully!', embed=self.generate_embed(article_obj))
    

    def find_by_id(self, query, id):
        return query.filter(Article.id==id)

    def find_by_channel(self, query, channel_id):
        return query.filter(Article.owners.any(ArticleOwner.discord_channel_id==channel_id))

    def find_like_tag(self, query, tag):
        return query.filter(Article.tags.any(Tag.name.like('%{0}%'.format(tag))))

    def find_like_title(self, query, title):
        return query.filter(Article.title.like('%{0}%'.format(title)))
    
    def find_by_keywords(self, query, keywords):
        articles_found = None

        for keyword in keywords:
            if articles_found is None or len(articles_found) == 0:
                articles_found = query.filter(Article.tags.any(Tag.name.like('%{0}%'.format(keyword))) | Article.title.like('%{0}%'.format(keyword))).all()
            if len(articles_found) == 1: #only one result is left, cannot get less anyway
                return articles_found
            elif len(articles_found) > 1:
                articles_tag = []
                articles_title = []

                for article in articles_found:
                    for tag in article.tags:
                        if keyword in tag.name:
                            articles_tag.append(article)
                            break

                    if keyword in article.title:
                        articles_title.append(article)

                if len(articles_tag) >= len(articles_title): #set whichever result set is biggest
                    articles_found = articles_tag
                elif len(articles_tag) < len(articles_title):
                    articles_found = articles_title

        return articles_found

    @commands.command(name='find_all')
    async def find_article(self, ctx, *keywords):
        articles_found = self.find_by_keywords(self.db_session.query(Article), keywords)
    
        if articles_found is not None:
            for article in articles_found:
                await ctx.send('Found!', embed=self.generate_embed(article))

        else:
            await ctx.send('Could not find your article. :(')

    @commands.command(name='find')
    async def find_article_channel(self, ctx, *keywords):
        articles_found = self.find_by_keywords(self.db_session.query(Article), keywords)
        articles_sent = False

        if articles_found is not None and len(articles_found) != 0:
            for article in articles_found:
                if any(owner.discord_channel_id == ctx.message.channel.id for owner in article.owners): 
                    articles_sent = True
                    await ctx.send('Found!', embed=self.generate_embed(article))

        if articles_sent == False:
            await ctx.send('Could not find your article. :(')

    @commands.command(name='id')
    async def find_article_id(self, ctx, id):
        article = self.find_by_id(self.db_session.query(Article), id).first()

        if article is not None:
            await ctx.send('Found!', embed=self.generate_embed(article))
        else:
            await ctx.send('Could not find specified article.')


    @commands.command(name='delete')
    async def delete_article(self, ctx, id):
        article_query = self.find_by_id(self.db_session.query(Article), id)
        article = article_query.first()

        if article is not None:
            #owner = article_query.filter(Article.owners.any((ArticleOwner.discord_channel_id==ctx.message.channel.id) & (ArticleOwner.discord_guild_id==ctx.guild.id))).first().owners[0]
            owners = article.find_owners(ArticleOwner(discord_channel_id=ctx.message.channel.id, discord_guild_id=ctx.guild.id, discord_user_id=ctx.author.id))
            if len(owners) > 1 or ctx.message.author.guild_permissions.administrator:
                
                for owner in owners:
                    self.db_session.delete(owner)
                
                if len(article.owners) == len(owners):
                    self.db_session.delete(article)

                self.db_session.commit()
                await ctx.send('Sucessfully deleted article!')
            else:
                await ctx.send('Only <@{0}> can delete this article!'.format(article.discord_user_id))
        else:
            await ctx.send('Could not find the specified article.')

    @commands.command(name='tag', aliases=['tags'])
    async def tag_article(self, ctx, id, *tags):
        article = self.find_by_id(self.db_session.query(Article), id).first()

        if article is not None:
            tags_add = []
            tags_remove = []

            for tag in tags:
                if tag[0] == '-':
                    tags_remove.append(tag[1:])
                elif tag[0] == '+':
                    article.tags.append(Tag(name=tag[1:]))
                else:
                    article.tags.append(Tag(name=tag))

            for existing_tag in article.tags:
                if existing_tag.name in tags_remove:
                    article.tags.remove(existing_tag)

            article.resolve_existing_tags(self.db_session)
            self.db_session.commit()
            await ctx.send('Tags updated!', embed=self.generate_embed(article))

        else:
            await ctx.send('Could not find the specified article.')

    @commands.command(name='update')
    async def update_article(self, ctx, id):
        article = self.find_by_id(self.db_session.query(Article), id).first()

        if article is not None:
            if scrape_article(article):
                article.resolve_existing_tags(self.db_session)
                self.db_session.commit()

                await ctx.send('Article has been autoupdated!', embed=self.generate_embed(article))
            else:
                await ctx.send('Could not open the article for updating!')

        else:
            await ctx.send('Could not find the specified article.')


    @commands.command(name='owner', aliases=['owners'])
    async def list_owners(self, ctx, id):
        article = self.find_by_id(self.db_session.query(Article), id).first()

        if article is not None:
            emb = discord.Embed(title=article.title)

            owners = article.owners_without_personal()
            owners_mentions = '\r\n'.join(['<@{0.discord_user_id}>'.format(owner) for owner in owners])
            owners_channels = '\r\n'.join(['<#{0.discord_channel_id}>'.format(owner) for owner in owners])

            emb.add_field(name='Owners', value=owners_mentions)
            emb.add_field(name='Channels', value=owners_channels)
            await ctx.send('Article owners list : ', embed=emb)
