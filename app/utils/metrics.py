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

# ── Redis Cache Metrics ──────────────────────────────────────────
cache_hits_total = Counter(
    "prediction_cache_hits_total",
    "Total prediction cache hits",
)

cache_misses_total = Counter(
    "prediction_cache_misses_total",
    "Total prediction cache misses",
)

cache_errors_total = Counter(
    "prediction_cache_errors_total",
    "Total Redis cache operation errors",
)

cache_hit_rate = Gauge(
    "prediction_cache_hit_rate",
    "Current prediction cache hit rate",
)

# ── Day 28: MLOps Drift & Retraining Metrics ────────────────────────────────

drift_features_detected = Gauge(
    "drift_features_detected_total",
    "Number of features with statistically significant data drift (KS test p < 0.05)",
)

drift_ks_statistic = Gauge(
    "drift_ks_statistic",
    "KS statistic for the most recently drifted feature (0 = identical, 1 = max drift)",
    ["feature"],
)

model_retraining_total = Counter(
    "model_retraining_total",
    "Total number of model retraining runs triggered",
    ["trigger_reason"],
)

model_deployed_total = Counter(
    "model_deployed_total",
    "Total number of times a retrained model was promoted to Production",
)

model_f1_score_gauge = Gauge(
    "model_f1_score_current",
    "Current deployed model F1 score (from most recent evaluation)",
)

model_accuracy_gauge = Gauge(
    "model_accuracy_current",
    "Current deployed model accuracy (from most recent evaluation)",
)
