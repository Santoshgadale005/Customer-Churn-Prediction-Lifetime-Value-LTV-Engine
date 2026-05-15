import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import os

def run_day4_preprocessing():
    # Step 2: Load cleaned dataset
    print("Step 2: Loading cleaned dataset...")
    df = pd.read_csv("data/cleaned_telco_data.csv")
    
    # Drop customerID if exists
    if 'customerID' in df.columns:
        df = df.drop('customerID', axis=1)

    # Step 5: Encode Target Variable
    print("Step 5: Encoding target variable...")
    df["Churn"] = df["Churn"].map({
        "Yes": 1,
        "No": 0
    })

    # Step 8: Apply One-Hot Encoding
    print("Step 8: Applying One-Hot Encoding...")
    df = pd.get_dummies(df, drop_first=True)

    # Save Full ML-Ready Dataset (Step 16)
    print("Step 16: Saving full ML-ready dataset...")
    df.to_csv("data/preprocessed_telco_data.csv", index=False)

    # Step 11: Separate Features and Target
    X = df.drop("Churn", axis=1)
    y = df["Churn"]

    # Step 12: Train-Test Split
    print("Step 12: Performing Train-Test Split...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, 
        y, 
        test_size=0.2, 
        random_state=42
    )

    # Step 13: Apply Standard Scaling
    print("Step 13: Applying Standard Scaling...")
    scaler = StandardScaler()
    
    # Fit and transform training data
    X_train_scaled = scaler.fit_transform(X_train)
    # Transform test data
    X_test_scaled = scaler.transform(X_test)

    # Convert back to DataFrame to keep column names (optional but good practice)
    X_train_df = pd.DataFrame(X_train_scaled, columns=X_train.columns)
    X_test_df = pd.DataFrame(X_test_scaled, columns=X_test.columns)

    # Step 15: Save Processed Data
    print("Step 15: Saving split datasets...")
    X_train_df.to_csv("data/X_train.csv", index=False)
    X_test_df.to_csv("data/X_test.csv", index=False)
    y_train.to_csv("data/y_train.csv", index=False)
    y_test.to_csv("data/y_test.csv", index=False)

    print("Day 4 Preprocessing Complete!")

if __name__ == "__main__":
    run_day4_preprocessing()
