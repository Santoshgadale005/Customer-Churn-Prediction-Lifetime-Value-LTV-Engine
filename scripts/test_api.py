import requests


def main():
    url = "http://127.0.0.1:8000/api/v1/predict"

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

    response = requests.post(url, json=data, timeout=10)
    response.raise_for_status()
    print(response.json())


if __name__ == "__main__":
    main()
