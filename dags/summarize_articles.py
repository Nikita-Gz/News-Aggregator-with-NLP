from DBTalker import get_website_db_session
from website_db_mapper import Article, CurrentlyFetchedArticle
import gensim
import logging

def summarize_articles():
  session = get_website_db_session()
  articles_and_their_fetching_data = session.query(Article, CurrentlyFetchedArticle).filter(Article.id==CurrentlyFetchedArticle.article_id)
  row_count = articles_and_their_fetching_data.count()
  for i, (article, fetching_data) in enumerate(articles_and_their_fetching_data):
    if fetching_data.was_already_downloaded:
      logging.info(f'Article {article.url} is already downloaded on {article.download_date} ({i+1} out of {row_count}), skipping summarization')
      continue

    logging.info(f'Summarizing article {article.url} ({i+1} out of row_count)')
    try:
      summary = gensim.summarization.summarize(article.text, word_count=200)
    except Exception as e:
      logging.error(f'Failed summarizing, skipping, e={repr(e)}')
      continue

    article.summary = summary
  session.commit()
