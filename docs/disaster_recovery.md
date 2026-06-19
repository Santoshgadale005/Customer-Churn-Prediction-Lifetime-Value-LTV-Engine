# Disaster Recovery & Production Readiness Guide

## Recovery Objectives

| Metric | Target | Notes |
|--------|--------|-------|
| **RTO** (Recovery Time Objective) | < 30 minutes | Time to restore full service |
| **RPO** (Recovery Point Objective) | < 24 hours | Maximum tolerable data loss |
| **MTTR** (Mean Time To Recovery) | < 15 minutes for code rollbacks | Rolling updates via K8s |

---

## Backup Locations

| Component | Backup Method | Location | Frequency |
|-----------|--------------|----------|-----------|
| PostgreSQL | `pg_dump` + gzip | `backups/database/` | Daily + Weekly |
| ML Models | `.pkl` files | `app/models/` + MLflow | Each training run |
| Grafana Dashboards | JSON exports | `monitoring/grafana/dashboards/` | Version-controlled |
| Application Config | Kubernetes Secrets/ConfigMaps | `k8s/` | Version-controlled |
| Prediction Logs | PostgreSQL (backed up above) | AWS RDS Multi-AZ | Continuous |

---

## Recovery Procedures

### 1. API Pods Crashed

```bash
# Check pod status
kubectl get pods

# View crash logs
kubectl logs <pod-name> --previous

# Kubernetes self-heals automatically — monitor recovery:
kubectl get pods --watch

# If image is bad, roll back to previous version:
kubectl rollout undo deployment/churn-api
kubectl rollout status deployment/churn-api
```

### 2. Database Recovery

```bash
# Restore from latest backup
gunzip -c backups/database/churn_ltv_db_daily_YYYYMMDD_HHMMSS.sql.gz | \
  psql -h localhost -U postgres -d churn_ltv_db

# Verify integrity before restore:
sha256sum -c backups/database/churn_ltv_db_daily_YYYYMMDD_HHMMSS.sql.gz.sha256
```

### 3. Model Rollback

```bash
# List all MLflow Production model versions
python - << 'EOF'
import mlflow
mlflow.set_tracking_uri("sqlite:///mlflow.db")
client = mlflow.tracking.MlflowClient()
versions = client.get_latest_versions("CustomerChurnModel", stages=["Production", "Archived"])
for v in versions:
    print(f"v{v.version} | {v.current_stage} | run={v.run_id}")
EOF

# Rollback: transition archived version back to Production
# Then copy the .pkl artifact to app/models/xgboost_model.pkl
```

### 4. Full Stack Recovery (Docker Compose)

```bash
# Stop all containers
docker-compose down

# Restore DB from backup (see step 2)

# Rebuild and restart
docker-compose up --build -d

# Verify health
curl http://localhost:8000/health
```

### 5. Full Stack Recovery (Kubernetes)

```bash
# Re-apply all manifests
kubectl apply -f k8s/

# Check all pods are running
kubectl get all

# Verify API is healthy
curl http://localhost:30080/health
```

---

## Production Readiness Checklist

### Scalability ✅
- [x] Kubernetes HPA: auto-scales 2–5 replicas on CPU/memory pressure
- [x] Redis caching: 96% latency reduction on repeated predictions
- [x] Multi-worker Uvicorn: 2 workers per container
- [x] Database indexes on churn_probability, customer_segment, created_at, user_id

### Security ✅
- [x] JWT authentication on all prediction endpoints
- [x] Role-based access control (admin vs. user roles)
- [x] Secrets managed via `.env` / Kubernetes Secrets (never hardcoded)
- [x] AWS Secrets Manager compatible via env-var injection
- [x] Non-root container user (UID 1001)
- [x] Network Policy: only ports 8000/5432/6379 allowed
- [x] HTTPS-ready via Nginx reverse proxy (AWS deployment)

### Monitoring ✅
- [x] Prometheus metrics: requests, errors, latency, churn rate
- [x] Grafana dashboards: Customer Intelligence + MLOps Drift
- [x] Prometheus alert rules: latency, error rate, API down, drift, model degradation
- [x] Structured JSON logging (Loki/ELK compatible)
- [x] Model performance gauges: F1 score, accuracy

### Recoverability ✅
- [x] Daily + weekly database backups with SHA-256 integrity verification
- [x] Kubernetes self-healing (pod restart policy: Always)
- [x] Rolling update strategy with zero downtime
- [x] MLflow model versioning: Staging → Production → Archived
- [x] Docker health check on `/health` endpoint

### MLOps ✅
- [x] Drift detection: KS test on 5 production features
- [x] Automated retraining: triggered when drift ≥ 2 features or F1 < 0.70
- [x] MLflow experiment tracking and model registry
- [x] Airflow daily pipeline: collect → detect → evaluate → retrain → alert

---

## Cost Optimization Strategy (AWS)

| Resource | Recommendation | Saving |
|----------|---------------|--------|
| EC2 | Use `t3.micro` (free tier) for dev/staging | ~$10/mo |
| RDS | Use `db.t3.micro` with single-AZ for non-prod | ~$15/mo |
| RDS Multi-AZ | Enable only for production | ~$0 dev |
| Unused environments | Stop EC2 when not in use | ~$8/mo |
| Data transfer | Use VPC endpoints to avoid egress costs | Varies |
| Savings Plans | 1-year commitment for predictable workloads | ~30% |

---

## Load Test Results

Run via: `locust -f scripts/load_test.py --host http://localhost:8000`

| Scenario | Users | Throughput | p95 Latency | Error Rate |
|----------|-------|-----------|-------------|------------|
| Baseline | 10 | ~40 req/s | ~85 ms | 0% |
| Moderate | 50 | ~120 req/s | ~210 ms | <0.1% |
| High | 100 | ~180 req/s | ~380 ms | <0.5% |
| Stress | 500 | ~210 req/s | ~490 ms | <1% |

> **Target**: p95 < 500ms ✅ | Error rate < 1% ✅

---

## Security Review Summary

| Area | Status | Detail |
|------|--------|--------|
| Authentication | ✅ Secure | JWT HS256 with expiry |
| Authorization | ✅ Secure | Admin RBAC for sensitive endpoints |
| Secrets | ✅ Secure | Environment variables, never committed |
| HTTPS | ✅ Ready | Nginx terminates TLS on AWS deployment |
| Container | ✅ Hardened | Non-root user, capability drop |
| Network | ✅ Restricted | Kubernetes NetworkPolicy |
| Database | ✅ Secure | Parameterized queries via SQLAlchemy |
| Dependencies | ⚠️ Monitor | Run `pip audit` regularly |
