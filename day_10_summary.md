# Day 10: Dashboard Analytics with Metabase

## Overview
Today, the project evolved from a backend API into a complete **Business Analytics Platform**. We deployed Metabase using Docker, ensuring that business stakeholders can interactively analyze ML predictions and monitor key performance indicators (KPIs).

## Accomplishments
- ✅ **Docker Environment:** Verified Docker installation and successfully pulled and launched the Metabase container on port 3000.
- ✅ **Database Troubleshooting:** Identified that local port 5432 was already in use by a native PostgreSQL 17 installation with unknown credentials. To resolve this, we spun up a new PostgreSQL 15 Docker container mapped to port 5433, matching the configured `.env` variables (`your_password`, `churn_ltv_db`).
- ✅ **Schema and Data Population:** Ran the `create_tables.py` script to create the `prediction_logs` table in our new database and created a Python script (`seed_predictions.py`) to insert 100 mock prediction logs so that Metabase has beautiful data to visualize immediately.

## Action Required: Metabase Setup
Because Metabase configuration requires manual UI interaction for creating dashboards, you need to complete the following steps in your browser:

### 1. Initial Setup
1. Open your browser and go to: [http://localhost:3000](http://localhost:3000)
2. Create your local admin account.

### 2. Connect PostgreSQL Database
1. Go to **Add Database** and select **PostgreSQL**.
2. Enter the following credentials:
   - **Host:** `host.docker.internal`
   - **Port:** `5433` *(Note: We used 5433 to avoid conflicts with your local PG17)*
   - **Database name:** `churn_ltv_db`
   - **Username:** `postgres`
   - **Password:** `your_password`

### 3. Build Your Dashboard
Use the "Custom Question -> SQL Query" feature to create the following KPIs and charts, saving each one and adding it to your final **Churn Analytics Dashboard**:

**KPI: Total Predictions**
```sql
SELECT COUNT(*) AS total_predictions
FROM prediction_logs;
```

**KPI: Average Churn Probability**
```sql
SELECT AVG(churn_probability) AS average_risk
FROM prediction_logs;
```

**Bar Chart: Churn Prediction Distribution**
```sql
SELECT prediction, COUNT(*) AS count
FROM prediction_logs
GROUP BY prediction;
```
*(Visualize as a Bar Chart)*

**Table: High-Risk Customers**
```sql
SELECT *
FROM prediction_logs
WHERE churn_probability > 0.8;
```

**Scatter Plot: Tenure vs Risk**
```sql
SELECT tenure, churn_probability
FROM prediction_logs;
```
*(Visualize as a Scatter Plot)*

## Next Steps
Now that the BI platform is up and running, you have successfully bridged the gap between raw ML predictions and actionable business insights. You can now present your project as an end-to-end, enterprise-grade machine learning system!
