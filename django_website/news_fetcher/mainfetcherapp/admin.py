from django.contrib import admin
from .models import Source, UserSelectedSource, Article, RecommendationServing, Recommendation, RecommendationTopic, ArticleKeyword, AnswerForArticle

admin.site.register(Source)
admin.site.register(UserSelectedSource)
admin.site.register(Article)
admin.site.register(ArticleKeyword)
admin.site.register(RecommendationServing)
admin.site.register(Recommendation)
admin.site.register(RecommendationTopic)
admin.site.register(AnswerForArticle)

# Register your models here.
