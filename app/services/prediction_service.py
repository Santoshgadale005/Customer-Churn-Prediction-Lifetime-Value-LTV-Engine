import joblib
import pandas as pd
from app.database.models import PredictionLog
from app.monitoring import log_prediction as log_prediction_metrics
from app.services.preprocessing import preprocess_customer
from app.services.feature_engineering import engineer_features
from app.utils.cache import cache_prediction, get_cached_prediction

# Load models safely
try:
    churn_model = joblib.load("app/models/xgboost_model.pkl")
    ltv_model = joblib.load("app/models/ltv_prediction_model.pkl")
    MODELS_LOADED = True
except Exception as e:
    print(f"Model loading failed: {e}")
    churn_model = None
    ltv_model = None
    MODELS_LOADED = False


def predict_customer_intelligence(data, db, current_user=None):
    # Try to get from cache first
    try:
        cached_result = get_cached_prediction(data)
        if cached_result is not None:
            try:
                log_prediction_metrics(int(cached_result["churn_prediction"]))
            except Exception as metric_error:
                print(f"Metrics logging failed: {metric_error}")
            return {**cached_result, "cache_hit": True}
    except Exception as cache_error:
        print(f"Cache lookup failed: {cache_error}")

    # Demo mode if models fail to load
    if not MODELS_LOADED:
        return {
            "churn_prediction": 0,
            "churn_probability": 0.50,
            "predicted_ltv": 5000.0,
            "customer_segment": "Demo Mode",
            "recommendation": "Models could not be loaded",
            "cache_hit": False
        }

    # Preprocess customer data
    features = preprocess_customer(data)

    # Feature engineering
    features = engineer_features(features)

    # Predictions
    churn_prediction = churn_model.predict(features)[0]
    churn_probability = churn_model.predict_proba(features)[0][1]

    predicted_ltv = ltv_model.predict(features)[0]

    # Customer segmentation
    if churn_probability > 0.7 and predicted_ltv > 5000:
        segment = "High Value - High Risk"
    elif churn_probability > 0.7:
        segment = "Low Value - High Risk"
    elif predicted_ltv > 5000:
        segment = "High Value - Low Risk"
    else:
        segment = "Standard Customer"

    # Recommendation engine
    if segment == "High Value - High Risk":
        recommendation = "Immediate retention action required"
    elif segment == "Low Value - High Risk":
        recommendation = "Low-cost retention strategy"
    elif segment == "High Value - Low Risk":
        recommendation = "Maintain premium engagement"
    else:
        recommendation = "Standard monitoring"

    # Store prediction log
    try:
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

    except Exception as db_error:
        print(f"Database logging failed: {db_error}")

    try:
        log_prediction_metrics(int(churn_prediction))
    except Exception as metric_error:
        print(f"Metrics logging failed: {metric_error}")

    result = {
        "churn_prediction": int(churn_prediction),
        "churn_probability": float(churn_probability),
        "predicted_ltv": float(predicted_ltv),
        "customer_segment": segment,
        "recommendation": recommendation,
    }
    
    try:
        cache_prediction(data, result)
    except Exception as cache_error:
        print(f"Cache write failed: {cache_error}")

    return {**result, "cache_hit": False}

