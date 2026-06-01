import logging
import os

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename='logs/app.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

def log_prediction(message):
    logging.info(message)
