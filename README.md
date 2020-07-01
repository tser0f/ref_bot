# ref_bot
A simple discord bot for keeping track of article links on a discord server.

## Features
Automatic title, description, and tags scraping
![scraping](/screens/scraping.png)

Increasingly specific searching by title contents, tags
![find1](/screens/find1.png)
![find2](/screens/find2.png)

Idk :d

## Requirements
This project uses python 3, [discord.py](https://github.com/Rapptz/discord.py), and [sqlalchemy](https://www.sqlalchemy.org).
You can check your python version by running `python --version`.

You can install discord.py and sqlalchemy with pip : 
```
python3 -m pip install -U discord.py
python3 -m pip install -U sqlalchemy
```

## Usage/installation
1. Create a copy of config.ini named config.dev.ini. (you can change the naming in conf.py)
2. Put your discord token next to `token=` and change any other options you'd like
3. Run `python3 setup_db.py`, this will create the database for the bot.
4. Run `python3 ref_bot.py`. You should see the following if the bot is running correctly:
```
ref_bot extension loading.
your_bot_name has connected to Discord!
```

## Usage on discord
# Commands : 
* `!ref add <article_url> <tags...>` - Adds a new article
* `!ref find <keywords...>` - Searches for an article posted in the current channel using the specified keywords.
* `!ref find_all <keywords...>` - Same as !ref find but posted anywhere
* `!ref id <id>` - Gets the article with specified id
* `!ref delete <id>` - Removes the article with specified id
* `!ref tag <id> <+tag -tag...>` - Adds tags specified with `+` and removes tags specified with `-`
* `!ref update <id>` - Automatically update the article from the url

# Examples : 
* `!ref add https://site.com/articles/23 hashing crypto`
* `!ref find hash`
* `!ref tag 5 +passwords +practice -dolan`
* `!ref delete 8`
