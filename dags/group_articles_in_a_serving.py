from DBTalker import get_website_db_session
from website_db_mapper import Article, User, RecommendationServing, UserBeingFetchedFor, UserSelectedSource, CurrentlyFetchedArticle, Recommendation, RecommendationTopic
from sklearn.cluster import KMeans
from typing import List, Dict
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from tokenizer import LemmaTokenizer
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
import nltk
import numpy as np
import logging

stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use'])
tokenizer = LemmaTokenizer()
token_stopwords = tokenizer(' '.join(stop_words))

random_state = 22
clustering_returned_categories_ids_key = 0
clustering_returned_categories_names_key = 1
clustering_returned_categories_amount_key = 2

def kmeans_4_topic_clustering(*, articles: List[Article], **kwargs)->Dict:
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


def lda_4_topic_clustering(*, articles: List[Article], **kwargs)->Dict:
  def sent_to_words(sentences):
    for sentence in sentences:
      # deacc=True removes punctuations
      yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))

  def remove_stopwords(texts):
    return [[word for word in simple_preprocess(str(doc)) 
             if word not in stop_words] for doc in texts]

  def lemmatize(texts):
    return [tokenizer.lemmatize_already_tokenized_texts(text) for text in texts]

  data_words = list(sent_to_words([article.text for article in articles]))
  data_words = remove_stopwords(data_words)
  #data_words = lemmatize(data_words)

  id2word = corpora.Dictionary(data_words)
  texts = data_words
  corpus = [id2word.doc2bow(text) for text in texts]

  num_topics = 4
  lda_model = gensim.models.LdaModel(corpus=corpus,
                                     id2word=id2word,
                                     passes=3,
                                     num_topics=num_topics)
  results = lda_model[corpus]

  def get_topic_from_lda_result(result):
    best_fitting_topic = 0
    top_certainty = 0
    for topic_tuple in result:
      topic_id = topic_tuple[0]
      certainty = topic_tuple[1]
      
      if certainty > top_certainty:
        best_fitting_topic = topic_id
        top_certainty = certainty
    return best_fitting_topic

  # decides which topic ID each article has
  topic_ids = np.zeros(len(results))
  for result_i, lda_result_for_article in enumerate(results):
    topic_ids[result_i] = get_topic_from_lda_result(lda_result_for_article)
  
  # composes topic descriptions
  topic_descriptions = dict()
  for topic_i in range(num_topics):
    topic_description_tuples = lda_model.show_topic(topic_i)[:10]
    topic_words = [keyword for keyword, _ in topic_description_tuples]
    topic_name = ', '.join(topic_words)
    topic_descriptions[topic_i] = topic_name

  clustering_result = {
    clustering_returned_categories_ids_key: topic_ids,
    clustering_returned_categories_names_key: topic_descriptions,
    clustering_returned_categories_amount_key: num_topics
  }
  return clustering_result



def choose_clustering_algorithm():
  # todo: add others
  algo_id = 1
  clustering_algos = {
    0: kmeans_4_topic_clustering,
    1: lda_4_topic_clustering
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
