from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

from app.monitoring import log_prediction, get_metrics
from app.api.predict import router as predict_router
from app.api.health import router as health_router
from app.auth import router as auth_router

app = FastAPI()

# Include routers
app.include_router(predict_router)
app.include_router(health_router)
app.include_router(auth_router)

# Optional: monitoring endpoint (if you use it)
@app.get("/metrics")
def metrics():
    return get_metrics()