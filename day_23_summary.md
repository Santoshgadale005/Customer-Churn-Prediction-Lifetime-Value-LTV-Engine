# Day 23: Automated Data Pipelines with Apache Airflow

## Overview
Today, the project evolved into an automated Data Engineering and MLOps platform by integrating **Apache Airflow**. Instead of relying on manual scripts, we established a scheduled ETL and retraining pipeline.

## Accomplishments
- ✅ **Airflow Integration:** Added the `apache/airflow:2.9.0` container to our `docker-compose.yml` to orchestrate workflows natively alongside our API and database.
- ✅ **Airflow Environment:** The Airflow Dashboard is now available locally on `http://localhost:8080`.
- ✅ **DAG Created:** Built our first Directed Acyclic Graph (DAG) at `airflow/dags/churn_pipeline.py`.
- ✅ **ETL Pipeline Automation:** Connected individual tasks into an automated sequence:
  - Extract Data
  - Transform Data
  - Feature Engineering (`app/services/feature_engineering.py`)
  - Load to PostgreSQL
  - Model Training (`app/models/train_with_mlflow.py`)
  - Model Evaluation
- ✅ **Scheduling:** Configured the pipeline to run daily (`@daily`) so that the models stay continuously updated as new data flows in.
- ✅ **MLflow Synergy:** Connected the Airflow pipeline to our MLflow scripts, establishing an automated loop: *Airflow triggers training → MLflow logs metrics → MLflow registers the best model*.

## Impact
Manual execution of feature engineering and training scripts is prone to human error and difficult to scale. With Airflow, we have automated the entire backend data flow. This connects the entire enterprise MLOps architecture: Scheduled jobs run feature generation, train new models, track metrics in MLflow, and deploy the updated results to the API database seamlessly.
