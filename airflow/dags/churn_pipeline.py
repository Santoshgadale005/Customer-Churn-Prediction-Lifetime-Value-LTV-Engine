from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os

def extract_data():
    print("Extracting data")
    # In a real pipeline, this would connect to a DB or API and fetch the latest raw data
    
def transform_data():
    print("Transforming data")
    # In a real pipeline, this would clean the raw data

def engineer_features():
    print("Feature Engineering")
    os.system("python app/services/feature_engineering.py")

def load_to_postgres():
    print("Loading to PostgreSQL")
    # In a real pipeline, this would load the engineered features into a Data Warehouse

def train_model():
    print("Training churn model")
    os.system("python app/models/train_with_mlflow.py")

def evaluate_model():
    print("Evaluating model")
    # In a real pipeline, this would evaluate the newly trained model against a validation set

with DAG(
    dag_id="customer_churn_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False
) as dag:

    extract_task = PythonOperator(
        task_id="extract_data",
        python_callable=extract_data
    )
    
    transform_task = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data
    )
    
    engineer_features_task = PythonOperator(
        task_id="engineer_features",
        python_callable=engineer_features
    )
    
    load_to_postgres_task = PythonOperator(
        task_id="load_to_postgres",
        python_callable=load_to_postgres
    )

    train_task = PythonOperator(
        task_id="train_model",
        python_callable=train_model
    )
    
    evaluate_task = PythonOperator(
        task_id="evaluate_model",
        python_callable=evaluate_model
    )

    # Define task dependencies
    extract_task >> transform_task >> engineer_features_task >> load_to_postgres_task >> train_task >> evaluate_task
