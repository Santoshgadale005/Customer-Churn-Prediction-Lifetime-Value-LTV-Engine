import time

from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.auth import router as auth_router
from app.api.cache import router as cache_router
from app.api.health import router as health_router
from app.api.predict import router as predict_router
from app.database.database import Base, engine
from app.database.indexes import ensure_prediction_indexes
from app.monitoring import get_metrics
from app.utils.metrics import (
    api_errors_total,
    api_requests_total,
    request_duration_seconds,
)

app = FastAPI(title="Customer Churn & LTV Prediction Engine", version="1.0.0")

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(cache_router)
app.include_router(predict_router)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    endpoint = request.url.path
    method = request.method
    status_code = str(response.status_code)

    api_requests_total.labels(method, endpoint, status_code).inc()
    request_duration_seconds.labels(method, endpoint).observe(duration)
    if response.status_code >= 500:
        api_errors_total.labels(method, endpoint, status_code).inc()

    return response


@app.get("/")
def home():
    return {"message": "API Working Successfully"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/metrics/summary")
def metrics_summary():
    return get_metrics()


@app.on_event("startup")
def create_database_tables():
    try:
        from app.database import models, user_model  # noqa: F401

        Base.metadata.create_all(bind=engine)
        ensure_prediction_indexes(engine)
    except Exception as exc:
        print(f"Database table creation skipped: {exc}")
