from fastapi import FastAPI
from pydantic import BaseModel
from app.monitoring import log_prediction, get_metrics
import joblib
import numpy as np

app = FastAPI()

# Load model
model = joblib.load("app/models/logistic_regression_model.pkl")

class CustomerData(BaseModel):
    tenure: int
    MonthlyCharges: float
    TotalCharges: float

@app.get("/")
def home():
    return {"message": "API Working Successfully"}
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": True
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/predict")
def predict(data: CustomerData):

    features = np.array([[
        data.tenure,
        data.MonthlyCharges,
        data.TotalCharges
    ]])

    prediction = model.predict(features)[0]

    return {
        "prediction": int(prediction)
    }


@app.get("/metrics")
def metrics():
    return get_metrics()