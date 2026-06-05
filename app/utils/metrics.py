"""
Prometheus metrics definitions.

All metric objects are defined here and imported where needed.
"""

from prometheus_client import Counter, Gauge, Histogram

# ── Request Counters ─────────────────────────────────────────────
api_requests_total = Counter(
    "api_requests_total",
    "Total number of API requests received",
    ["method", "endpoint", "status_code"],
)

api_errors_total = Counter(
    "api_errors_total",
    "Total number of API responses with status code 500 or higher",
    ["method", "endpoint", "status_code"],
)

prediction_requests_total = Counter(
    "prediction_requests_total",
    "Total number of prediction requests made",
)

churn_predictions_total = Counter(
    "churn_predictions_total",
    "Total customers predicted as churned",
)

non_churn_predictions_total = Counter(
    "non_churn_predictions_total",
    "Total customers predicted as NOT churned",
)

# ── Latency Histogram ────────────────────────────────────────────
request_duration_seconds = Histogram(
    "request_duration_seconds",
    "API endpoint response time in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# ── Business Gauges ──────────────────────────────────────────────
churn_rate_gauge = Gauge(
    "churn_rate_current",
    "Current running churn rate (churn / total predictions)",
)
