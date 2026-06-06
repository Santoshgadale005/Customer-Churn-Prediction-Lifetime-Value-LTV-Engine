# Customer Intelligence Executive Dashboard

This document provides the blueprint for the Executive Intelligence Layer created in Metabase (or any BI tool connected to PostgreSQL). It translates raw ML outputs into business metrics.

## Executive KPIs

### 1. Total Customers Analyzed
- **SQL**: `SELECT COUNT(*) AS total_customers FROM prediction_logs;`
- **Visualization**: KPI Card
- **Business Meaning**: Shows platform usage and prediction volume.

### 2. Average Churn Probability
- **SQL**: `SELECT AVG(churn_probability) AS avg_churn_risk FROM prediction_logs;`
- **Visualization**: KPI Card
- **Business Meaning**: Overall customer risk level.

### 3. Average Predicted LTV
- **SQL**: `SELECT AVG(predicted_ltv) AS avg_ltv FROM prediction_logs;`
- **Visualization**: KPI Card
- **Business Meaning**: Average expected future customer value.

### 4. High-Risk Customers
- **SQL**: `SELECT COUNT(*) FROM prediction_logs WHERE churn_probability > 0.7;`
- **Visualization**: KPI Card
- **Business Meaning**: How many customers need immediate retention action?

## Revenue At Risk

- **SQL**: 
  ```sql
  SELECT SUM(predicted_ltv) AS revenue_at_risk 
  FROM prediction_logs 
  WHERE churn_probability > 0.7;
  ```
- **Visualization**: KPI Card
- **Business Meaning**: How much future revenue might we lose if these customers churn?

## Segment Analytics

### Customer Segment Distribution
- **SQL**:
  ```sql
  SELECT customer_segment, COUNT(*) AS customer_count 
  FROM prediction_logs 
  GROUP BY customer_segment;
  ```
- **Visualization**: Bar Chart
- **Business Meaning**: Helps allocate retention budgets by showing the distribution of High Value/High Risk vs Standard Customers.

### Revenue Segment Analysis
- **SQL**:
  ```sql
  SELECT customer_segment, AVG(predicted_ltv) AS avg_ltv 
  FROM prediction_logs 
  GROUP BY customer_segment;
  ```
- **Visualization**: Bar Chart
- **Business Meaning**: Average value per customer segment.

## Risk & LTV Distributions

### Churn Risk Distribution
- **SQL**: `SELECT prediction, COUNT(*) AS count FROM prediction_logs GROUP BY prediction;`
- **Visualization**: Pie Chart

### LTV Distribution
- **SQL**: `SELECT predicted_ltv FROM prediction_logs;`
- **Visualization**: Histogram

### Churn Probability Histogram
- **SQL**: `SELECT churn_probability FROM prediction_logs;`
- **Visualization**: Histogram

## Executive Summary Views

### Retention Priority Dashboard
- **SQL**:
  ```sql
  SELECT
      id,
      churn_probability,
      predicted_ltv,
      customer_segment,
      recommendation,
      created_at
  FROM prediction_logs
  WHERE churn_probability > 0.7
    AND predicted_ltv > 5000
  ORDER BY churn_probability DESC, predicted_ltv DESC
  LIMIT 100;
  ```
- **Visualization**: Table
- **Business Meaning**: These customers represent the highest business priority.

### Top 20 Valuable Customers
- **SQL**:
  ```sql
  SELECT
      id,
      predicted_ltv,
      churn_probability,
      customer_segment,
      recommendation,
      created_at
  FROM prediction_logs
  ORDER BY predicted_ltv DESC
  LIMIT 20;
  ```
- **Visualization**: Table
- **Business Meaning**: Identifies VIP customer management targets.

### Retention Recommendation Dashboard
- **SQL**:
  ```sql
  SELECT recommendation, COUNT(*) AS count 
  FROM prediction_logs 
  GROUP BY recommendation;
  ```
- **Visualization**: Bar Chart
- **Business Meaning**: Categorizes customers by intervention type (immediate retention, standard monitoring, etc.).

## Dashboard Filters
Ensure the dashboard includes global filters for:
- **Customer Segment**
- **Churn Risk**
- **LTV Range**
- **Tenure Range**

## Dashboard Layout Design

```text
------------------------------------------------
Total Customers | Avg LTV | Avg Risk | Revenue Risk
------------------------------------------------
Customer Segments      | Churn Distribution
------------------------------------------------
LTV Distribution       | Risk Distribution
------------------------------------------------
High Priority Customers Table
------------------------------------------------
Recommendations Analysis
------------------------------------------------
```
