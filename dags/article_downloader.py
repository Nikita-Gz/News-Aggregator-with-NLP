from DBTalker import get_website_db_session, query_fetched_articles_and_fetching_data
from website_db_mapper import CurrentlyFetchedArticle, Article
from newspaper import Article as ArticleDownloader
from network_stuff import get_newspaper3k_config
import datetime
import logging

# turn this into a different task maybe?
def check_is_article_loaded(articles):
    """
    Gets a list of articles from DB, returns a boolean list, eachelement tells if article is already loaded
    """
    return [False] * len(articles)

def get_article_from_website_db(fetcher_db_article):
    raise NotImplementedError('get_article_from_website_db')

def download_article_html(url):
    # TODO: stream article response in bits, until it overflows over the maximum size
    downloaded_article = ArticleDownloader(url, config=get_newspaper3k_config())
    downloaded_article.download()

    html = downloaded_article.html
    if html is None:
        raise Exception(f'Could not download html from article {url}')

    return html

def download_articles_html():
    session = get_website_db_session()
    articles_and_their_fetching_data = query_fetched_articles_and_fetching_data(session)
    row_count = articles_and_their_fetching_data.count()
    for i, (article, fetching_data) in enumerate(articles_and_their_fetching_data):
        if fetching_data.was_already_downloaded:
            logging.info(f'Article {article.url} is already downloaded on {article.download_date} ({i+1} out of {row_count})')
            continue

        try:
            logging.info(f'Downloading article {article.url} ({i+1} out of {row_count})')
            html = download_article_html(article.url)
        except Exception as e:
            logging.error(f'Exception when downloading article {article.url}, deleting it from fetching list, e={repr(e)}')
            session.delete(fetching_data)
            continue
        
        article.html = html
        article.download_date = datetime.datetime.now()

    session.commit()