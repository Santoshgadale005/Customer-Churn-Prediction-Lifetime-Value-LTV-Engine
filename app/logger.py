"""
Structured Logging — Day 29: Production Optimization

Replaces ad-hoc print() calls and the basic logging config with a
JSON-structured logger that:
  - Emits structured JSON to stdout (Grafana Loki / ELK compatible)
  - Writes human-readable logs to logs/app.log for local debugging
  - Provides convenience loggers per sub-system
  - Supports correlation IDs for tracing requests end-to-end
"""

import json
import logging
import logging.handlers
import os
import sys
import traceback
from datetime import datetime, timezone
from typing import Any, Dict, Optional


# ── Environment ──────────────────────────────────────────────────────────────
LOG_LEVEL  = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.environ.get("LOG_FORMAT", "json")   # "json" or "text"
LOG_DIR    = "logs"
os.makedirs(LOG_DIR, exist_ok=True)


# ── JSON Formatter ────────────────────────────────────────────────────────────
class JSONFormatter(logging.Formatter):
    """
    Emits each log record as a single-line JSON object.
    Compatible with Grafana Loki, ELK Stack, and GCP Cloud Logging.
    """

    SERVICE_NAME = "churn-ltv-engine"

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level":     record.levelname,
            "logger":    record.name,
            "service":   self.SERVICE_NAME,
            "message":   record.getMessage(),
            "module":    record.module,
            "function":  record.funcName,
            "line":      record.lineno,
        }

        # Attach extra fields pushed via logger.extra
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "taskName",
            ):
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
            payload["traceback"] = traceback.format_exception(*record.exc_info)

        return json.dumps(payload, default=str)


# ── Text Formatter (human-readable for local dev) ────────────────────────────
TEXT_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(funcName)s:%(lineno)d | %(message)s"
)

# ── Root Logger Setup ─────────────────────────────────────────────────────────

def _build_handler(stream, use_json: bool) -> logging.StreamHandler:
    handler = logging.StreamHandler(stream)
    handler.setFormatter(JSONFormatter() if use_json else logging.Formatter(TEXT_FORMAT))
    return handler


def configure_logging() -> None:
    """
    Call once at application startup to configure the root logger.
    All module-level loggers created via get_logger() inherit this config.
    """
    use_json = LOG_FORMAT == "json"

    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)
    root.handlers.clear()

    # 1. Structured stdout handler (Loki / ELK ingestion)
    root.addHandler(_build_handler(sys.stdout, use_json=use_json))

    # 2. Rotating file handler — human-readable for local debugging
    file_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(LOG_DIR, "app.log"),
        maxBytes=10 * 1024 * 1024,   # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter(TEXT_FORMAT))
    root.addHandler(file_handler)

    # 3. Separate error log file
    error_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(LOG_DIR, "errors.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(TEXT_FORMAT))
    root.addHandler(error_handler)

    # Silence noisy third-party loggers
    for noisy in ("uvicorn.access", "sqlalchemy.engine", "httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger. Call from any module: logger = get_logger(__name__)"""
    return logging.getLogger(name)


# ── Convenience helpers ───────────────────────────────────────────────────────

def log_prediction_event(
    logger: logging.Logger,
    *,
    customer_id: Optional[str] = None,
    churn_prediction: int,
    churn_probability: float,
    predicted_ltv: float,
    segment: str,
    cache_hit: bool = False,
    user_id: Optional[int] = None,
    latency_ms: Optional[float] = None,
) -> None:
    """Structured log for every prediction — queryable in Loki / ELK."""
    logger.info(
        "prediction_completed",
        extra={
            "event":             "prediction",
            "customer_id":       customer_id,
            "churn_prediction":  churn_prediction,
            "churn_probability": round(churn_probability, 4),
            "predicted_ltv":     round(float(predicted_ltv), 2),
            "segment":           segment,
            "cache_hit":         cache_hit,
            "user_id":           user_id,
            "latency_ms":        latency_ms,
        },
    )


def log_security_event(
    logger: logging.Logger,
    *,
    event_type: str,
    username: Optional[str] = None,
    ip_address: Optional[str] = None,
    success: bool = True,
    detail: Optional[str] = None,
) -> None:
    """Structured log for authentication and authorization events."""
    level = logging.INFO if success else logging.WARNING
    logger.log(
        level,
        f"security_{event_type}",
        extra={
            "event":      f"security_{event_type}",
            "username":   username,
            "ip_address": ip_address,
            "success":    success,
            "detail":     detail,
        },
    )


def log_drift_event(
    logger: logging.Logger,
    *,
    status: str,
    drifted_features: list,
    recommend_retraining: bool,
) -> None:
    """Structured log for drift detection results."""
    level = logging.WARNING if status == "drift_detected" else logging.INFO
    logger.log(
        level,
        f"drift_detection_{status}",
        extra={
            "event":                "drift_detection",
            "status":               status,
            "drifted_features":     drifted_features,
            "recommend_retraining": recommend_retraining,
        },
    )


# Initialize on import
configure_logging()

# Legacy shim — keeps existing `from app.logger import log_prediction` calls working
def log_prediction(message: str) -> None:
    """Backward-compatible shim for legacy callers."""
    get_logger("app.legacy").info(message, extra={"event": "legacy_log"})
