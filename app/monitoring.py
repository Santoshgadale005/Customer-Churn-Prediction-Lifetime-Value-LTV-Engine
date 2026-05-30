from datetime import datetime

def log_prediction(customer_id, churn_prediction, ltv_prediction):
    return {
        "customer_id": customer_id,
        "timestamp": datetime.now().isoformat(),
        "churn_prediction": churn_prediction,
        "ltv_prediction": ltv_prediction
    }