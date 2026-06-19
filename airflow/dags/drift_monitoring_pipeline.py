"""
Drift Monitoring Airflow DAG — Day 28: Advanced MLOps

DAG: drift_monitoring_pipeline
Schedule: Daily at 02:00 UTC

Pipeline steps:
  1. collect_production_data    — ensure production predictions file is current
  2. detect_drift               — run KS test across monitored features
  3. evaluate_performance       — compute model metrics (if labels available)
  4. decide_retraining          — determine if retraining is warranted
  5. retrain_model              — execute retraining (skipped if not needed)
  6. register_model             — log result to MLflow registry
  7. send_alert                 — notify if drift or degradation detected
"""

import json
import logging
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator

logger = logging.getLogger(__name__)

# ── DAG Default Arguments ─────────────────────────────────────────────────────
default_args = {
    "owner": "mlops-team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


# ── Task Functions ─────────────────────────────────────────────────────────────

def collect_production_data(**context):
    """
    Ensure production predictions file exists and is up to date.
    In a real system this would query the prediction logging database.
    """
    production_path = "data/production_predictions.csv"
    if not os.path.exists(production_path):
        logger.warning("Production data file missing — running seed script")
        os.system("python scripts/generate_production_data.py")
    else:
        import pandas as pd
        df = pd.read_csv(production_path)
        logger.info(f"Production data found: {len(df)} records")
    context["ti"].xcom_push(key="production_data_path", value=production_path)


def detect_drift(**context):
    """Run KS-based drift detection across monitored features."""
    import sys
    sys.path.insert(0, os.getcwd())
    from app.services.drift_detection import run_drift_detection

    report = run_drift_detection()
    drift_count = report.get("features_with_drift", 0)
    recommend_retrain = report.get("recommend_retraining", False)
    drifted = report.get("drifted_features", [])

    logger.info(f"Drift Detection: {drift_count} features drifted → {drifted}")
    context["ti"].xcom_push(key="drift_report",          value=report)
    context["ti"].xcom_push(key="drift_feature_count",   value=drift_count)
    context["ti"].xcom_push(key="recommend_retraining",  value=recommend_retrain)
    context["ti"].xcom_push(key="drifted_features",      value=drifted)


def evaluate_performance(**context):
    """Compute model performance metrics from production data."""
    import sys
    sys.path.insert(0, os.getcwd())
    from app.services.performance_monitor import run_performance_monitoring

    drift_count = context["ti"].xcom_pull(
        task_ids="detect_drift", key="drift_feature_count"
    ) or 0

    report = run_performance_monitoring()
    retraining_decision = report.get("retraining_decision", {})
    should_retrain = retraining_decision.get("should_retrain", False)

    # Also consider drift as a retraining trigger
    from app.services.drift_detection import DRIFT_FEATURE_COUNT_THRESHOLD
    if drift_count >= DRIFT_FEATURE_COUNT_THRESHOLD:
        should_retrain = True

    context["ti"].xcom_push(key="performance_report",  value=report)
    context["ti"].xcom_push(key="should_retrain",      value=should_retrain)
    logger.info(f"Performance evaluation complete. Should retrain: {should_retrain}")


def decide_retraining(**context):
    """
    ShortCircuit gate: returns True only if retraining is warranted.
    When False, all downstream tasks are skipped cleanly.
    """
    should_retrain = context["ti"].xcom_pull(
        task_ids="evaluate_performance", key="should_retrain"
    )
    logger.info(f"Retraining gate: {'PROCEED' if should_retrain else 'SKIP'}")
    return bool(should_retrain)


def retrain_model_task(**context):
    """Execute model retraining pipeline."""
    import sys
    sys.path.insert(0, os.getcwd())
    from app.models.retrain_model import retrain_model

    drifted_features = context["ti"].xcom_pull(
        task_ids="detect_drift", key="drifted_features"
    ) or []
    trigger_reason = (
        f"airflow_scheduled_drift_in_{'+'.join(drifted_features)}"
        if drifted_features else "airflow_performance_degradation"
    )

    result = retrain_model(trigger_reason=trigger_reason)
    context["ti"].xcom_push(key="retrain_result", value=result)
    logger.info(f"Retraining complete. Deployed: {result.get('should_deploy')}")


def register_model(**context):
    """Log final model registry status (MLflow transitions handled inside retrain_model)."""
    retrain_result = context["ti"].xcom_pull(
        task_ids="retrain_model_task", key="retrain_result"
    ) or {}

    deployed = retrain_result.get("should_deploy", False)
    version  = retrain_result.get("mlflow_model_version")
    reason   = retrain_result.get("deployment_reason", "N/A")

    if deployed:
        logger.info(f"✅ New model v{version} promoted to Production")
    else:
        logger.info(f"⏸️  Model NOT promoted: {reason}")


def send_alert(**context):
    """
    Send alert notifications when drift or performance degradation is detected.

    In production this would integrate with:
      - Email (SMTP / SendGrid)
      - Slack Webhook
      - PagerDuty
      - Microsoft Teams
    """
    drift_report      = context["ti"].xcom_pull(task_ids="detect_drift",         key="drift_report")      or {}
    performance_report = context["ti"].xcom_pull(task_ids="evaluate_performance", key="performance_report") or {}
    retrain_result    = context["ti"].xcom_pull(task_ids="retrain_model_task",    key="retrain_result")    or {}

    should_retrain = context["ti"].xcom_pull(
        task_ids="evaluate_performance", key="should_retrain"
    )

    alert_payload = {
        "timestamp":          datetime.utcnow().isoformat(),
        "alert_type":         "mlops_drift_alert",
        "drift_status":       drift_report.get("status"),
        "drifted_features":   drift_report.get("drifted_features", []),
        "features_drifted":   drift_report.get("features_with_drift", 0),
        "retrain_triggered":  should_retrain,
        "retrain_deployed":   retrain_result.get("should_deploy", False),
        "new_model_metrics":  retrain_result.get("new_metrics"),
        "performance_status": performance_report.get("status"),
    }

    os.makedirs("reports", exist_ok=True)
    alert_path = f"reports/alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(alert_path, "w") as f:
        json.dump(alert_payload, f, indent=2)

    logger.info("=" * 50)
    logger.info("ALERT TRIGGERED")
    logger.info(f"  Drift Status       : {alert_payload['drift_status']}")
    logger.info(f"  Features Drifted   : {alert_payload['drifted_features']}")
    logger.info(f"  Retrain Triggered  : {alert_payload['retrain_triggered']}")
    logger.info(f"  Model Deployed     : {alert_payload['retrain_deployed']}")
    logger.info(f"  Alert saved to     : {alert_path}")
    logger.info("=" * 50)

    # ── Slack Webhook (uncomment and set SLACK_WEBHOOK_URL env var to enable) ──
    # import requests
    # webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    # if webhook_url:
    #     message = (
    #         f"*MLOps Alert* 🚨\n"
    #         f"• Drift: {alert_payload['drift_status']}\n"
    #         f"• Drifted Features: {alert_payload['drifted_features']}\n"
    #         f"• Retrain: {alert_payload['retrain_triggered']}\n"
    #         f"• Deployed: {alert_payload['retrain_deployed']}"
    #     )
    #     requests.post(webhook_url, json={"text": message}, timeout=10)


# ── DAG Definition ─────────────────────────────────────────────────────────────
with DAG(
    dag_id="drift_monitoring_pipeline",
    description="Automated MLOps: drift detection, performance monitoring, and model retraining",
    default_args=default_args,
    start_date=datetime(2025, 1, 1),
    schedule="0 2 * * *",   # Daily at 02:00 UTC
    catchup=False,
    tags=["mlops", "drift", "retraining", "monitoring"],
) as dag:

    collect_task = PythonOperator(
        task_id="collect_production_data",
        python_callable=collect_production_data,
    )

    drift_task = PythonOperator(
        task_id="detect_drift",
        python_callable=detect_drift,
    )

    performance_task = PythonOperator(
        task_id="evaluate_performance",
        python_callable=evaluate_performance,
    )

    # ShortCircuitOperator: skips retrain + register if not needed
    decide_task = ShortCircuitOperator(
        task_id="decide_retraining",
        python_callable=decide_retraining,
    )

    retrain_task = PythonOperator(
        task_id="retrain_model_task",
        python_callable=retrain_model_task,
    )

    register_task = PythonOperator(
        task_id="register_model",
        python_callable=register_model,
    )

    alert_task = PythonOperator(
        task_id="send_alert",
        python_callable=send_alert,
        trigger_rule="all_done",  # Always runs regardless of upstream skips
    )

    # ── Pipeline DAG ─────────────────────────────────────────────────────────
    (
        collect_task
        >> drift_task
        >> performance_task
        >> decide_task
        >> retrain_task
        >> register_task
        >> alert_task
    )

    # Alert also triggers directly from performance evaluation (not gated)
    performance_task >> alert_task
