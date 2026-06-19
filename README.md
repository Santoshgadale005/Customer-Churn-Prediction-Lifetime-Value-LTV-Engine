# Customer Churn Prediction & LTV Engine
## 30-Day Enterprise MLOps Capstone Project

**A production-grade machine learning platform** built over 30 days, demonstrating the complete lifecycle of an enterprise ML system — from raw data to cloud deployment with automated monitoring, drift detection, and self-healing retraining pipelines.

---

## 🏗️ Complete System Architecture

```
Customer Data (Telco CSV / API)
          │
          ▼
   PostgreSQL Database
          │
          ▼
   Data Preprocessing
   Feature Engineering
          │
     ┌────┴────┐
     ▼         ▼
 XGBoost    LTV Random
  Churn      Forest
  Model      Model
     └────┬────┘
          │
          ▼
       SHAP
  Explainability
          │
          ▼
      FastAPI
   (JWT + RBAC)
          │
     ┌────┴────┐
     ▼         ▼
  Redis      PostgreSQL
  Cache    Prediction Logs
          │
     ┌────┴────┐
     ▼         ▼
Metabase    Prometheus
Dashboard    + Grafana
          │
     ┌────┴────────┐
     ▼             ▼
  Docker/      AWS EC2
Kubernetes      + RDS
          │
          ▼
   MLOps Platform
  Drift Detection (KS Test)
  Automated Retraining
  MLflow Registry
  Airflow Orchestration
```

---

## ✨ Key Features

### Machine Learning
- Churn classification: Logistic Regression, Random Forest, XGBoost
- LTV regression: Random Forest Regressor
- SHAP explainability for every prediction
- MLflow experiment tracking and model registry

### API & Backend
- FastAPI with versioned endpoints (`/api/v1/`)
- JWT authentication + role-based access control (admin/user)
- Redis prediction caching (96% latency reduction)
- Batch prediction endpoint
- SHAP explanation endpoint

### MLOps (Days 21–28)
- **Drift Detection**: Kolmogorov–Smirnov test across 5 production features
- **Automated Retraining**: Triggered when drift ≥ 2 features or F1 < 0.70
- **MLflow Model Registry**: Staging → Production → Archived lifecycle
- **Apache Airflow DAG**: Daily drift monitoring and conditional retraining
- **Production Prediction Logging**: Full audit trail of every prediction

### Infrastructure
- **Docker + Docker Compose**: Full local stack in one command
- **Kubernetes**: Multi-replica, HPA auto-scaling (2–5 pods), self-healing
- **AWS Deployment**: EC2 + RDS + Nginx reverse proxy
- **Multi-Stage Dockerfile**: ~5x image size reduction

### Monitoring (Days 20–29)
- **Prometheus**: 15+ custom metrics (requests, latency, cache, churn rate, drift, model F1)
- **Grafana**: 2 dashboards (Customer Intelligence + MLOps Drift & Retraining)
- **Alert Rules**: High latency, error rate, API down, drift detected, model degradation
- **Structured JSON Logging**: Loki/ELK-compatible output

---

## 📊 Model Results

| Model | Metric | Value |
|-------|--------|------:|
| XGBoost Churn | Accuracy | 0.791 |
| XGBoost Churn | Precision | 0.633 |
| XGBoost Churn | Recall | 0.508 |
| XGBoost Churn | F1 Score | 0.564 |
| LTV Model | MAE | 1.089 |
| LTV Model | RMSE | 1.995 |
| LTV Model | R² | 0.9999 |

---

## 🔌 API Endpoints

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/health` | None | Service health check |
| GET | `/metrics` | None | Prometheus scrape endpoint |
| POST | `/register` | None | Create user account |
| POST | `/login` | None | JWT token |
| POST | `/api/v1/predict` | User | Single churn + LTV prediction |
| POST | `/api/v1/predict/explain` | User | SHAP explanation |
| POST | `/api/v1/predict/batch` | User | Batch predictions |
| GET | `/api/v1/predict/feature-importance` | User | Model feature importance |
| GET | `/api/v1/mlops/drift` | User | Live drift detection |
| GET | `/api/v1/mlops/status` | User | MLOps platform status |
| POST | `/api/v1/mlops/retrain` | Admin | Trigger retraining |
| GET | `/api/v1/mlops/retrain/history` | User | Retraining audit log |
| GET | `/api/v1/model-info` | Admin | Model metadata |
| DELETE | `/api/v1/cache` | Admin | Invalidate prediction cache |

---

## ⚡ Performance

| Metric | Value |
|--------|-------|
| Cold prediction latency | 70.82 ms |
| Cached prediction latency | 2.82 ms |
| Cache latency reduction | **96.01%** |
| p95 latency at 100 users | ~380 ms |
| Max throughput | ~210 req/sec |
| Cache TTL | 3,600 seconds |

---

## 🚀 Quick Start

```bash
# 1. Clone and set up
git clone https://github.com/Santoshgadale005/Customer-Churn-Prediction-Lifetime-Value-LTV-Engine
cd Customer-Churn-Prediction-Lifetime-Value-LTV-Engine

# 2. Create virtual environment
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Run locally
uvicorn app.main:app --reload

# 4. Full stack (Docker Compose)
docker-compose up --build

# 5. Generate production test data and run drift detection
python scripts/generate_production_data.py
python app/services/drift_detection.py
```

**Access Points (Docker Compose):**
- FastAPI Docs: http://localhost:8000/docs
- Metabase: http://localhost:3000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)
- Airflow: http://localhost:8080

---

## ☸️ Kubernetes Deployment

```bash
docker build -t churn-api:latest .
kubectl apply -f k8s/
kubectl get all
# Access: http://localhost:30080/docs
```

**K8s Features:**
- 2–5 auto-scaling replicas (HPA: CPU 70%, Memory 80%)
- Liveness + Readiness probes on `/health`
- Zero-downtime rolling updates
- PodDisruptionBudget: minimum 1 replica always available
- NetworkPolicy: least-privilege port access

---

## ☁️ AWS Cloud Deployment

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
chmod +x scripts/deploy_aws.sh && ./scripts/deploy_aws.sh
```

**Architecture:** EC2 (FastAPI + Redis + Metabase) + RDS PostgreSQL (Multi-AZ) + Nginx reverse proxy

---

## 🔁 MLOps Lifecycle

```
Train Model → Deploy → Monitor → Detect Drift → Retrain → Redeploy
     │                                              │
     └──────────────────────────────────────────────┘
              MLflow Model Registry governs every transition
```

**Automated daily Airflow DAG**: `drift_monitoring_pipeline`
1. Collect production data
2. KS-test drift detection (5 features)
3. Evaluate model performance (F1, Accuracy)
4. ShortCircuit gate: retrain only if needed
5. Compare old vs. new model
6. Promote if improved → MLflow Production
7. Send alert

---

## 🧪 Testing

```bash
# Unit and API tests
pytest tests/ -v

# Load testing (50 users)
locust -f scripts/load_test.py --host http://localhost:8000 \
       --headless --users 50 --spawn-rate 10 --run-time 60s

# Drift detection
python app/services/drift_detection.py

# Database backup
python scripts/db_backup.py
```

---

## 📁 Project Structure

```
customer-churn-ltv/
├── app/
│   ├── api/          # FastAPI routes (predict, auth, cache, mlops, health)
│   ├── database/     # SQLAlchemy models, indexes, connection
│   ├── models/       # ML models + retraining script
│   ├── services/     # Prediction, preprocessing, drift detection, performance monitor
│   └── utils/        # Redis cache, Prometheus metrics
├── airflow/dags/     # ETL pipeline + drift monitoring DAG
├── data/             # Training + production datasets
├── docs/             # Architecture diagrams, disaster recovery guide
├── k8s/              # Kubernetes manifests (deployment, HPA, secrets, network policy)
├── monitoring/       # Grafana dashboards, Prometheus alert rules
├── nginx/            # Nginx reverse proxy config
├── reports/          # Model results, drift reports, retrain logs
├── scripts/          # Load tests, backup, benchmarks, deployment
├── tests/            # Pytest API and model tests
├── Dockerfile        # Multi-stage production build
└── docker-compose.yml
```

---

## 🎯 Business Value

This system enables businesses to:
1. **Identify at-risk customers** before they leave
2. **Prioritize by revenue impact** using LTV estimates
3. **Understand WHY** a customer is flagged (SHAP explanations)
4. **Give non-technical teams** dashboard visibility
5. **Automatically adapt** when customer behavior changes (drift detection + retraining)

> "Instead of treating every customer the same, teams can focus incentives and outreach where they protect the most revenue."

---

## 📈 Tech Stack

Python · FastAPI · PostgreSQL · SQLAlchemy · XGBoost · Scikit-learn · SHAP · MLflow · Apache Airflow · Docker · Kubernetes · AWS (EC2 + RDS) · Nginx · Prometheus · Grafana · Redis · GitHub Actions · Pytest · Locust · SciPy

---

## 🔮 Future Improvements

- Real-time streaming with Apache Kafka
- Distributed tracing with OpenTelemetry
- Alembic database migrations
- Batch CSV upload endpoint for business analysts
- A/B model testing framework
- Advanced recommender system for retention offers
- SMS/Email/Slack alert notification channels

---

## 📝 License

MIT License — see LICENSE for details.
