from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task
from airflow.operators.python_operator import PythonOperator
from DBTalker import clear_last_fetching_temporary_data, select_users_for_fetching, finalize_fetching
from article_url_fetcher import fetch_article_urls
from article_downloader import download_articles_html
from article_parser import parse_articles
from summarize_articles import summarize_articles
from keyword_extracter import extract_article_keywords
from clear_blacklisted_articles import clear_blacklisted
from group_articles_in_a_serving import group_articles_in_a_serving
#from compute_tfidf import compute_article_tfidf
from create_recommendation_servings import create_servings

default_args = {
    'owner': 'Nikito',
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='News_fetcher',
    default_args=default_args,
    description='TODO',
    schedule_interval=timedelta(hours=1),
    start_date=datetime(2022, 1, 1),
    catchup=False,
    max_active_runs=1
    #tags=['example'],
) as dag:
    clear_fetcher_db_task = PythonOperator(task_id="clear_fetcher_DB", python_callable=clear_last_fetching_temporary_data)

    initial_data_task = PythonOperator(task_id='select_users_for_fetching', python_callable=select_users_for_fetching)
    clear_fetcher_db_task >> initial_data_task

    url_fetcher_task = PythonOperator(task_id='fetch_urls_to_download', python_callable=fetch_article_urls)
    initial_data_task >> url_fetcher_task

    downloader_task = PythonOperator(task_id='download_articles', python_callable=download_articles_html)
    url_fetcher_task >> downloader_task

    parser_task = PythonOperator(task_id='parse_articles', python_callable=parse_articles)
    downloader_task >> parser_task

    summarizer_task = PythonOperator(task_id='summarize_articles', python_callable=summarize_articles)
    parser_task >> summarizer_task

    keywords_task = PythonOperator(task_id='get_keywords', python_callable=extract_article_keywords)
    parser_task >> keywords_task

    #tf_idf_task = PythonOperator(task_id='tf-idf', python_callable=compute_article_tfidf)
    #parser_task >> tf_idf_task

    servings_task = PythonOperator(task_id='create_recommendation_servings', python_callable=create_servings)
    parser_task >> servings_task

    clear_blacklisted_task = PythonOperator(task_id='clear_blacklisted_keyword_articles', python_callable=clear_blacklisted)
    servings_task >> clear_blacklisted_task

    group_task = PythonOperator(task_id='group_articles_in_serving', python_callable=group_articles_in_a_serving)
    clear_blacklisted_task >> group_task

    finalize_task = PythonOperator(task_id='finalize_fetching', python_callable=finalize_fetching)
    [group_task, summarizer_task, keywords_task] >> finalize_task
