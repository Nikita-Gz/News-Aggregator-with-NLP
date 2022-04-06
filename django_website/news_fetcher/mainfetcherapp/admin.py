from django.contrib import admin
from .models import Source, UserSelectedSource, Article, RecommendationServing, Recommendation, RecommendationTopic

admin.site.register(Source)
admin.site.register(UserSelectedSource)
admin.site.register(Article)
admin.site.register(RecommendationServing)
admin.site.register(Recommendation)
admin.site.register(RecommendationTopic)

# Register your models here.
