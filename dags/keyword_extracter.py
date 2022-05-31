from DBTalker import get_website_db_session
from website_db_mapper import Article, ArticleKeyword, CurrentlyFetchedArticle
from nltk.stem import WordNetLemmatizer
import gensim
import logging

def lemmatize_keywords(key_words):
  wordnet_lemmatizer = WordNetLemmatizer()
  return list([wordnet_lemmatizer.lemmatize(keyword) for keyword in key_words])

def extract_article_keywords():
  session = get_website_db_session()
  articles_and_their_fetching_data = session.query(Article, CurrentlyFetchedArticle).filter(Article.id==CurrentlyFetchedArticle.article_id)
  row_count = articles_and_their_fetching_data.count()
  for i, (article, fetching_data) in enumerate(articles_and_their_fetching_data):
    if fetching_data.was_already_downloaded:
      logging.info(f'Article {article.url} is already downloaded on {article.download_date} ({i+1} out of {row_count}), skipping keyword extraction')
      continue

    logging.info(f'Extracting article {article.url} ({i}) keywords')
    try:
      keywords = gensim.summarization.keywords(article.text, words=6).split('\n')
      lemmatized_keywords = lemmatize_keywords(keywords)
    except Exception as e:
      logging.error(f'Failed extracting keywords, skipping, e={repr(e)}')
      continue

    for keyword, lemmatized_version in zip(keywords, lemmatized_keywords):
      logging.info(f'Saving keyword {keyword} (lemmatized: lemmatized_version)')
      db_keyword = ArticleKeyword(article_id=article.id, text=keyword, lemmatized_text=lemmatized_version)
      session.add(db_keyword)
  session.commit()
