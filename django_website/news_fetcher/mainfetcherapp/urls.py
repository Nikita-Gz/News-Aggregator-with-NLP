from django.urls import path

from . import views

urlpatterns = [
    path('', views.recommendations_page, name='homepage'),
    path('crossroads', views.crossroads, name='crossroads'),
    path('ask_post', views.answer_post_question, name='answer_post_question'),
    path('rate_article_answer', views.rate_article_answer, name='rate_article_answer'),
    path('setup_sources', views.setup_sources, name='sourcesSetup'),
    path('register', views.register_request, name='register'),
    path("login", views.login_request, name="login")
]
