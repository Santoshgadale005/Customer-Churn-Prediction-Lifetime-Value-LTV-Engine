# Customer Churn & LTV Engine

## Project Overview
This project is a production-level predictive analytics platform designed for telecom and subscription-based businesses. It focuses on two key metrics:
1. **Customer Churn Prediction**: Identifying customers likely to leave the service.
2. **Customer Lifetime Value (LTV)**: Predicting the total revenue a customer will generate.

## Tech Stack
- **Language**: Python 3.9+
- **Database**: PostgreSQL (Data Warehouse)
- **ML Frameworks**: Scikit-Learn, XGBoost
- **Explainability**: SHAP
- **API**: FastAPI
- **Visualization**: Plotly, Seaborn
- **Deployment**: Docker

## Project Structure
- `app/`: Core application logic (API, Models, Services)
- `data/`: Local storage for datasets (Git ignored)
- `notebooks/`: Exploratory Data Analysis and prototyping
- `dashboards/`: Visualization configurations
- `docker/`: Containerization setup

## Setup Instructions
1. Create a virtual environment: `python3 -m venv venv`
2. Activate venv: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
