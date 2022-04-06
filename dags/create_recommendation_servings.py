from DBTalker import get_website_db_session
from website_db_mapper import Article, User, RecommendationServing, UserBeingFetchedFor, UserSelectedSource, CurrentlyFetchedArticle, Recommendation
import logging
import datetime

# for each user, assign them articles according to their sources list
def create_servings(time=None):
  session = get_website_db_session()
  recommendation_date = datetime.datetime.now()

  fetched_users = session.query(UserBeingFetchedFor)
  fetched_users_count = fetched_users.count()
  for user_i, user in enumerate(fetched_users):
    logging.info(f'Packing recommendations for user ({user_i+1} out of {fetched_users_count})')

    recommendation_serving = RecommendationServing(user_id=user.user_id, recommendation_date=recommendation_date, is_being_prepared=True, blacklisted_articles_amount=0)
    session.add(recommendation_serving)
    session.commit()

    # Recommend articles from the user's sources, pack them under one recommendation serving.
    # Delete created recommendation serving if something goes wrong
    try:
      sources_ids_user_chose = session.query(UserSelectedSource.source_id).filter(UserSelectedSource.user_id==user.user_id).subquery()
      currently_fetching_articles = session.query(CurrentlyFetchedArticle.article_id).subquery()
      fetched_articles_from_selected_sources = session.query(Article).filter(Article.id.in_(currently_fetching_articles), Article.source_id.in_(sources_ids_user_chose))
      recommended_articles_amount = 0
      for article in fetched_articles_from_selected_sources:
        recommendation = Recommendation(recommendation_serving_id=recommendation_serving.id, article_id=article.id)
        session.add(recommendation)
        recommended_articles_amount += 1
      logging.info(f'Recommended {recommended_articles_amount} articles to user')
      session.commit()
    except Exception as e:
      # delete recommendation serving if there was a problem with assigning articles to it
      session.delete(recommendation_serving)
      raise e

  # just in case  
  session.commit()