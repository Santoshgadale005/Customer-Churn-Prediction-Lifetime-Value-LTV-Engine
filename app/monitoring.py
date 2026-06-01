prediction_count = 0
churn_count = 0
non_churn_count = 0

def log_prediction(prediction):
    global prediction_count, churn_count, non_churn_count

    prediction_count += 1

    if prediction == 1:
        churn_count += 1
    else:
        non_churn_count += 1


def get_metrics():
    return {
        "total_predictions": prediction_count,
        "churn_predictions": churn_count,
        "non_churn_predictions": non_churn_count
    }