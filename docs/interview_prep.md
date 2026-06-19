# Interview Preparation Guide
## Customer Churn Prediction & LTV Engine — 30-Day Capstone

---

## Elevator Pitch (30 seconds)

> "I built a production-grade Customer Churn Prediction and Lifetime Value Engine over 30 days. The system uses XGBoost and SHAP to predict which customers are likely to leave and why, exposes results through a FastAPI service with JWT authentication, caches predictions in Redis for a 96% latency reduction, and is deployed with Docker, Kubernetes, and AWS. Most importantly, it's a self-monitoring MLOps platform — it automatically detects when model performance degrades due to real-world data drift and triggers retraining using Apache Airflow and MLflow."

---

## System Design Questions

### Q: Walk me through your overall architecture.

**Answer:**
Customer data enters through the FastAPI service. The preprocessing layer cleans and one-hot encodes raw inputs, then applies feature engineering. Two ML models run in parallel: an XGBoost classifier for churn prediction and a Random Forest regressor for LTV estimation. SHAP generates human-readable explanations for each prediction. Results are logged to PostgreSQL, returned to the caller, and cached in Redis using a SHA-256 content-addressable key.

For monitoring, FastAPI exports Prometheus metrics, Grafana visualizes them, and Prometheus alert rules fire on latency, error rate, and model degradation. An Airflow DAG runs daily to detect data drift (using the Kolmogorov–Smirnov test), evaluate model performance, and conditionally trigger retraining.

---

### Q: Why PostgreSQL? Why not MySQL or MongoDB?

**Answer:**
PostgreSQL was chosen because:
1. **ACID compliance** — prediction logs must be reliable and consistent
2. **Advanced indexing** — partial indexes and composite indexes for dashboard queries
3. **JSON support** — could store SHAP explanation payloads if needed
4. **AWS RDS compatibility** — managed Multi-AZ PostgreSQL for production
5. **SQLAlchemy ORM** — clean integration with FastAPI

---

### Q: Why XGBoost over Logistic Regression or Random Forest?

**Answer:**
All three were trained and compared. XGBoost won on the F1/precision tradeoff for churn because:
- **Handles class imbalance better** — churn is ~26% of the dataset, gradient boosting adapts
- **Feature interactions** — automatically captures non-linear relationships between tenure, charges, and contract type
- **Speed** — faster inference than Random Forest on the same feature set
- **MLflow experiment tracking** confirmed XGBoost outperformed alternatives on F1 score

Logistic Regression is still kept as a baseline — useful for explaining individual coefficient directions.

---

### Q: Why SHAP? What problem does it solve?

**Answer:**
ML models are "black boxes." A business analyst or customer success manager cannot act on "churn probability = 0.83" without knowing WHY. SHAP (SHapley Additive exPlanations) assigns each feature a contribution score that explains the gap between the model's average prediction and this customer's specific prediction.

Example output:
- `tenure (-0.4)` → long customer, reducing churn risk
- `Contract_Month-to-month (+0.6)` → no lock-in, increasing churn risk
- `MonthlyCharges (+0.3)` → high charges, increasing risk

This enables targeted retention: "Offer this customer a 1-year contract discount."

---

### Q: How does your caching work?

**Answer:**
When a prediction request arrives, we serialize the input features into a deterministic sorted JSON string and hash it with SHA-256. The resulting hex digest is the Redis key. If a cache hit occurs, we return the stored result in ~2.82ms (vs. ~70ms for a fresh model inference — a 96% reduction).

The cache key includes a `CACHE_VERSION` prefix, so when a new model is deployed, we increment the version and all old keys are effectively invalidated without needing to flush Redis.

Cache TTL is 3,600 seconds. Redis eviction policy is `allkeys-lru` with a 256 MB memory limit.

---

### Q: Explain your drift detection approach.

**Answer:**
I use the **Kolmogorov–Smirnov (KS) test**, a non-parametric statistical test that measures the maximum difference between two cumulative distribution functions. It doesn't assume a normal distribution, which makes it robust for real-world data.

For each monitored feature (tenure, MonthlyCharges, TotalCharges, RevenuePerMonth, EngagementScore), I compare the training distribution against the production prediction distribution. A p-value < 0.05 indicates statistically significant drift.

**Demonstrated result:** MonthlyCharges drifted from μ=$64.80 in training to μ=$89.03 in production (a simulated +35% pricing shift), with KS=0.37 and p≈0.000 — drift clearly detected.

Retraining is triggered when 2+ features show drift, balancing sensitivity against unnecessary retraining costs.

---

### Q: How does your retraining pipeline decide whether to deploy the new model?

**Answer:**
After retraining, the new model's F1 score is compared against the currently-deployed Production model's F1 score (retrieved from MLflow). The new model is only promoted to Production if:
- No Production model exists (first deployment), OR
- New F1 - Old F1 ≥ 0.005 (0.5 percentage point minimum improvement)

This prevents deploying a model that trained on new data but didn't actually improve. If the new model doesn't qualify, it's transitioned to "Archived" in MLflow for traceability — we still have the audit trail.

---

### Q: Why Airflow? Couldn't you use a cron job?

**Answer:**
A cron job runs a shell script. Airflow provides:
1. **DAG visualization** — see the full pipeline in a web UI
2. **Task-level retry** — if drift detection fails, only that task retries, not the whole pipeline
3. **ShortCircuitOperator** — intelligently skips downstream tasks (retraining) when not needed
4. **Execution history** — queryable logs for every run
5. **Dependency management** — retraining doesn't start until drift detection completes successfully
6. **Alerting hooks** — built-in email/Slack callbacks on failure

---

### Q: How did you secure the API?

**Answer:**
1. **JWT tokens** (HS256) with configurable expiry — every prediction endpoint requires a valid Bearer token
2. **RBAC** — admin endpoints (`/model-info`, `/retrain`, `/cache` delete, `/admin/users`) require the admin role
3. **Password hashing** — bcrypt via Passlib, never stored in plaintext
4. **Environment variables** — database credentials, JWT secrets via `.env` / Kubernetes Secrets, never committed to Git
5. **Non-root container** — Docker runs as UID 1001, not root
6. **Kubernetes NetworkPolicy** — pods can only communicate on required ports (8000, 5432, 6379)
7. **Nginx TLS termination** — HTTPS on the AWS deployment
8. **SQLAlchemy ORM** — parameterized queries, SQL injection impossible

---

## EDA Findings & Business Recommendations

### Top Churn Drivers (from analysis)
| Driver | Churn Rate | Recommendation |
|--------|-----------|----------------|
| Month-to-month contract | ~43% | Incentivize 1-year contracts |
| Fiber optic + no security add-ons | ~41% | Bundle security services |
| Tenure < 12 months | ~48% | Onboarding program for new customers |
| Electronic check payment | ~45% | Auto-pay discount programs |
| High MonthlyCharges + short tenure | High risk | Tiered pricing for new high-value customers |

### LTV Insights
- High-value customers (LTV > $5,000) represent 23% of the base but 60% of revenue
- Retention of 1 high-value customer = retention of 6 standard customers by revenue
- **Priority targeting**: High Value + High Risk segment first

---

## ML Model Justification

| Model | Reason Selected | When to Use |
|-------|----------------|-------------|
| Logistic Regression | Interpretable baseline, fast inference | When explainability > accuracy |
| Random Forest | Robust to overfitting, feature importance | Tabular data with noisy features |
| XGBoost | Best F1 on this dataset, handles imbalance | Production churn (deployed) |

---

## Demo Script (API Walkthrough)

```bash
# 1. Register
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","email":"demo@example.com","password":"demo1234"}'

# 2. Login
TOKEN=$(curl -s -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"demo1234"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 3. Predict (high-risk customer)
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @sample_request.json

# 4. Check MLOps status
curl http://localhost:8000/api/v1/mlops/status

# 5. Run drift detection
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/mlops/drift
```

---

## Viva Questions & Answers

### "What would you do differently with more time?"
1. Real-time Kafka stream for live churn scoring (not batch)
2. A/B testing framework to compare models in production traffic
3. Alembic migrations for schema versioning
4. Canary deployments instead of full rolling updates
5. OpenTelemetry distributed tracing across services

### "What is the business value of this system?"
Every 1% reduction in churn for a mid-size telecom (1M customers, $65 ARPU) = $780,000 annual revenue protected. The system makes data-driven retention decisions, focuses retention spend on highest-value customers, and adapts automatically as customer behavior changes.

### "How would you scale this to 10 million customers?"
1. Kafka for real-time prediction streams
2. Kubernetes HPA already in place (2–5 pods now, extend to 50+)
3. PostgreSQL read replicas for dashboard queries
4. Redis Cluster (not single node)
5. Batch prediction jobs for offline scoring
6. Feature store (Feast) for consistent feature computation

### "How do you know the model is still performing well in production?"
- Drift detection: KS test daily via Airflow
- Performance monitoring: F1/Accuracy computed when labels become available
- Prometheus alerts: `model_f1_score_current < 0.70` fires an alert
- Grafana dashboard: visual trend of model metrics over time
- Retraining log: full audit trail in `reports/retrain_log.json`

---

## LinkedIn Project Description

**Customer Churn Prediction & Lifetime Value Engine** | Python · FastAPI · XGBoost · MLOps

Built a 30-day enterprise ML platform that predicts customer churn and estimates lifetime value for telecom businesses. The system features XGBoost classification, SHAP explainability, FastAPI inference API with JWT authentication, Redis caching (96% latency reduction), and PostgreSQL logging — deployed with Docker, Kubernetes, and AWS EC2/RDS. The platform evolved into a self-monitoring MLOps system with automated drift detection (KS test), conditional model retraining via Apache Airflow, MLflow model registry governance, and Prometheus/Grafana production monitoring. Demonstrated self-healing infrastructure, zero-downtime rolling updates, and multi-AZ cloud deployment.

---

## Resume Bullet Points

- Built a production Customer Churn Prediction & LTV Engine using FastAPI, PostgreSQL, XGBoost, and SHAP, achieving 79.1% accuracy on telecom data with Redis prediction caching providing 96% latency reduction (70ms → 2.82ms)
- Designed and deployed a self-monitoring MLOps platform with automated data drift detection (Kolmogorov–Smirnov test), conditional model retraining (Airflow DAG), and MLflow Model Registry governance — reducing stale model risk without unnecessary retraining
- Deployed to AWS cloud using EC2, RDS Multi-AZ PostgreSQL, and Nginx reverse proxy; orchestrated to Kubernetes with Horizontal Pod Autoscaling (2–5 replicas), zero-downtime rolling updates, and self-healing pod management
- Implemented enterprise production stack: Prometheus/Grafana monitoring with 15+ custom metrics, structured JSON logging (ELK/Loki-compatible), multi-stage Docker builds (~5x image size reduction), database backup automation with SHA-256 integrity verification, and Locust load testing validated p95 latency < 500ms at 100 concurrent users
