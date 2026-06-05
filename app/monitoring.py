"""
Monitoring module — upgraded to emit Prometheus metrics.

Keeps backward-compatible get_metrics() helper for the /metrics JSON endpoint
and exposes Prometheus counters/gauges that are scraped by Prometheus.
"""

from app.utils.metrics import (
    prediction_requests_total,
    churn_predictions_total,
    non_churn_predictions_total,
    churn_rate_gauge,
)

# In-memory fallback counters (used by the simple JSON metrics view)
_total = 0
_churn = 0
_non_churn = 0


def log_prediction(prediction: int):
    """Increment all relevant counters for a single prediction."""
    global _total, _churn, _non_churn

    _total += 1
    prediction_requests_total.inc()

    if prediction == 1:
        _churn += 1
        churn_predictions_total.inc()
    else:
        _non_churn += 1
        non_churn_predictions_total.inc()

    # Update running churn rate gauge
    if _total > 0:
        churn_rate_gauge.set(_churn / _total)


def get_metrics() -> dict:
    """Return a simple JSON summary of prediction counts."""
    return {
        "total_predictions": _total,
        "churn_predictions": _churn,
        "non_churn_predictions": _non_churn,
        "churn_rate": round(_churn / _total, 4) if _total > 0 else 0.0,
    }