from fastapi import FastAPI
from app.api.predict import router as predict_router
from app.api.health import router as health_router
from app.auth import router as auth_router

app = FastAPI(title="Customer Churn & LTV Prediction Engine", version="1.0.0")

app.include_router(health_router)
app.include_router(predict_router)
app.include_router(auth_router)

@app.get("/")
def home():
    return {"message": "API Working Successfully"}