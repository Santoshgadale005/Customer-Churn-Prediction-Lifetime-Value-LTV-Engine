import joblib
import pandas as pd
from app.database.models import PredictionLog
from app.monitoring import log_prediction as log_prediction_metrics
from app.services.preprocessing import preprocess_customer
from app.services.feature_engineering import engineer_features

churn_model = joblib.load("app/models/xgboost_model.pkl")
ltv_model = joblib.load("app/models/ltv_prediction_model.pkl")

def predict_customer_intelligence(data, db, current_user=None):
    # Use preprocessing to ensure all 30 features are present
    features = preprocess_customer(data)
    
    # Apply advanced behavioral feature engineering
    features = engineer_features(features)
    
    churn_prediction = churn_model.predict(features)[0]
    churn_probability = churn_model.predict_proba(features)[0][1]
    
    predicted_ltv = ltv_model.predict(features)[0]
    
    if churn_probability > 0.7 and predicted_ltv > 5000:
        segment = "High Value - High Risk"
    elif churn_probability > 0.7:
        segment = "Low Value - High Risk"
    elif predicted_ltv > 5000:
        segment = "High Value - Low Risk"
    else:
        segment = "Standard Customer"
        
    if segment == "High Value - High Risk":
        recommendation = "Immediate retention action required"
    elif segment == "Low Value - High Risk":
        recommendation = "Low-cost retention strategy"
    elif segment == "High Value - Low Risk":
        recommendation = "Maintain premium engagement"
    else:
        recommendation = "Standard monitoring"
        
    # Log prediction to PostgreSQL
    log = PredictionLog(
        gender=data.get("gender", str(data.get("gender_Male", "Unknown"))),
        tenure=data.get("tenure", 0),
        monthly_charges=data.get("MonthlyCharges", 0.0),
        total_charges=data.get("TotalCharges", 0.0),
        prediction=int(churn_prediction),
        churn_probability=float(churn_probability),
        predicted_ltv=float(predicted_ltv),
        customer_segment=segment,
        recommendation=recommendation,
        user_id=getattr(current_user, "id", None)
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    log_prediction_metrics(int(churn_prediction))
    
    return {
        "churn_prediction": int(churn_prediction),
        "churn_probability": float(churn_probability),
        "predicted_ltv": float(predicted_ltv),
        "customer_segment": segment,
        "recommendation": recommendation
    }
