from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class CustomerData(BaseModel):
    tenure: int
    MonthlyCharges: float

@app.get("/")
def home():
    return {"message": "FastAPI Running"}

@app.post("/predict")
def predict(data: CustomerData):

    tenure = data.tenure
    charges = data.MonthlyCharges

    if charges > 70:
        prediction = "Likely to Churn"
    else:
        prediction = "Not Likely to Churn"

    return {
        "prediction": prediction,
        "tenure": tenure,
        "monthly_charges": charges
    }