"""
Drift Detection Service — Day 28: Advanced MLOps

Detects data drift between the training distribution and the production
prediction distribution using the Kolmogorov–Smirnov (KS) statistical test.

A p-value < 0.05 indicates statistically significant drift in that feature.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from scipy.stats import ks_2samp

logger = logging.getLogger(__name__)

# Features to monitor for data drift
MONITORED_FEATURES = [
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
    "RevenuePerMonth",
    "EngagementScore",
]

TRAINING_DATA_PATH = "data/engineered_telco_data.csv"
PRODUCTION_DATA_PATH = "data/production_predictions.csv"
DRIFT_REPORT_PATH = "reports/drift_report.json"

# Threshold: p-value below this means drift is detected
DRIFT_P_VALUE_THRESHOLD = 0.05

# Alert threshold: trigger retraining if this many features have drift
DRIFT_FEATURE_COUNT_THRESHOLD = 2


def load_training_data() -> pd.DataFrame:
    """Load the baseline training dataset."""
    if not os.path.exists(TRAINING_DATA_PATH):
        raise FileNotFoundError(f"Training data not found: {TRAINING_DATA_PATH}")
    df = pd.read_csv(TRAINING_DATA_PATH)
    logger.info(f"Loaded training data: {len(df)} rows, {len(df.columns)} cols")
    return df


def load_production_data() -> Optional[pd.DataFrame]:
    """Load the production predictions dataset (may not exist yet)."""
    if not os.path.exists(PRODUCTION_DATA_PATH):
        logger.warning(f"Production data not found: {PRODUCTION_DATA_PATH}")
        return None
    df = pd.read_csv(PRODUCTION_DATA_PATH)
    logger.info(f"Loaded production data: {len(df)} rows")
    return df


def detect_feature_drift(
    training_series: pd.Series,
    production_series: pd.Series,
    feature_name: str,
) -> Dict:
    """
    Run the KS test between training and production distributions for a single feature.

    Returns a dictionary with:
        - feature: feature name
        - ks_statistic: KS distance (0=identical, 1=maximally different)
        - p_value: statistical significance
        - drift_detected: True if p_value < threshold
        - severity: 'none' | 'low' | 'medium' | 'high'
    """
    # Drop NaN values before testing
    train = training_series.dropna()
    prod = production_series.dropna()

    if len(train) == 0 or len(prod) == 0:
        logger.warning(f"Skipping {feature_name}: insufficient data after NaN removal")
        return {
            "feature": feature_name,
            "ks_statistic": None,
            "p_value": None,
            "drift_detected": False,
            "severity": "unknown",
            "train_mean": None,
            "prod_mean": None,
            "train_std": None,
            "prod_std": None,
        }

    statistic, p_value = ks_2samp(train, prod)
    drift_detected = p_value < DRIFT_P_VALUE_THRESHOLD

    # Classify severity by KS statistic
    if not drift_detected:
        severity = "none"
    elif statistic < 0.1:
        severity = "low"
    elif statistic < 0.3:
        severity = "medium"
    else:
        severity = "high"

    result = {
        "feature": feature_name,
        "ks_statistic": round(float(statistic), 6),
        "p_value": round(float(p_value), 6),
        "drift_detected": bool(drift_detected),
        "severity": severity,
        "train_mean": round(float(train.mean()), 4),
        "prod_mean": round(float(prod.mean()), 4),
        "train_std": round(float(train.std()), 4),
        "prod_std": round(float(prod.std()), 4),
    }

    status = "⚠️  DRIFT DETECTED" if drift_detected else "✅ No Drift"
    logger.info(
        f"[{feature_name}] {status} | KS={statistic:.4f} | p={p_value:.4f} | "
        f"Train μ={train.mean():.2f} → Prod μ={prod.mean():.2f}"
    )
    return result


def run_drift_detection() -> Dict:
    """
    Run drift detection across all monitored features.

    Returns a full drift report including:
        - per-feature results
        - overall drift summary
        - retraining recommendation
    """
    logger.info("=" * 60)
    logger.info("Starting Drift Detection Pipeline")
    logger.info("=" * 60)

    training_df = load_training_data()
    production_df = load_production_data()

    if production_df is None or len(production_df) < 10:
        logger.warning("Not enough production data to perform drift detection.")
        return {
            "status": "skipped",
            "reason": "Insufficient production data (minimum 10 records required)",
            "timestamp": datetime.utcnow().isoformat(),
        }

    feature_results = []
    drifted_features = []

    for feature in MONITORED_FEATURES:
        if feature not in training_df.columns:
            logger.warning(f"Feature '{feature}' not found in training data. Skipping.")
            continue
        if feature not in production_df.columns:
            logger.warning(f"Feature '{feature}' not found in production data. Skipping.")
            continue

        result = detect_feature_drift(
            training_df[feature],
            production_df[feature],
            feature,
        )
        feature_results.append(result)
        if result.get("drift_detected"):
            drifted_features.append(feature)

    # Determine overall drift status
    drift_count = len(drifted_features)
    overall_drift = drift_count >= DRIFT_FEATURE_COUNT_THRESHOLD
    recommend_retraining = overall_drift

    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "drift_detected" if overall_drift else "stable",
        "total_features_checked": len(feature_results),
        "features_with_drift": drift_count,
        "drifted_features": drifted_features,
        "recommend_retraining": recommend_retraining,
        "drift_threshold": DRIFT_P_VALUE_THRESHOLD,
        "retraining_trigger_threshold": DRIFT_FEATURE_COUNT_THRESHOLD,
        "feature_results": feature_results,
    }

    # Persist the report
    os.makedirs("reports", exist_ok=True)
    with open(DRIFT_REPORT_PATH, "w") as f:
        json.dump(report, f, indent=2)

    logger.info("=" * 60)
    logger.info(f"Drift Detection Complete")
    logger.info(f"  Features checked   : {len(feature_results)}")
    logger.info(f"  Features drifted   : {drift_count}")
    logger.info(f"  Overall status     : {report['status'].upper()}")
    logger.info(f"  Retrain recommended: {recommend_retraining}")
    logger.info(f"  Report saved to    : {DRIFT_REPORT_PATH}")
    logger.info("=" * 60)

    return report


def get_latest_drift_report() -> Optional[Dict]:
    """Load the most recently saved drift report."""
    if not os.path.exists(DRIFT_REPORT_PATH):
        return None
    with open(DRIFT_REPORT_PATH, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    report = run_drift_detection()
    print("\n=== DRIFT DETECTION REPORT ===")
    for r in report.get("feature_results", []):
        status = "⚠️  DRIFT" if r["drift_detected"] else "✅ OK   "
        print(
            f"  {status} | {r['feature']:<20} | "
            f"KS={r['ks_statistic']:.4f} | p={r['p_value']:.4f} | "
            f"Train μ={r['train_mean']} → Prod μ={r['prod_mean']}"
        )
    print(f"\nOverall: {report['status'].upper()}")
    print(f"Retrain Recommended: {report['recommend_retraining']}")
