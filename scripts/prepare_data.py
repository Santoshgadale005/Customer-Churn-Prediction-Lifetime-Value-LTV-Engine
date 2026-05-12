import pandas as pd
import numpy as np
import os

def prepare_data():
    raw_data_path = "data/WA_Fn-UseC_-Telco-Customer-Churn.csv"
    cleaned_data_path = "data/cleaned_telco_data.csv"

    if not os.path.exists(raw_data_path):
        print(f"Error: Raw data not found at {raw_data_path}")
        return

    print("Loading dataset...")
    df = pd.read_csv(raw_data_path)

    print(f"Initial shape: {df.shape}")

    # Step 14: Detect hidden missing values in TotalCharges
    print("Cleaning TotalCharges...")
    df["TotalCharges"] = df["TotalCharges"].replace(" ", np.nan)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"])

    # Step 16: Handle missing values (Drop them)
    print(f"Missing values before dropping:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    df.dropna(inplace=True)
    print(f"Shape after dropping missing values: {df.shape}")

    # Step 21: Convert target for correlation (optional but good for consistency)
    # df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0}) # Keeping original for now as per notebook's final step save

    print(f"Saving cleaned dataset to {cleaned_data_path}...")
    df.to_csv(cleaned_data_path, index=False)
    print("Data preparation complete!")

if __name__ == "__main__":
    prepare_data()
