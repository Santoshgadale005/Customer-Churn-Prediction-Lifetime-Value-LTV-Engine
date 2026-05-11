import pandas as pd
from app.database.db_connection import get_engine

def load_sample_data():
    engine = get_engine()
    
    data = {
        "gender": ["Male", "Female"],
        "senior_citizen": [0, 1],
        "partner": ["Yes", "No"],
        "dependents": ["No", "No"],
        "tenure": [12, 24],
        "phone_service": ["Yes", "Yes"],
        "internet_service": ["Fiber optic", "DSL"],
        "contract": ["Month-to-month", "Two year"],
        "monthly_charges": [70.5, 89.2],
        "total_charges": [850.0, 2100.0],
        "churn": ["Yes", "No"]
    }
    
    df = pd.DataFrame(data)
    
    try:
        df.to_sql(
            "customers",
            engine,
            if_exists="append",
            index=False
        )
        print("Data inserted successfully")
    except Exception as e:
        print(f"Error inserting data: {e}")

if __name__ == "__main__":
    load_sample_data()
