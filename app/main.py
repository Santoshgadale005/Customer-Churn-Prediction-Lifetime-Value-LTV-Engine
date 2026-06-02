from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.predict import router as predict_router
from app.database.database import Base, engine
from app.monitoring import get_metrics

app = FastAPI(title="Customer Churn & LTV Prediction Engine", version="1.0.0")

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(predict_router)


@app.get("/")
def home():
    return {"message": "API Working Successfully"}


@app.get("/metrics")
def metrics():
    return get_metrics()


@app.on_event("startup")
def create_database_tables():
    try:
        from app.database import models, user_model  # noqa: F401

        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        print(f"Database table creation skipped: {exc}")
