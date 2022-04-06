from DBTalker import get_website_db_session
from website_db_mapper import RecommendationServing
import logging
import datetime

# for each user, assign them articles according to their sources list
def create_servings(time):
  session = get_website_db_session()
  servings_being_prepared = session.query(RecommendationServing).filter(RecommendationServing.is_being_prepared==True)
  for serving in servings_being_prepared:
    serving.is_being_prepared = False
  session.commit()
