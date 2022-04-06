from sqlalchemy.orm import Session
from datetime import datetime
from newspaper import Source as NewsSourceParser
import logging

from DBTalker import get_website_db_session
from website_db_mapper import Source, Article, CurrentlyFetchedArticle, UserBeingFetchedFor, UserSelectedSource
from network_stuff import get_newspaper3k_config


def get_article_if_exists(session: Session, url: str):
    return session.query(Article).filter(Article.url==url).first()

def fetch_article_urls():
    session = get_website_db_session()
    total_articles = 0
    failed_counter = 0

    # for each source selected by users who are being fetched for...
    fetched_users = session.query(UserBeingFetchedFor.user_id).subquery()
    source_ids = session.query(UserSelectedSource.source_id).filter(UserSelectedSource.user_id.in_(fetched_users)).subquery()
    sources = session.query(Source).filter(Source.id.in_(source_ids))
    for source in sources:
        source_url = source.url
        
        # TODO: stream source response in small bits, until it overflows over the maximum size
        try:
            logging.info(f'Downloading source {source_url}')
            built_source = NewsSourceParser(source_url, config=get_newspaper3k_config(), memoize_articles=False)
            built_source.build()
        except Exception as e:
            logging.error(f'Exception when building source {source_url}, e={repr(e)}')
            failed_counter += 1
            continue
        
        articles_limit_from_source = 50
        for article_object in built_source.articles[:articles_limit_from_source]:
            # get article object if it was already downloaded before and is stored in DB
            # create new article object if there isn't one in the DB already
            was_article_already_downloaded = True
            article_in_db = get_article_if_exists(session, article_object.url)
            if article_in_db is None:
                was_article_already_downloaded = False
                article_in_db = Article(url=article_object.url, source_id=source.id,
                html='',
                title='',
                text='',
                summary='',
                main_image='',
                publish_date='')
                session.add(article_in_db)
                session.commit()

            fetching_assignment = CurrentlyFetchedArticle(article_id=article_in_db.id, was_already_downloaded=was_article_already_downloaded)
            session.add(fetching_assignment)
            session.commit()
            total_articles += 1
        logging.info(f'Fetched {len(built_source.articles)} article urls from source {source_url}')
    logging.info(f'Fetched {total_articles} article urls in total, skipped {failed_counter} sources')
