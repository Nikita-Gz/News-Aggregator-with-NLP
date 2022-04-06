from DBTalker import get_website_db_session, query_fetched_articles_and_fetching_data
from website_db_mapper import Article, CurrentlyFetchedArticle
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from DBTalker import get_website_db_session
import nltk
import logging
import pickle
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('omw-1.4')

class LemmaTokenizer:
  ignore_tokens = [',', '.', ';', ':', '"', '``', "''", '`']
  def __init__(self):
    self.wnl = WordNetLemmatizer()
  def __call__(self, doc):
    return [self.wnl.lemmatize(t) for t in word_tokenize(doc) if t not in self.ignore_tokens]


def compute_article_tfidf():
  session = get_website_db_session()
  tokenizer = LemmaTokenizer()
  stop_words = set(stopwords.words('english')) 
  token_stopwords = tokenizer(' '.join(stop_words))
  vectorizer = TfidfVectorizer(tokenizer=tokenizer, stop_words=token_stopwords)

  logging.info(f'Computing TF-IDF')
  text_to_process = []
  articles_and_their_fetching_data = query_fetched_articles_and_fetching_data(session)
  row_count = articles_and_their_fetching_data.count()
  for i, (article, fetching_data) in enumerate(articles_and_their_fetching_data):
    if fetching_data.was_already_downloaded:
      logging.info(f'Article {article.url} ({i+1}\'th out of {row_count}) is already downloaded, skipping getting tf-idf')
      continue
    text_to_process.append(article.text)

  tf_idf_results = vectorizer.fit_transform(text_to_process)
  logging.info(f'Saving TF-IDF')
  for article_i, article_fetching_data in enumerate(fetching_data):
    article_fetching_data.tfidf = pickle.dumps(tf_idf_results[article_i])

  session.commit()

