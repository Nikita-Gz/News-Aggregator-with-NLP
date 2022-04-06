from DBTalker import get_website_db_session
from website_db_mapper import Article, User, RecommendationServing, UserBeingFetchedFor, UserSelectedSource, CurrentlyFetchedArticle, Recommendation, RecommendationTopic
from sklearn.cluster import KMeans
from typing import List, Dict
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from tokenizer import LemmaTokenizer
import nltk
import numpy as np
import logging

random_state = 22
clustering_returned_categories_ids_key = 0
clustering_returned_categories_names_key = 1
clustering_returned_categories_amount_key = 2

def kmeans_4_topic_clustering(*, articles: List[Article], **kwargs)->Dict:
  # get tf-idf first
  tokenizer = LemmaTokenizer()
  stop_words = set(stopwords.words('english')) 
  token_stopwords = tokenizer(' '.join(stop_words))
  vectorizer = TfidfVectorizer(tokenizer=tokenizer, stop_words=token_stopwords, max_features=200)
  tfidf_results = vectorizer.fit_transform([article.text for article in articles])
  logging.info(f'tfidf result dimensions: {tfidf_results.shape}')

  n_clusters = 4
  clusterizer = KMeans(n_clusters, random_state=random_state)
  category_ids = clusterizer.fit_predict(tfidf_results)

  clustering_result = {
    clustering_returned_categories_ids_key: category_ids,
    clustering_returned_categories_names_key: {i:f'topic {i+1}' for i in range(n_clusters)},
    clustering_returned_categories_amount_key: n_clusters
  }
  return clustering_result


def choose_clustering_algorithm():
  # todo: add others
  algo_id = 0
  clustering_algos = {
    0: kmeans_4_topic_clustering
  }

  return algo_id, clustering_algos[algo_id]


def group_articles_in_a_serving():
  session = get_website_db_session()
  servings_to_be_grouped = session.query(RecommendationServing).filter(RecommendationServing.is_being_prepared==True)
  row_count = servings_to_be_grouped.count()
  for serving_i, serving in enumerate(servings_to_be_grouped):
    logging.info(f'Grouping serving id {serving.id} for user {serving.user_id} (total serving #{serving_i+1} out of {row_count}')


    articles_and_respective_recommendations = session.query(Article, Recommendation).filter(
      Recommendation.recommendation_serving_id==serving.id,
      Recommendation.article_id==Article.id).all()
    articles_count = len(articles_and_respective_recommendations)
    if articles_count != 0:
      logging.info(f'{articles_count} articles up for grouping')
    else:
      logging.info(f'No articles, skipping grouping')
      continue
    articles, recommeandations = zip(*articles_and_respective_recommendations)

    algo_id, algo_callable = choose_clustering_algorithm()
    serving.topic_clustering_method = algo_id
    logging.info(f'Using clustering algorithm {algo_id}')

    clustering_result = algo_callable(articles=articles)
    cluster_ids = clustering_result[clustering_returned_categories_ids_key]
    cluster_id_2_name = clustering_result[clustering_returned_categories_names_key]
    #cluster_amount = clustering_result[clustering_returned_categories_amount_key]

    topic_objects_by_topic_id = {}
    for topic_id, topic_name in cluster_id_2_name.items():
      logging.info(f'Creating topic {topic_name} with id {topic_id}')
      topic_object = RecommendationTopic(recommendation_serving_id=serving.id, topic_name=topic_name, topic_description='Idk')
      topic_objects_by_topic_id[topic_id] = topic_object
      session.add(topic_object)
    session.commit()

    for article_i, (article, recommeandation) in enumerate(zip(articles, recommeandations)):
      article_topic_id = cluster_ids[article_i]
      logging.info(f"article \"{article.text[:100]}\" got category {topic_objects_by_topic_id[article_topic_id].topic_name}")
      
      recommeandation.topic_group_id = topic_objects_by_topic_id[article_topic_id].id
    session.commit()
