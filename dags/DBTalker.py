from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, text
from website_db_mapper import RecommendationServing
from website_db_mapper import CurrentlyFetchedArticle, UserBeingFetchedFor, User, Article
import logging

def connect_to_website_db():
    # !! use propper password
    return create_engine('postgresql+psycopg2://airflow:airflow@postgres:5432/website_db', echo=True)

def get_website_db_session(engine=None) -> Session:
    if engine is None:
        engine = connect_to_website_db()
    session = sessionmaker(bind=engine)()
    return session

def get_website_db_metadata(engine=None):
    if engine is None:
        engine = connect_to_website_db()
    return MetaData(bind=engine, reflect=True)

def get_website_table(table_name: str, *, metadata=None, engine=None):
    if metadata is None:
        if engine is None:
            engine = connect_to_website_db()
        metadata = get_website_db_metadata(engine=engine)
    return metadata.tables['mainfetcherapp_' + table_name]

def clear_last_fetching_temporary_data():
    # todo: clean only appropriate data when and if running several fetchers
    session = get_website_db_session()
    session.query(CurrentlyFetchedArticle).delete()
    session.query(UserBeingFetchedFor).delete()
    session.query(RecommendationServing).filter(RecommendationServing.is_being_prepared==True).delete()
    session.commit()

def finalize_fetching():
    # todo: clean only appropriate data when and if running several fetchers
    session = get_website_db_session()
    recommendation_servings = session.query(RecommendationServing).filter(RecommendationServing.is_being_prepared==True)
    for serving in recommendation_servings:
        serving.is_being_prepared = False
    session.query(CurrentlyFetchedArticle).delete()
    session.query(UserBeingFetchedFor).delete()
    session.commit()

def select_users_for_fetching(hour_of_day=None):
    # just select all applicable users for now
    session = get_website_db_session()
    for user in session.query(User).filter(User.is_staff==False, User.is_active==True):
        user_being_fetched_for = UserBeingFetchedFor(user_id=user.id)
        session.add(user_being_fetched_for)
    session.commit()


    '''
    website_engine = create_engine('postgresql+psycopg2://airflow:airflow@postgres:5432/website_db', echo=True)
    website_db = sessionmaker(bind=website_engine)()
    fetcher_db = get_fetcher_db_session()

    # get required users from website (todo: fetch only necessary users)
    users_request = text("SELECT id from auth_user WHERE is_staff=false AND is_active=true")
    users_from_website = website_db.execute(users_request).fetchall()
    if len(users_from_website)==0:
        logging.warn('No users fetched from website database')

    user_ids = [user_tuple[0] for user_tuple in users_from_website]
    users_for_fetcher_db = dict()
    for user_id in user_ids:
        users_for_fetcher_db[user_id] = User(id=user_id)
        fetcher_db.add(users_for_fetcher_db[user_id])
    
    # get user <-> source associations from website db
    user_source_association_request = text('SELECT source_id, user_id FROM mainfetcherapp_userselectedsource WHERE user_id IN :id_list')
    user_source_association_tuples = website_db.execute(user_source_association_request, {'id_list':tuple(user_ids)}).fetchall()
    del user_ids
    if len(user_source_association_tuples)==0:
        logging.warn('No selected sources fetched from website database')

    # get sources from chosen sources list
    unique_source_ids = tuple(set([source_selection_tuple[0] for source_selection_tuple in user_source_association_tuples]))
    source_request = text('SELECT id, url, name FROM mainfetcherapp_source WHERE id IN :id_list')
    sources_from_website = website_db.execute(source_request, {'id_list':tuple(unique_source_ids)}).fetchall()
    if len(sources_from_website)==0:
        logging.warn('No selected sources fetched from website database')
    
    sources_for_fetcher_db = dict()
    for source_id, url, name in sources_from_website:
        sources_for_fetcher_db[source_id] = Source(id=source_id, url=url, name=name)
        fetcher_db.add(sources_for_fetcher_db[source_id])

    website_db.close()

    # setup user <-> source assiciations in fetcher DB
    for source_id, user_id in user_source_association_tuples:
        sources_for_fetcher_db[source_id].chosen_by_users.append(users_for_fetcher_db[user_id])
    
    fetcher_db.commit()
    '''

def query_fetched_articles_and_fetching_data(session: Session):
    return session.query(Article, CurrentlyFetchedArticle).filter(Article.id==CurrentlyFetchedArticle.article_id)

