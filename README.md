# recomender_app
Bachelor's diploma project. News aggregator website with text summarization, question answering and topic modelling. Utilizes airflow for scheduling the aggregation process

Features
1) Aggregates news from different user-selected sources on certain schedule
2) Provides a concise summary for each news article
3) Groups aggregated news by topic keywords
4) Generates answers for questions user asks about an article

Todo:
1) Use airflow/postgresql/django passwords and secret keys from environment variables
2) Use a proper webserver
3) Host this somewhere
4) Don't show all of the aggregated articles ao once, wait for user to scroll to the end of the page
