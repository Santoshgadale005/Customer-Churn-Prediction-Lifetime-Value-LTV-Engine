# Day 9: PostgreSQL Integration & Prediction Logging

## Overview
Today we evolved the Churn Prediction API into a persistent, enterprise-ready machine learning platform by integrating PostgreSQL using SQLAlchemy. Predictions are no longer ephemeral; they are now logged systematically for auditing, monitoring, and future dashboard analytics.

## Accomplishments
- ✅ **Connected FastAPI with PostgreSQL:** Configured SQLAlchemy engine and sessions using credentials from `.env`.
- ✅ **Created PredictionLog Model:** Implemented an ORM model mapping python objects to the `prediction_logs` database table.
- ✅ **Automated Table Creation:** Built `create_tables.py` to seamlessly initialize the database schema.
- ✅ **Built Reusable DB Session Dependency:** Configured FastAPI dependency injection (`get_db`) to manage database transactions and ensure graceful connection closures.
- ✅ **Updated Prediction Service:** Created `app/services/prediction_service.py` to seamlessly orchestrate prediction and PostgreSQL logging in one transaction.
- ✅ **Integrated Logging into API:** Modified the single prediction endpoint in `app/api/predict.py` to save customer input, prediction results, and churn probability in real-time.

## Current Status
The prediction logging infrastructure is fully implemented. Every time a customer is evaluated using the `/predict/` endpoint, a record is added to the database.

> [!WARNING]
> You may encounter a **password authentication error** when running `create_tables.py` if your PostgreSQL password is not correctly configured in the `.env` file. 

## Action Required
Before running the server or the table creation script, ensure your `.env` file contains your PostgreSQL password:
```env
DB_USER=postgres
DB_PASSWORD=your_actual_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=churn_ltv_db
```

## How to Run the Scripts
1. **Create the Tables**: 
```bash
source .venv/bin/activate
python create_tables.py
```
2. **Start the API**:
```bash
uvicorn app.main:app --reload
```
3. **Test the Endpoint**:
Send a POST request to `http://127.0.0.1:8000/predict/` using the Swagger UI (`/docs`). Afterwards, check pgAdmin to verify the entry in the `prediction_logs` table!

## Next Steps
In Day 10, we will continue building on this foundation to add more features or start integrating real-time dashboards to analyze the churn probabilities and feature logging we established today.
