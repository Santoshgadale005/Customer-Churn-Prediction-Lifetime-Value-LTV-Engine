"""
MLOps Drift & Retraining API Endpoints — Day 28

Routes:
  GET  /api/v1/mlops/drift           — Run drift detection and return report
  GET  /api/v1/mlops/drift/latest    — Return the last saved drift report
  GET  /api/v1/mlops/performance     — Run performance monitoring
  POST /api/v1/mlops/retrain         — Manually trigger model retraining
  GET  /api/v1/mlops/retrain/history — View retraining history log
  GET  /api/v1/mlops/status          — Overall MLOps platform status
"""

import json
import logging
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.api.auth import require_admin

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/mlops", tags=["MLOps"])

DRIFT_REPORT_PATH      = "reports/drift_report.json"
PERFORMANCE_REPORT_PATH = "reports/performance_report.json"
RETRAIN_LOG_PATH       = "reports/retrain_log.json"


# ── Request / Response Schemas ─────────────────────────────────────────────────

class RetrainRequest(BaseModel):
    trigger_reason: str = "manual_api_trigger"


# ── Helper ─────────────────────────────────────────────────────────────────────

def _load_json(path: str) -> Optional[dict]:
    """Load a JSON file, returning None if it doesn't exist."""
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/drift", summary="Run live drift detection")
def run_drift_detection_endpoint():
    """
    Execute drift detection across all monitored features using the KS test.
    Compares the current production prediction distribution against training data.
    """
    try:
        from app.services.drift_detection import run_drift_detection
        report = run_drift_detection()
        return report
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Drift detection failed")
        raise HTTPException(status_code=500, detail=f"Drift detection error: {str(e)}")


@router.get("/drift/latest", summary="Return the most recent drift report")
def get_latest_drift_report():
    """Return the saved drift report from the last detection run."""
    report = _load_json(DRIFT_REPORT_PATH)
    if not report:
        raise HTTPException(
            status_code=404,
            detail="No drift report found. Run /api/v1/mlops/drift first.",
        )
    return report


@router.get("/performance", summary="Run model performance monitoring")
def run_performance_monitoring_endpoint():
    """
    Evaluate current model performance against production prediction data.
    Requires actual_churn labels in production_predictions.csv.
    """
    try:
        from app.services.performance_monitor import run_performance_monitoring
        report = run_performance_monitoring()
        return report
    except Exception as e:
        logger.exception("Performance monitoring failed")
        raise HTTPException(status_code=500, detail=f"Performance monitoring error: {str(e)}")


@router.post("/retrain", summary="Trigger model retraining (admin only)")
def trigger_retraining(
    request: RetrainRequest,
    background_tasks: BackgroundTasks,
    _: None = Depends(require_admin),
):
    """
    Manually trigger model retraining. Runs in the background to avoid
    blocking the API response. Results are logged to reports/retrain_log.json.
    Only admin users can trigger retraining.
    """
    def _retrain():
        try:
            from app.models.retrain_model import retrain_model
            result = retrain_model(trigger_reason=request.trigger_reason)
            logger.info(f"Background retraining complete: {result.get('should_deploy')}")
        except Exception as e:
            logger.exception(f"Background retraining failed: {e}")

    background_tasks.add_task(_retrain)
    return {
        "message": "Model retraining triggered in the background.",
        "trigger_reason": request.trigger_reason,
        "status": "queued",
        "result_path": RETRAIN_LOG_PATH,
    }


@router.get("/retrain/history", summary="View retraining history")
def get_retrain_history():
    """Return the full log of all retraining runs."""
    history = _load_json(RETRAIN_LOG_PATH)
    if not history:
        return {"message": "No retraining runs recorded yet.", "history": []}
    return {"total_runs": len(history), "history": history}


@router.get("/status", summary="MLOps platform status overview")
def get_mlops_status():
    """
    Returns a unified MLOps status dashboard view including:
    - Latest drift report summary
    - Latest performance report summary
    - Retraining history count
    - Overall health status
    """
    drift_report      = _load_json(DRIFT_REPORT_PATH)
    performance_report = _load_json(PERFORMANCE_REPORT_PATH)
    retrain_history   = _load_json(RETRAIN_LOG_PATH) or []

    status = {
        "mlops_status": "healthy",
        "drift": {
            "last_checked": drift_report.get("timestamp") if drift_report else None,
            "status":       drift_report.get("status")    if drift_report else "not_run",
            "drifted_features": drift_report.get("drifted_features", []) if drift_report else [],
            "recommend_retraining": drift_report.get("recommend_retraining", False) if drift_report else False,
        },
        "performance": {
            "last_checked": performance_report.get("timestamp") if performance_report else None,
            "status":       performance_report.get("status")    if performance_report else "not_run",
            "metrics":      (performance_report.get("performance_metrics") if performance_report else None),
        },
        "retraining": {
            "total_runs":  len(retrain_history),
            "last_run":    retrain_history[-1].get("timestamp") if retrain_history else None,
            "last_deployed": retrain_history[-1].get("should_deploy") if retrain_history else None,
        },
    }

    # Degrade overall status if drift or performance issues present
    if drift_report and drift_report.get("recommend_retraining"):
        status["mlops_status"] = "drift_detected"
    if performance_report:
        decision = performance_report.get("retraining_decision", {})
        if decision.get("should_retrain"):
            status["mlops_status"] = "performance_degraded"

    return status
