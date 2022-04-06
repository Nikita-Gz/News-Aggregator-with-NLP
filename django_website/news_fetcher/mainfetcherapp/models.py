from email.policy import default
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Source(models.Model):
  url = models.TextField(unique=True, null=False)
  name = models.TextField(unique=True, null=False)
  assigned_to_user_by_default = models.BooleanField(null=False, default=False)
  image = models.ImageField(null=True, upload_to ='source_logos/')

  selected_by_users = models.ManyToManyField(User, through='UserSelectedSource')

  def __str__(self):
    return '{}'.format(self.name)

class UserSelectedSource(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
  source = models.ForeignKey(Source, on_delete=models.CASCADE, null=False)

  def __str__(self):
    return '{} <-> {}'.format(self.user, self.source)

class Blacklist(models.Model):
    keyword = models.TextField()
    lemmatized = models.TextField()
    block_all_occurences = models.BooleanField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

class Article(models.Model): 
  url = models.TextField(unique=True, null=False)
  source = models.ForeignKey(Source, on_delete=models.CASCADE, null=False)
  html = models.TextField()
  title = models.TextField()
  text = models.TextField()
  summary = models.TextField()
  main_image = models.TextField()
  publish_date = models.TextField()
  download_date = models.DateTimeField(null=True)

  def __str__(self):
    return '{}'.format(self.url)

class AnswerForArticle(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
  article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)
  model_id = models.IntegerField(null=False)
  rating = models.IntegerField(null=False)
  certainty = models.FloatField(null=False)
  question = models.TextField()
  answer = models.TextField()

  def __str__(self):
      return f'user {self.user}: {self.question} -> {self.answer}'

class ArticleKeyword(models.Model):
  article = models.ForeignKey(Article, null=False, on_delete=models.CASCADE)
  text = models.TextField()
  lemmatized_text = models.TextField()

  def __str__(self):
    return '{} (lemmatized: {})'.format(self.text, self.lemmatized_text)

class CurrentlyFetchedArticle(models.Model):
  article = models.OneToOneField(Article, unique=True, null=False, on_delete=models.CASCADE)
  was_already_downloaded = models.BooleanField(null=False)
  tfidf = models.BinaryField(null=True)

  def __str__(self):
    return '{}, {}'.format(self.article, self.was_already_downloaded)

class UserBeingFetchedFor(models.Model):
  user = models.OneToOneField(User, unique=True, null=False, on_delete=models.CASCADE)

  def __str__(self):
    return '{}'.format(self.user)

# associates packs of recommended articles for a certain day <-> user
class RecommendationServing(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
  recommendation_date = models.DateTimeField(null=False)
  is_being_prepared = models.BooleanField(null=False)
  topic_clustering_method = models.IntegerField(null=True)
  blacklisted_articles_amount = models.IntegerField(null=False, default=0)

  readonly_fields = ('id',)

  def __str__(self):
    is_ready = 'ready'
    if self.is_being_prepared:
      is_ready = 'not ready'
    return '{} for {} on {} ({} articles blocked)'.format(is_ready, self.user, self.recommendation_date, self.blacklisted_articles_amount)

class RecommendationTopic(models.Model):
  recommendation_serving = models.ForeignKey(RecommendationServing, on_delete=models.CASCADE, null=False)
  topic_name = models.TextField(null=False)
  topic_description = models.TextField(null=False)

  readonly_fields = ('id',)

  def __str__(self):
    return '"{}" by method {}'.format(self.topic_name, self.topic_description)

class Recommendation(models.Model):
  recommendation_serving = models.ForeignKey(RecommendationServing, on_delete=models.CASCADE, null=False)
  article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)
  topic_group = models.ForeignKey(RecommendationTopic, on_delete=models.CASCADE, null=True)

  readonly_fields = ('id',)

  def __str__(self):
    return 'article {} {}'.format(self.article, str(self.recommendation_serving))
