"""
Automated Model Retraining Script — Day 28: Advanced MLOps

Retrains the XGBoost churn model on the latest available data,
compares it against the previously deployed model, and registers
the new model to MLflow only if it improves performance.

MLflow Model Registry stages:
  Staging    → new model waiting for evaluation
  Production → currently serving model
  Archived   → superseded models
"""

import json
import logging
import os
import pickle
from datetime import datetime
from typing import Dict, Optional, Tuple

import joblib
import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

logger = logging.getLogger(__name__)

TRAINING_DATA_PATH = "data/engineered_telco_data.csv"
MODEL_OUTPUT_PATH  = "app/models/xgboost_model.pkl"
RETRAIN_LOG_PATH   = "reports/retrain_log.json"

MLFLOW_TRACKING_URI = "sqlite:///mlflow.db"
MLFLOW_EXPERIMENT   = "Customer_Churn_Prediction"
MLFLOW_MODEL_NAME   = "CustomerChurnModel"

# Only deploy if new model beats old model by this minimum improvement
MIN_F1_IMPROVEMENT = 0.005   # 0.5 percentage points


def load_training_data() -> Tuple[pd.DataFrame, pd.Series]:
    """Load and prepare features/labels from the engineered dataset."""
    df = pd.read_csv(TRAINING_DATA_PATH)

    target_col = "Churn"
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found in training data.")

    drop_cols = [target_col]
    for col in ["Customer Lifetime Value", "CLV"]:
        if col in df.columns:
            drop_cols.append(col)

    X = df.drop(columns=drop_cols)
    y = df[target_col]

    logger.info(f"Training data loaded: {len(df)} rows, {X.shape[1]} features")
    return X, y


def evaluate_model(model, X_test: pd.DataFrame, y_test: pd.Series) -> Dict:
    """Compute standard classification metrics for a fitted model."""
    predictions = model.predict(X_test)
    return {
        "accuracy":  round(float(accuracy_score(y_test,  predictions)), 4),
        "precision": round(float(precision_score(y_test, predictions, zero_division=0)), 4),
        "recall":    round(float(recall_score(y_test,    predictions, zero_division=0)), 4),
        "f1_score":  round(float(f1_score(y_test,        predictions, zero_division=0)), 4),
    }


def get_current_model_metrics() -> Optional[Dict]:
    """
    Retrieve the performance metrics of the currently deployed model
    from the most recent MLflow Production run, if available.
    """
    try:
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        client = mlflow.tracking.MlflowClient()
        versions = client.get_latest_versions(MLFLOW_MODEL_NAME, stages=["Production"])
        if not versions:
            logger.info("No Production model found in MLflow registry.")
            return None
        run_id = versions[0].run_id
        run = client.get_run(run_id)
        metrics = run.data.metrics
        logger.info(f"Current Production model metrics: {metrics}")
        return {
            "accuracy":  round(metrics.get("accuracy",  0.0), 4),
            "precision": round(metrics.get("precision", 0.0), 4),
            "recall":    round(metrics.get("recall",    0.0), 4),
            "f1_score":  round(metrics.get("f1_score",  0.0), 4),
        }
    except Exception as e:
        logger.warning(f"Could not fetch current model metrics from MLflow: {e}")
        return None


def retrain_model(trigger_reason: str = "manual") -> Dict:
    """
    Full retraining pipeline:
      1. Load latest data
      2. Train a new XGBoost model
      3. Evaluate against holdout set
      4. Compare to current production model
      5. Register to MLflow (Staging → Production if improved)
      6. Save .pkl artifact and retraining log
    """
    logger.info("=" * 60)
    logger.info(f"Retraining Triggered — Reason: {trigger_reason}")
    logger.info("=" * 60)

    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment(MLFLOW_EXPERIMENT)

    X, y = load_training_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Hyperparameters (can be tuned or retrieved from Optuna/grid search)
    params = {
        "n_estimators":  300,
        "learning_rate": 0.05,
        "max_depth":     6,
        "subsample":     0.8,
        "colsample_bytree": 0.8,
        "random_state":  42,
        "eval_metric":   "logloss",
    }

    new_model = XGBClassifier(**params)

    run_name = f"retrain_{trigger_reason}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_param("trigger_reason", trigger_reason)
        mlflow.log_param("model_type", "xgboost")
        mlflow.log_param("train_size", len(X_train))
        for k, v in params.items():
            mlflow.log_param(k, v)

        logger.info("Training new XGBoost model...")
        new_model.fit(X_train, y_train)

        new_metrics = evaluate_model(new_model, X_test, y_test)
        logger.info(f"New model metrics: {new_metrics}")

        for metric_name, value in new_metrics.items():
            mlflow.log_metric(metric_name, value)

        # Register new model to MLflow (lands in None/Staging by default)
        mlflow.sklearn.log_model(
            new_model,
            artifact_path="model",
            registered_model_name=MLFLOW_MODEL_NAME,
        )
        new_run_id = run.info.run_id

    # Compare against current production model
    current_metrics = get_current_model_metrics()
    should_deploy    = False
    deployment_reason = ""

    if current_metrics is None:
        should_deploy    = True
        deployment_reason = "No existing production model found — deploying automatically."
    else:
        f1_improvement = new_metrics["f1_score"] - current_metrics["f1_score"]
        logger.info(
            f"F1 comparison — Current: {current_metrics['f1_score']:.4f}  "
            f"New: {new_metrics['f1_score']:.4f}  "
            f"Δ: {f1_improvement:+.4f}"
        )
        if f1_improvement >= MIN_F1_IMPROVEMENT:
            should_deploy    = True
            deployment_reason = f"New model F1 improved by {f1_improvement:+.4f}"
        else:
            deployment_reason = (
                f"New model F1 did not improve sufficiently "
                f"(Δ={f1_improvement:+.4f} < min {MIN_F1_IMPROVEMENT}). "
                "Keeping current production model."
            )

    # Transition MLflow model stage
    client = mlflow.tracking.MlflowClient()
    latest_versions = client.get_latest_versions(MLFLOW_MODEL_NAME, stages=["None", "Staging"])
    new_version = max(latest_versions, key=lambda v: int(v.version)).version if latest_versions else None

    if new_version:
        if should_deploy:
            # Archive old production model
            prod_versions = client.get_latest_versions(MLFLOW_MODEL_NAME, stages=["Production"])
            for pv in prod_versions:
                client.transition_model_version_stage(
                    name=MLFLOW_MODEL_NAME,
                    version=pv.version,
                    stage="Archived",
                )
                logger.info(f"Archived previous Production model v{pv.version}")

            client.transition_model_version_stage(
                name=MLFLOW_MODEL_NAME,
                version=new_version,
                stage="Production",
            )
            logger.info(f"✅ Promoted model v{new_version} to Production")

            # Save updated .pkl for FastAPI
            joblib.dump(new_model, MODEL_OUTPUT_PATH)
            logger.info(f"Saved new model artifact: {MODEL_OUTPUT_PATH}")
        else:
            client.transition_model_version_stage(
                name=MLFLOW_MODEL_NAME,
                version=new_version,
                stage="Archived",
            )
            logger.info(f"Model v{new_version} kept in Archived (did not improve)")

    result = {
        "timestamp":       datetime.utcnow().isoformat(),
        "trigger_reason":  trigger_reason,
        "run_id":          new_run_id,
        "new_metrics":     new_metrics,
        "current_metrics": current_metrics,
        "should_deploy":   should_deploy,
        "deployment_reason": deployment_reason,
        "mlflow_model_version": new_version,
    }

    os.makedirs("reports", exist_ok=True)
    # Append to the retrain log
    log_entries = []
    if os.path.exists(RETRAIN_LOG_PATH):
        with open(RETRAIN_LOG_PATH, "r") as f:
            log_entries = json.load(f)
    log_entries.append(result)
    with open(RETRAIN_LOG_PATH, "w") as f:
        json.dump(log_entries, f, indent=2)

    logger.info("=" * 60)
    logger.info(f"Retraining Complete")
    logger.info(f"  Deployed: {should_deploy}")
    logger.info(f"  Reason  : {deployment_reason}")
    logger.info("=" * 60)

    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
    result = retrain_model(trigger_reason="manual_trigger")
    print("\n=== RETRAINING RESULT ===")
    print(json.dumps(result, indent=2))
