from DBTalker import get_website_db_session
from website_db_mapper import Article, CurrentlyFetchedArticle
from newspaper import Article as ArticleParser
import logging

def parse_article(article_in_db):
  article_parser = ArticleParser(article_in_db.url)

  # doesen't actually download article again, just sets parser's html to the supplied article_in_db.html
  article_parser.download(article_in_db.html)

  article_parser.parse()

  if article_parser.title is None or article_parser.title == '':
    raise Exception('Article had empty title')
  if article_parser.text is None or article_parser.text == '':
    raise Exception('Article had empty text')

  article_in_db.title = article_parser.title
  article_in_db.text = article_parser.text

  if article_parser.publish_date is None:
    article_in_db.publish_date = ''
  else:
    article_in_db.publish_date = article_parser.publish_date

  # try setting parsed top_image as the image, otherwise set the first image in the article as the top image
  if article_parser.top_image is not None and article_parser.top_image != '':
    article_in_db.main_image = article_parser.top_image
  elif isinstance(article_parser.images, list) and len(article_parser.images) > 0:
    article_in_db.main_image = article_parser.images[0]

def parse_articles():
  session = get_website_db_session()
  articles_and_their_fetching_data = session.query(Article, CurrentlyFetchedArticle).filter(Article.id==CurrentlyFetchedArticle.article_id)
  row_count = articles_and_their_fetching_data.count()
  for i, (article, fetching_data) in enumerate(articles_and_their_fetching_data):
    if fetching_data.was_already_downloaded:
      logging.info(f'Article {article.url} ({i+1}\'th out of {row_count}) is already downloaded, skipping parsing')
      continue

    try:
      logging.info(f'Parsing article {article.url} ({i+1}\'th out of {row_count})')
      parse_article(article)
    except Exception as e:
      logging.error(f'Failed parsing article {article.url}, deleting it from fetching list, e={repr(e)} \n {str(e)}')
      session.delete(fetching_data)
      continue
  session.commit()