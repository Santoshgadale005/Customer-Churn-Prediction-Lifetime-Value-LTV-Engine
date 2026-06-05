from app.monitoring import get_metrics, log_prediction

log_prediction(0)
log_prediction(1)
result = get_metrics()

print(result)
