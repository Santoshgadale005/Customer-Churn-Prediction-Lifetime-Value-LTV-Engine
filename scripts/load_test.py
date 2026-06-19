"""
Locust Load Test — Day 29: Performance Optimization

Usage:
    # Start Locust web UI (then open http://localhost:8089)
    locust -f scripts/load_test.py --host http://localhost:8000

    # Headless run (50 users, 10 spawn/sec, 60s duration)
    locust -f scripts/load_test.py --host http://localhost:8000 \
           --headless --users 50 --spawn-rate 10 --run-time 60s

    # Scale up to 100 users
    locust -f scripts/load_test.py --host http://localhost:8000 \
           --headless --users 100 --spawn-rate 20 --run-time 120s

Performance targets:
    - p95 response time  < 500 ms
    - Error rate         < 1%
    - Throughput         > 50 req/sec
"""

import json
import os
import random
from locust import HttpUser, SequentialTaskSet, TaskSet, between, task

# ── Sample payloads ───────────────────────────────────────────────────────────

SAMPLE_CUSTOMER = {
    "gender": "Male",
    "SeniorCitizen": 0,
    "Partner": "Yes",
    "Dependents": "No",
    "tenure": 24,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "OnlineBackup": "No",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "Yes",
    "StreamingMovies": "Yes",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 85.50,
    "TotalCharges": 2052.0,
}

SAMPLE_BATCH = {
    "customers": [
        {**SAMPLE_CUSTOMER, "tenure": random.randint(1, 72), "MonthlyCharges": random.uniform(20, 120)}
        for _ in range(5)
    ]
}

CREDENTIALS = {
    "username": os.environ.get("TEST_USERNAME", "santosh"),
    "password": os.environ.get("TEST_PASSWORD", "password123"),
}


# ── Task Sets ─────────────────────────────────────────────────────────────────

class PublicEndpointTasks(TaskSet):
    """Unauthenticated endpoints — high frequency."""

    @task(5)
    def health_check(self):
        with self.client.get("/health", catch_response=True, name="/health") as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Health check failed: {resp.status_code}")

    @task(2)
    def metrics_summary(self):
        self.client.get("/metrics/summary", name="/metrics/summary")

    @task(1)
    def mlops_status(self):
        self.client.get("/api/v1/mlops/status", name="/api/v1/mlops/status")


class AuthenticatedTasks(SequentialTaskSet):
    """Authenticated prediction endpoints — main load scenario."""

    token: str = ""

    def on_start(self):
        """Login once and store the JWT token."""
        resp = self.client.post(
            "/login",
            json=CREDENTIALS,
            name="/login",
        )
        if resp.status_code == 200:
            self.token = resp.json().get("access_token", "")
        else:
            self.token = ""

    def _auth_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    @task
    def predict_single(self):
        """Main prediction endpoint — most business-critical."""
        payload = {
            **SAMPLE_CUSTOMER,
            "tenure": random.randint(1, 72),
            "MonthlyCharges": round(random.uniform(20.0, 120.0), 2),
        }
        with self.client.post(
            "/api/v1/predict",
            json=payload,
            headers=self._auth_headers(),
            catch_response=True,
            name="/api/v1/predict",
        ) as resp:
            if resp.status_code in (200, 201):
                data = resp.json()
                if "churn_prediction" not in data and "churn_probability" not in data:
                    resp.failure("Response missing churn_prediction field")
                else:
                    resp.success()
            elif resp.status_code == 503:
                resp.failure("Model not loaded")
            else:
                resp.failure(f"Unexpected status {resp.status_code}")

    @task
    def predict_batch(self):
        """Batch prediction — heavier payload."""
        customers = [
            {**SAMPLE_CUSTOMER, "tenure": random.randint(1, 72)}
            for _ in range(3)
        ]
        self.client.post(
            "/api/v1/predict/batch",
            json={"customers": customers},
            headers=self._auth_headers(),
            name="/api/v1/predict/batch",
        )

    @task
    def feature_importance(self):
        """Feature importance — read-heavy, cacheable."""
        self.client.get(
            "/api/v1/predict/feature-importance",
            headers=self._auth_headers(),
            name="/api/v1/predict/feature-importance",
        )

    @task
    def drift_status(self):
        """Drift report endpoint."""
        self.client.get(
            "/api/v1/mlops/drift/latest",
            headers=self._auth_headers(),
            name="/api/v1/mlops/drift/latest",
        )


# ── User Classes ──────────────────────────────────────────────────────────────

class PublicUser(HttpUser):
    """Simulates anonymous monitoring probes and health checks."""
    tasks      = [PublicEndpointTasks]
    wait_time  = between(0.5, 2.0)
    weight     = 2    # 2× more common than authenticated users


class APIUser(HttpUser):
    """Simulates authenticated application clients making predictions."""
    tasks      = [AuthenticatedTasks]
    wait_time  = between(0.2, 1.0)
    weight     = 8    # 80% of traffic is authenticated predictions
