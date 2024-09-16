from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
from youtube_comments_etl import extract_comments, load_comments_to_csv

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'youtube_comments_etl',
    default_args=default_args,
    description='A DAG to extract and load YouTube comments into a CSV file',
    schedule_interval='@daily',  # Adjust the schedule as needed
    start_date=days_ago(1),
    catchup=False,
)

# Define the tasks
def extract_comments_task(**kwargs):
    api_key = "AIzaSyBoWZi2jsQNO5mZZlSk8cyHPVpgZP3jgho"  # Replace with your YouTube API key
    video_id = "OLXkGB7krGo"  # Replace with the YouTube video ID
    comments = extract_comments(api_key, video_id)
    kwargs['ti'].xcom_push(key='comments', value=comments)

def load_comments_task(**kwargs):
    ti = kwargs['ti']
    comments = ti.xcom_pull(task_ids='extract_comments', key='comments')
    output_file = "/opt/airflow/dags/youtube_comments.csv"  # Path in the Airflow container
    load_comments_to_csv(comments, output_file)

# Create PythonOperator tasks
extract_comments_op = PythonOperator(
    task_id='extract_comments',
    python_callable=extract_comments_task,
    provide_context=True,
    dag=dag,
)

load_comments_op = PythonOperator(
    task_id='load_comments',
    python_callable=load_comments_task,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
extract_comments_op >> load_comments_op
