import urllib.request

from ref_bot.data_models import Article, Tag
from bs4 import BeautifulSoup

def scrape_article(article):
    request = urllib.request.Request(article.url, data=None,
            headers={'User-Agent': 'ref_bot/1.0 discord/1.0'})

    
    try: 
        response = urllib.request.urlopen(request)
        body = response.read()
        soup = BeautifulSoup(body, 'html.parser')
        
        article.title = soup.title.string

        for meta in soup.find_all('meta', content=True):
            m_name = meta.get('name', '').lower()
            m_content = meta.get('content', '')

            if m_name == 'description':
                article.description = m_content 

            if m_name == 'keywords':
                for keyword in m_content.split(','):
                    article.tags.append(Tag(name=str(keyword).strip()))
        return True
    except:
        pass
    
    return False
