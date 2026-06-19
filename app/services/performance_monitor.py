"""
Performance Monitor — Day 28: Advanced MLOps

Tracks model quality metrics over time by comparing stored predictions
against actual outcomes (when available). Defines retraining thresholds
and emits Prometheus-compatible gauges for Grafana dashboards.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Optional

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)

logger = logging.getLogger(__name__)

PRODUCTION_DATA_PATH = "data/production_predictions.csv"
PERFORMANCE_REPORT_PATH = "reports/performance_report.json"

# Retraining thresholds — retrain if ANY of these are breached
F1_THRESHOLD = 0.70          # F1 score below this triggers retraining
ACCURACY_THRESHOLD = 0.75    # Accuracy below this triggers retraining


def compute_performance_metrics(production_df: pd.DataFrame) -> Optional[Dict]:
    """
    Compute churn model accuracy metrics from production data.

    Requires both 'predicted_churn' and 'actual_churn' columns to be present.
    Returns None if actual labels are unavailable.
    """
    if "predicted_churn" not in production_df.columns:
        logger.warning("'predicted_churn' column missing from production data.")
        return None
    if "actual_churn" not in production_df.columns:
        logger.warning(
            "'actual_churn' column missing — cannot compute performance metrics. "
            "This is expected when ground-truth labels are not yet available."
        )
        return None

    labeled = production_df.dropna(subset=["actual_churn", "predicted_churn"])
    if len(labeled) < 10:
        logger.warning(f"Only {len(labeled)} labeled records — need at least 10.")
        return None

    y_true = labeled["actual_churn"].astype(int)
    y_pred = labeled["predicted_churn"].astype(int)

    accuracy  = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall    = recall_score(y_true, y_pred, zero_division=0)
    f1        = f1_score(y_true, y_pred, zero_division=0)

    metrics = {
        "labeled_records": int(len(labeled)),
        "accuracy":        round(float(accuracy),  4),
        "precision":       round(float(precision), 4),
        "recall":          round(float(recall),    4),
        "f1_score":        round(float(f1),        4),
    }
    logger.info(
        f"Performance — Accuracy={accuracy:.4f}  Precision={precision:.4f}  "
        f"Recall={recall:.4f}  F1={f1:.4f}  (n={len(labeled)})"
    )
    return metrics


def check_retraining_needed(metrics: Optional[Dict], drift_feature_count: int = 0) -> Dict:
    """
    Evaluate whether retraining should be triggered based on:
      1. Model performance metrics falling below thresholds
      2. Significant data drift detected across multiple features

    Returns a dict with 'should_retrain' and the triggering reasons.
    """
    reasons = []

    if metrics is not None:
        if metrics["f1_score"] < F1_THRESHOLD:
            reasons.append(
                f"F1 Score {metrics['f1_score']:.4f} < threshold {F1_THRESHOLD}"
            )
        if metrics["accuracy"] < ACCURACY_THRESHOLD:
            reasons.append(
                f"Accuracy {metrics['accuracy']:.4f} < threshold {ACCURACY_THRESHOLD}"
            )

    from app.services.drift_detection import DRIFT_FEATURE_COUNT_THRESHOLD
    if drift_feature_count >= DRIFT_FEATURE_COUNT_THRESHOLD:
        reasons.append(
            f"Data drift detected in {drift_feature_count} features "
            f"(threshold: {DRIFT_FEATURE_COUNT_THRESHOLD})"
        )

    should_retrain = len(reasons) > 0

    return {
        "should_retrain": should_retrain,
        "reasons": reasons,
        "f1_threshold": F1_THRESHOLD,
        "accuracy_threshold": ACCURACY_THRESHOLD,
        "drift_feature_threshold": DRIFT_FEATURE_COUNT_THRESHOLD,
    }


def run_performance_monitoring() -> Dict:
    """
    Full performance monitoring pipeline.

    1. Load production prediction data
    2. Compute metrics (if actual labels are available)
    3. Check retraining thresholds
    4. Save and return the report
    """
    logger.info("Starting Performance Monitoring")

    if not os.path.exists(PRODUCTION_DATA_PATH):
        logger.warning(f"Production data not found at {PRODUCTION_DATA_PATH}")
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "skipped",
            "reason": "Production predictions file does not exist yet.",
        }
        return report

    production_df = pd.read_csv(PRODUCTION_DATA_PATH)
    logger.info(f"Loaded {len(production_df)} production records")

    metrics = compute_performance_metrics(production_df)
    retraining = check_retraining_needed(metrics)

    # Prediction distribution stats (always available)
    dist_stats = {}
    if "predicted_churn" in production_df.columns:
        churn_rate = production_df["predicted_churn"].mean()
        dist_stats = {
            "total_predictions": int(len(production_df)),
            "predicted_churn_rate": round(float(churn_rate), 4),
            "predicted_churn_count": int(production_df["predicted_churn"].sum()),
        }

    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "evaluated" if metrics else "no_labels",
        "prediction_distribution": dist_stats,
        "performance_metrics": metrics,
        "retraining_decision": retraining,
    }

    os.makedirs("reports", exist_ok=True)
    with open(PERFORMANCE_REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Performance report saved: {PERFORMANCE_REPORT_PATH}")
    logger.info(f"Should retrain: {retraining['should_retrain']}")
    for reason in retraining["reasons"]:
        logger.warning(f"  → {reason}")

    return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    report = run_performance_monitoring()
    print(json.dumps(report, indent=2))
