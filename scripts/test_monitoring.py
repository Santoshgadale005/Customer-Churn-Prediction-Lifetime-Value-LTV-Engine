from app.monitoring import log_prediction

result = log_prediction(
    101,
    "No Churn",
    15000
)

print(result)