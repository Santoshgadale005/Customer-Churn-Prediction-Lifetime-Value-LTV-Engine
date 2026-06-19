# Day 28: Advanced MLOps — Automated Model Retraining & Drift Detection

## Overview

Today the Customer Churn Prediction & LTV Engine evolved from a deployed ML application into a **self-monitoring MLOps platform**. The system can now detect when model performance degrades due to real-world data distribution changes and automatically trigger retraining workflows — closing the full MLOps lifecycle loop.

## The Problem Solved

Models trained once degrade silently over time. Customer behavior, market pricing, and business strategies shift — but without monitoring, the model keeps predicting on stale assumptions:

```
Model Accuracy ↓  →  Prediction Quality ↓  →  Business Value ↓
```

## Accomplishments

- ✅ **Drift Detection Service Built:** Created [`app/services/drift_detection.py`](file:///Users/santoshgadale/Desktop/zaaalima%201/app/services/drift_detection.py) using the **Kolmogorov–Smirnov (KS) test** to compare training and production feature distributions across 5 monitored features.
- ✅ **Real Drift Detected:** Generated a production dataset with a simulated pricing market shift (+35% MonthlyCharges). KS test confirmed statistically significant drift in **3 features** (MonthlyCharges, TotalCharges, RevenuePerMonth) with p-values of 0.0000.
- ✅ **Performance Monitor Built:** Created [`app/services/performance_monitor.py`](file:///Users/santoshgadale/Desktop/zaaalima%201/app/services/performance_monitor.py) to compute Accuracy, Precision, Recall, and F1 score when ground-truth labels become available, with configurable retraining thresholds.
- ✅ **Automated Retraining Script:** Created [`app/models/retrain_model.py`](file:///Users/santoshgadale/Desktop/zaaalima%201/app/models/retrain_model.py) which retrains the XGBoost model and **only deploys if the new model beats the old model** (by at least 0.5% F1 improvement).
- ✅ **MLflow Model Registry Integrated:** Retraining script transitions models through `Staging → Production → Archived` stages, ensuring governance of every deployment decision.
- ✅ **Airflow DAG Created:** Built [`airflow/dags/drift_monitoring_pipeline.py`](file:///Users/santoshgadale/Desktop/zaaalima%201/airflow/dags/drift_monitoring_pipeline.py) — a daily automated pipeline (runs 02:00 UTC) with a `ShortCircuitOperator` that skips retraining when drift thresholds aren't breached.
- ✅ **MLOps API Endpoints Added:** Created [`app/api/mlops.py`](file:///Users/santoshgadale/Desktop/zaaalima%201/app/api/mlops.py) with 6 new REST endpoints for on-demand drift detection, performance monitoring, manual retraining (admin only), and status dashboard.
- ✅ **Prometheus Metrics Extended:** Added 7 new Prometheus gauges/counters: `drift_features_detected_total`, `drift_ks_statistic`, `model_f1_score_current`, `model_accuracy_current`, `model_retraining_total`, `model_deployed_total`.
- ✅ **Grafana Dashboard Created:** Built [`monitoring/grafana/dashboards/mlops_drift_retraining.json`](file:///Users/santoshgadale/Desktop/zaaalima%201/monitoring/grafana/dashboards/mlops_drift_retraining.json) with panels for drift scores, model performance over time, retraining activity, and live churn rate.

## Drift Detection Results

```
Feature               Status          KS Stat   p-value     Train μ     Prod μ
──────────────────────────────────────────────────────────────────────────────
tenure                ✅ No Drift     0.0496    0.1938      32.42       34.45
MonthlyCharges        ⚠️  DRIFT       0.3698    0.0000      64.80       89.03
TotalCharges          ⚠️  DRIFT       0.1222    0.0000      2283.30     3201.76
RevenuePerMonth       ⚠️  DRIFT       0.3390    0.0000      59.08       85.59
EngagementScore       ✅ No Drift     0.0482    0.2216      2283.15     2459.68

Overall: DRIFT_DETECTED  |  Retrain Recommended: True
```

## Files Created / Modified

| File | Action | Purpose |
|------|--------|---------|
| `app/services/drift_detection.py` | **NEW** | KS-test drift detection across 5 features |
| `app/services/performance_monitor.py` | **NEW** | Model accuracy/F1 monitoring with threshold alerts |
| `app/models/retrain_model.py` | **NEW** | Automated XGBoost retraining with MLflow governance |
| `scripts/generate_production_data.py` | **NEW** | Seeds realistic production predictions with drift |
| `airflow/dags/drift_monitoring_pipeline.py` | **NEW** | Daily Airflow DAG: drift → evaluate → retrain → alert |
| `app/api/mlops.py` | **NEW** | 6 REST endpoints for the MLOps platform |
| `monitoring/grafana/dashboards/mlops_drift_retraining.json` | **NEW** | Grafana MLOps dashboard |
| `app/utils/metrics.py` | **MODIFIED** | +7 Prometheus drift & retraining metrics |
| `app/main.py` | **MODIFIED** | Registered MLOps API router |
| `data/production_predictions.csv` | **GENERATED** | 500-record production prediction log with drift |
| `reports/drift_report.json` | **GENERATED** | Drift detection report output |
| `reports/performance_report.json` | **GENERATED** | Performance monitoring report output |

## New API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/mlops/drift` | Run live drift detection |
| GET | `/api/v1/mlops/drift/latest` | Return last drift report |
| GET | `/api/v1/mlops/performance` | Run performance monitoring |
| POST | `/api/v1/mlops/retrain` | Trigger retraining (admin only) |
| GET | `/api/v1/mlops/retrain/history` | Retraining history log |
| GET | `/api/v1/mlops/status` | MLOps platform status overview |

## Complete MLOps Lifecycle

```
Customer Data
      ↓
  FastAPI
      ↓
Predictions → production_predictions.csv
      ↓
Performance Monitor (Accuracy, F1, Recall)
      ↓
Drift Detection (KS Test, 5 features)
      ↓
Airflow DAG (Daily 02:00 UTC)
      ↓
ShortCircuit Gate: Retrain only if needed
      ↓
XGBoost Retrain + MLflow Comparison
      ↓
New Model > Old Model? → Promote to Production
      ↓
MLflow Registry (Staging → Production → Archived)
      ↓
Alert (JSON Report → Slack/Email/PagerDuty)
      ↓
Grafana Dashboard (Drift Score, F1, Retraining)
```

## Key Concepts Learned

| Concept | Explanation |
|---------|-------------|
| **Data Drift** | Input distribution changes: MonthlyCharges μ shifted from $64.80 → $89.03 |
| **Concept Drift** | Relationship between inputs and outputs changes |
| **KS Test** | Non-parametric test measuring distribution distance; p < 0.05 = drift |
| **Model Governance** | Track what was deployed, when, why, and whether it improved |
| **ShortCircuit DAG** | Intelligent retraining — only runs when thresholds are breached |

## Outcomes

The ML platform is now self-monitoring and self-healing. It detects pricing shifts, behavioral changes, and seasonal effects automatically — then decides, with measurable evidence, whether the current model should be replaced. This closes the gap between model deployment and production reliability.
