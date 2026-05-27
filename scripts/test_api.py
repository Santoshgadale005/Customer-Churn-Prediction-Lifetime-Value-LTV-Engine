import requests

url = "http://127.0.0.1:8000/predict"

data = {
    "gender": "Female",
    "SeniorCitizen": 0,
    "Partner": "Yes",
    "Dependents": "No",
    "tenure": 24,
    "PhoneService": "Yes",
    "MonthlyCharges": 75.5,
    "TotalCharges": 1800
}

response = requests.post(url, json=data)

print(response.json())