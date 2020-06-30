import discord
from discord.ext import commands
from ref_bot.data_models import Article, Tag
from ref_bot.article_scraper import scrape_article

class ArticleRefs(commands.Cog):
    def __init__(self, bot, db_session):
        self.bot = bot
        self.db_session = db_session
        self._last_member = None

    def generate_embed(self, article):
            emb = discord.Embed(title=article.title, description=article.description, url=article.url)
            #emb.set_author(name=article.discord_user_id)

            emb.add_field(name="Id", value=article.id)
            emb.add_field(name="Tags", value=[str(tag.name) for tag in article.tags])
            emb.add_field(name="Added by", value="<@{0}>".format(article.discord_user_id))
            emb.add_field(name="Channel", value="<#{0}>".format(article.discord_channel_id))
            
            emb.add_field(name="Original request", value="[Link!](https://discordapp.com/channels/{0.discord_guild_id}/{0.discord_channel_id}/{0.discord_message_id})".format(article))
            
            emb.set_footer(text="Created: {0.created} | Last updated: {0.last_updated}".format(article))
            return emb

    def resolve_existing_tags(self, article):
        resolved_tags = []
        for tag_i in set(article.tags):
            tag_db_obj = self.db_session.query(Tag).filter(Tag.name==tag_i.name).first()

            if tag_db_obj is None:
                self.db_session.add(tag_i)
                resolved_tags.append(tag_i)
            else:
                resolved_tags.append(tag_db_obj)

        article.tags = resolved_tags

    @commands.command(name="help")
    async def show_help(self, ctx):

        emb = discord.Embed(title="Ref bot help",
                description="""Commands : 
                `!ref add <article_url> <tags...>` - Adds a new article
                `!ref find <id|keywords...>` - Searches for an article posted in the current channel using the specified keywords.
                `!ref find_all <id|keywords...>` - Same as !ref find but posted anywhere
                `!ref id <id>` - Gets the article with specified id
                `!ref delete <id>` - Removes the article with specified id
                `!ref tag <id> <+tag -tag...>` - Adds tags specified with `+` and removes tags specified with `-`
                `!ref update <id> - Automatically update the article from the url

                Examples : 
                `!ref add https://site.com/articles/23 hashing crypto`
                `!ref find hash`
                `!ref tag 5 +passwords +practice -dolan`
                `!ref delete 8`
                """)
        await ctx.send(embed=emb)

    @commands.command(name="add")
    async def add_article(self, ctx, url, *tags):
        url = url.strip()
        if url[0] == '<' and url[-1] == '>':
            url = url[1:-1]

        article_obj = self.db_session.query(Article).filter_by(url=url).first()

        if article_obj is None:
            article_obj = Article(url=url, 
                discord_user_id=ctx.author.id, discord_channel_id=ctx.message.channel.id, discord_message_id=ctx.message.id,
                discord_guild_id=ctx.guild.id)
      
            for tag in tags:
                article_obj.tags.append(Tag(name=tag))

            if scrape_article(article_obj):
                self.resolve_existing_tags(article_obj)
                self.db_session.add(article_obj)
                self.db_session.commit()

                await ctx.send('Article added successfully!', embed=self.generate_embed(article_obj))
            else:
                await ctx.send('Error! Could not add the article')
        else:
            await ctx.send('Article already exists!', embed=self.generate_embed(article_obj))
    

    def find_by_id(self, query, id):
        return query.filter(Article.id==id)

    def find_by_channel(self, query, channel_id):
        return query.filter(Article.discord_channel_id==channel_id)

    def find_like_tag(self, query, tag):
        return query.filter(Article.tags.any(Tag.name.like('%{0}%'.format(tag))))

    def find_like_title(self, query, title):
        return query.filter(Article.title.like('%{0}%'.format(title)))
    
    def find_by_keywords(self, query, keywords):
        articles_found = query 
        articles_narrowed_flag = False

        for keyword in keywords:
            articles_found_new = None

            if keyword.isdigit(): #keyword is probably id
                articles_found_new = self.find_by_id(articles_found, keyword) 

            if articles_found_new is None or articles_found_new.count() == 0:
                articles_found_new = self.find_like_tag(articles_found, keyword) 
            
            if articles_found_new is None or articles_found_new.count() == 0: #nothing found by tags
                articles_found_new = self.find_like_title(articles_found, keyword)
            
            if articles_found_new is not None and articles_found_new.count() != 0: #search narrowed down results, but not down to nothing
                articles_found = articles_found_new
                articles_narrowed_flag = True
        
        if articles_narrowed_flag: 
            return articles_found
        
        return None

    @commands.command(name="find_all")
    async def find_article(self, ctx, *keywords):
        articles_found = self.find_by_keywords(self.db_session.query(Article), keywords)
    
        if articles_found is not None:
            for article in articles_found:
                await ctx.send('Found!', embed=self.generate_embed(article))

        else:
            await ctx.send('Could not find your article. :(')

    @commands.command(name="find")
    async def find_article_channel(self, ctx, *keywords):
        articles_found = self.find_by_keywords(self.db_session.query(Article), keywords)
    
        if articles_found is not None:
            articles_found = self.find_by_channel(articles_found, ctx.message.channel.id)
            
        if articles_found is not None and articles_found.count() != 0:
            for article in articles_found:
                await ctx.send('Found!', embed=self.generate_embed(article))

        else:
            await ctx.send('Could not find your article. :(')

    @commands.command(name="id")
    async def find_article_id(self, ctx, id):
        article = self.find_by_id(self.db_session.query(Article), id).first()

        if article is not None:
            await ctx.send('Found!', embed=self.generate_embed(article))
        else:
            await ctx.send('Could not find specified article.')


    @commands.command(name="delete")
    async def delete_article(self, ctx, id):
        article = self.find_by_id(self.db_session.query(Article), id).first()

        if article is not None:
            if ctx.author.id == article.discord_user_id or discord.Permissions.administrator(ctx.author.permissions_in(ctx.message.channel)):
                self.db_session.delete(article)
                self.db_session.commit()
                await ctx.send('Sucessfully deleted article!')
            else:
                await ctx.send('Only <@{0}> can delete this article!'.format(article.discord_user_id))
        else:
            await ctx.send('Could not find the specified article.')

    @commands.command(name="tag", aliases=["tags"])
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

            self.resolve_existing_tags(article)
            self.db_session.commit()
            await ctx.send('Tags updated!', embed=self.generate_embed(article))

        else:
            await ctx.send('Could not find the specified article.')

    @commands.command(name="update")
    async def update_article(self, ctx, id):
        article = self.find_by_id(self.db_session.query(Article), id).first()

        if article is not None:
            if scrape_article(article):
                self.resolve_existing_tags(article)
                self.db_session.commit()

                await ctx.send('Article has been autoupdated!', embed=self.generate_embed(article))
            else:
                await ctx.send('Could not open the article for updating!')

        else:
            await ctx.send('Could not find the specified article.')
