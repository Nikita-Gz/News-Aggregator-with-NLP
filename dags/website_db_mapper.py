from lib2to3.pgen2.token import STRING
#from sqlalchemy import Column, Integer, BOOLEAN, String, PickleType, TIMESTAMP, ForeignKey, Table, Text
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import relationship

# !! use propper password
engine = create_engine('postgresql+psycopg2://airflow:airflow@postgres:5432/website_db', echo=False)
Base = automap_base()

class User(Base):
    __tablename__='auth_user'

class UserBeingFetchedFor(Base):
    __tablename__='mainfetcherapp_userbeingfetchedfor'

class Article(Base):
    __tablename__='mainfetcherapp_article'

class ArticleKeyword(Base):
    __tablename__ = 'mainfetcherapp_articlekeyword'

class CurrentlyFetchedArticle(Base):
    __tablename__='mainfetcherapp_currentlyfetchedarticle'

class Source(Base):
    __tablename__='mainfetcherapp_source'

class UserSelectedSource(Base):
    __tablename__='mainfetcherapp_userselectedsource'

class Blacklist(Base):
    __tablename__='mainfetcherapp_blacklist'

class RecommendationTopic(Base):
    __tablename__='mainfetcherapp_recommendationtopic'

class RecommendationServing(Base):
    __tablename__='mainfetcherapp_recommendationserving'

class Recommendation(Base):
    __tablename__='mainfetcherapp_recommendation'

Base.prepare(engine, reflect=True)

'''
Base = declarative_base()

chosen_sources = Table('chosen_sources', Base.metadata,
  Column('user_id', ForeignKey('users.id'), primary_key=True),
  Column('source_id', ForeignKey('sources.id'), primary_key=True)
)

class Source(Base):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    name = Column(String(30))

    articles = relationship('Article', back_populates='source', cascade='all, delete, delete-orphan')

    chosen_by_users = relationship('User', secondary=chosen_sources, back_populates='chosen_sources')

    def __repr__(self) -> str:
        return "<Source(url='%s', url='%s')>" % (self.url, self.name)

class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    html = Column(String)
    title = Column(String)
    text = Column(String)
    summary = Column(String)
    main_image = Column(String)
    tfidf = Column(PickleType)
    publish_date = Column(String)
    download_date = Column(TIMESTAMP)
    is_downloaded_on_main = Column(BOOLEAN)

    source_id = Column(Integer, ForeignKey('sources.id'))
    source = relationship("Source", back_populates="articles")

    keywords = relationship('ArticleKWord', back_populates='article', cascade='all, delete, delete-orphan')

    recommendations = relationship('Recommendations', back_populates='article', cascade='all, delete, delete-orphan')

class ArticleKWord(Base):
    __tablename__ = 'article_keywords'
    id = Column(Integer, primary_key=True)
    kword = Column(String)
    article_id = Column(Integer, ForeignKey('articles.id'))
    article = relationship("Article", back_populates="keywords")

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    chosen_sources = relationship('Source', secondary=chosen_sources, back_populates='chosen_by_users')

    blacklist_keywords = relationship('Blacklist', back_populates='user', cascade='all, delete, delete-orphan')

    recommendation_servings = relationship('RecommendationServing', back_populates='user', cascade='all, delete, delete-orphan')

class Blacklist(Base):
    __tablename__ = 'blacklist_keywords'
    id = Column(Integer, primary_key=True)
    keyword = Column(String)
    block_all_occurences = Column(BOOLEAN)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="blacklist_keywords")

# associates packs of recommended articles for a certain day <-> user
class RecommendationServing(Base):
    __tablename__ = 'recommendation_serving'
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='recommendation_servings')

    recommendation_date = Column(TIMESTAMP, nullable=False)

    recommendation_topics = relationship('RecommendationTopic', back_populates='recommendation_serving', cascade='all, delete, delete-orphan')
    recommendations = relationship('Recommendations', back_populates='recommendation_serving', cascade='all, delete, delete-orphan')

class RecommendationTopic(Base):
    __tablename__ = 'recommendation_topics'
    id = Column(Integer, primary_key=True)

    recommendation_serving_id = Column(Integer, ForeignKey('recommendation_serving.id'))
    recommendation_serving = relationship('RecommendationServing', back_populates='recommendation_topics')

    topic_name = Column(String, nullable=False)
    topic_description = Column(String, nullable=False)
    topic_method = Column(Integer, nullable=False)

    recommendations = relationship('Recommendations', back_populates='recommendation_topics', cascade='all, delete, delete-orphan')

class Recommendations(Base):
    __tablename__ = 'recommendations'

    recommendation_serving_id = Column(Integer, ForeignKey('recommendation_serving.id'), nullable=False)
    recommendation_serving = relationship('RecommendationServing', back_populates='recommendations')

    article_id = Column(Integer, ForeignKey('articles.id'), nullable=False)
    article = relationship("Article", back_populates="recommendations")

    topic_id = Column(Integer, ForeignKey('recommendation_topics.id'), nullable=True)
    topic = relationship("RecommendationTopic", back_populates="recommendations")
'''
