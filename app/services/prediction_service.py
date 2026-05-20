import joblib
import pandas as pd
from app.database.models import PredictionLog
from app.services.preprocessing import preprocess_customer, get_risk_level

model = joblib.load("app/models/xgboost_model.pkl")

def predict_churn(data: dict, db):
    # Preprocess the data using existing robust preprocessor
    features = preprocess_customer(data)
    
    # Predict
    prediction = int(model.predict(features)[0])
    probability = float(model.predict_proba(features)[0][1])
    
    # Log prediction to PostgreSQL
    log = PredictionLog(
        gender=data.get("gender", str(data.get("gender_Male", "Unknown"))),
        tenure=data.get("tenure", 0),
        monthly_charges=data.get("MonthlyCharges", 0.0),
        total_charges=data.get("TotalCharges", 0.0),
        prediction=prediction,
        churn_probability=probability
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    
    risk = get_risk_level(probability)
    
    return {
        "prediction": prediction,
        "churn_probability": probability,
        "risk_level": risk
    }
