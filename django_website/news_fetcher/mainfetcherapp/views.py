from importlib import import_module
import logging
from collections import Counter

from .qa_models import qa_models

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpRequest
from .forms import NewUserForm, SourceSelectionForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.db.models.query import QuerySet

from .models import Article, Source, UserSelectedSource, RecommendationServing, AnswerForArticle
from .constants import default_serving_username

'''
def index(request: HttpRequest):
	username = None
	if request.user.is_authenticated:
		username = request.user.username
		print(type(request.user))
	return render (request=request, template_name="mainfetcherapp/homepage.html", context={"username":username})
'''

def crossroads(request: HttpRequest):
	user = request.user
	username = user.username
	return render(request=request, template_name="mainfetcherapp/crossroads.html", context={"username":username})

def recommendations_page(request: HttpRequest):
	user = request.user
	username = None
	if user.is_authenticated:
		username = user.username
		print(type(user))
	else:
		return render(request=request, template_name="mainfetcherapp/homepage.html")
	
	if user.is_staff:
		return render(request=request, template_name="mainfetcherapp/homepage.html", context={'username':username, 'staff':True})

	latest_serving = RecommendationServing.objects.filter(user=user, is_being_prepared=False).order_by('recommendation_date').last()
	if latest_serving is None:
		# fallbacks on default serving
		default_servings_user = User.objects.filter(username=default_serving_username).last()
		latest_serving = RecommendationServing.objects.filter(user=default_servings_user, is_being_prepared=False).order_by('recommendation_date').last()

		# do not use any serving if there's no default one
		if latest_serving is None:
			print(f'Found no servings for user {user.username} and no default servings')
			context = {
			"username":username,
			}
			return render (request=request, template_name="mainfetcherapp/homepage.html", context=context)

		is_default_serving = True
		print(f'Using default serving for user {user.username}')
	else:
		is_default_serving = False
	

	topics = latest_serving.recommendationtopic_set.all()
	topics_to_render = []
	total_article_count = 0
	for topic in topics:
		topic_data = {'name': topic.topic_name}

		recommendations_for_topic = topic.recommendation_set.all()
		articles_to_render = []
		keyword_counts = dict()
		for recommendation in recommendations_for_topic:
			article_entry_to_render = dict()
			article = recommendation.article

			keyword_objects = article.articlekeyword_set.all()
			keywords_string = ', '.join([kword_object.lemmatized_text for kword_object in keyword_objects])
			for keyword_object in keyword_objects:
				keyword_counts[keyword_object.lemmatized_text] = keyword_counts.get(keyword_object.lemmatized_text, 0) + 1

			article_entry_to_render['content'] = article
			article_entry_to_render['keywords'] = keywords_string
			article_entry_to_render['topic'] = recommendation.topic_group.topic_name
			article_entry_to_render["minutes_to_read"] = max((len(article.text.split()) // 200), 1)
			articles_to_render.append(article_entry_to_render)
			total_article_count += 1
		topic_data['articles'] = articles_to_render
		topic_data['article_count'] = len(articles_to_render)

		# select top keywords
		n_top_keywords = 4
		keywords_strings = []
		for keyword, count in Counter(keyword_counts).most_common(n_top_keywords):
			keywords_strings.append(f'{keyword} ({count} mentions)')
		final_keywords_string = ', '.join(keywords_strings)
		topic_data['keywords'] = final_keywords_string

		topics_to_render.append(topic_data)


	#print(latest_serving)
	context = {
		"username":username, 'topics': topics_to_render, 'recommendation_date': latest_serving.recommendation_date,
		'total_article_count': total_article_count,
		'default_serving': is_default_serving
		}
	return render (request=request, template_name="mainfetcherapp/homepage.html", context=context)


def answer_post_question(request: HttpRequest):
	user = request.user

	# todo: select random model
	model_id, model_pipeline = list(qa_models.items())[0]

	# todo: check validity
	article_id = request.GET['article_id']
	question = request.GET['question']
	article = Article.objects.get(pk=article_id)

	print(f'Answering {question}...')
	model_results = model_pipeline(question = question, context = article.text,
		max_answer_len=512, handle_impossible_answer =True,
    max_question_len=999,
    max_seq_len=512,
		top_k=3)
	
	answers = []
	for result in model_results:
		answer = result['answer']
		new_answer = AnswerForArticle(
			user=user,
			article=article,
			model_id=model_id,
			rating=0,
			certainty=result['score'],
			question=question,
			answer=answer)
		new_answer.save()
		answers.append(new_answer)
		print(f'Answered "{question}" with "{answer}"')

	#score = model_result['score']
	context = {'answers': answers}
	return render(request=request, template_name="mainfetcherapp/answers_response.html", context=context)


def rate_article_answer(request: HttpRequest):
	user = request.user
	answer_id = request.GET['answer_id']

	# get answer model, and check if it belongs to the user
	try:
		answer = AnswerForArticle.objects.get(pk=answer_id, user=user)
	except:
		return HttpResponse(">:(")
	
	answer.rating = 1
	answer.save()
	return HttpResponse("")


def setup_sources(request):
	user = request.user
	if not user.is_authenticated:
		messages.error(request, "You need to be logged in.")
		return render (request=request, template_name="mainfetcherapp/homepage.html", context={"username":user.username})

	def return_get_request():
		selected_sources = Source.objects.filter(selected_by_users=user)
		form = SourceSelectionForm(initial={'sourceChoices': selected_sources})
		return render(request, 'mainfetcherapp/sources_selection.html', {'form': form})

	if request.method == 'POST':
		form = SourceSelectionForm(request.POST)
		if not form.is_valid():
			messages.error(request, "Invalid submitted data.")
			return return_get_request()
		
		sources_selected = form.cleaned_data['sourceChoices'] # type: QuerySet
		previously_selected_sources = Source.objects.filter(selected_by_users=user)
		newly_selected_sources = sources_selected.exclude(pk__in=previously_selected_sources)
		deselected_sources = previously_selected_sources.exclude(pk__in=sources_selected)

		# removes deselected "user <-> source" relations
		# todo: bulk update
		for removedSource in deselected_sources:
			removedSource.selected_by_users.remove(user)

		# adds new "user <-> source" relations
		# todo: bulk update
		for newSource in newly_selected_sources:
			newSource.selected_by_users.add(user)

		messages.success(request, "Updated sources.")
		return return_get_request()
	else:
		return return_get_request()


def register_request(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )

			# adds some default sources to user's source selection
			# todo: bulk update
			for source in Source.objects.filter(assigned_to_user_by_default=True):
				source.selected_by_users.add(user)

			return redirect("homepage")

		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm()
	return render (request=request, template_name="mainfetcherapp/register.html", context={"register_form":form})

def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)

			if user is None:
				messages.error(request,"Invalid username or password.")
			elif username != default_serving_username:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("homepage")
			elif username == default_serving_username:
				messages.error(request,"Please use a different username.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="mainfetcherapp/login.html", context={"login_form":form})

