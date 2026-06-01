import pandas as pd

def engineer_features(df):
    # Ensure tenure is float/int.
    # We add 1 to avoid division by zero.
    df["RevenuePerMonth"] = df["TotalCharges"] / (df["tenure"] + 1)
    df["EngagementScore"] = df["tenure"] * df["MonthlyCharges"]
    df["RiskScore"] = df["MonthlyCharges"] / (df["tenure"] + 1)
    df["TenureChargeInteraction"] = df["tenure"] * df["MonthlyCharges"]
    df["CustomerStability"] = df["tenure"] / (df["MonthlyCharges"] + 1)
    df["ServiceDensity"] = df["MonthlyCharges"] / (df["tenure"] + 1)
    return df

if __name__ == "__main__":
    print("Loading preprocessed dataset...")
    df = pd.read_csv("data/preprocessed_telco_data.csv")
    
    print("Engineering advanced features...")
    df = engineer_features(df)
    
    print("Saving engineered dataset...")
    df.to_csv("data/engineered_telco_data.csv", index=False)
    
    print("Feature engineering completed successfully. Created data/engineered_telco_data.csv")
