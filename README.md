# recomender_app
Bachelor's diploma project. News aggregator website with text summarization, question answering and topic modelling. Utilizes airflow for scheduling the aggregation process

Features
1) Aggregates news from different user-selected sources on a schedule
2) Provides a concise summary for each news article
3) Groups aggregated news by topic keywords
4) Generates answers for questions user asks about an article

Todo:
1) Use airflow/postgresql/django passwords and secret keys from environment variables
2) Use a proper webserver
3) Host this somewhere
4) Don't show all of the aggregated articles at once, wait for user to scroll to the end of the page

Projet folders:
1) "dags" - contains files needed for news aggregation process DAG, including text summarization and topic modelling
2) "django_website" - contains files for django website

Container structure:
Django website container <=> PostgreSQL container <=> Airflow containers for news aggregation & NLP

How to launch and how to use: WIP
