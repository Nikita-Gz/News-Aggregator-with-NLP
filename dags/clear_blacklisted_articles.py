from DBTalker import get_website_db_session
from website_db_mapper import Article, User, RecommendationServing, UserBeingFetchedFor, UserSelectedSource, CurrentlyFetchedArticle, Recommendation, Blacklist
from tokenizer import LemmaTokenizer
import logging
import datetime

# for each serving, get user's blacklist, and remove articles with words from blacklist
def clear_blacklisted(time=None):
  session = get_website_db_session()
  tokenizer = LemmaTokenizer()

  servings_and_users = session.query(RecommendationServing, User).filter(RecommendationServing.is_being_prepared==True, User.id==RecommendationServing.user_id)
  row_count = servings_and_users.count()
  logging.info(row_count)
  for i, (serving, user) in enumerate(servings_and_users):
    logging.info(f'Clearing blacklist for user {user.username} and serving {serving.recommendation_date} ({i+1}\' row out of {row_count}')

    articles_and_recommendation_data = session.query(Article, Recommendation).filter(
      Recommendation.article_id==Article.id,
      Recommendation.recommendation_serving_id==serving.id)
    blacklist = session.query(Blacklist).filter(Blacklist.user_id==user.id)
    for article, recommendation in articles_and_recommendation_data:
      lemmatized_article_words = tokenizer(article.text)

      # check if lemmatized article text contains any of lemmatized blacklisted words
      for blacklist_entry in blacklist:
        if blacklist_entry.lemmatized in lemmatized_article_words:
          serving.blacklisted_articles_amount += 1
          session.delete(recommendation)
          break
  session.commit()
