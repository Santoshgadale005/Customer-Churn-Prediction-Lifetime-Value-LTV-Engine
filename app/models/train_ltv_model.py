import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

def main():
    # Load dataset
    print("Loading dataset...")
    df = pd.read_csv("data/preprocessed_telco_data.csv")
    
    # Engineer LTV target
    print("Engineering LTV target...")
    df["LTV"] = df["MonthlyCharges"] * df["tenure"]
    
    # Separate features and target, prevent target leakage by dropping 'Churn'
    X = df.drop(["LTV", "Churn"], axis=1)
    y = df["LTV"]
    
    # Train-Test Split
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train Model
    print("Training Random Forest Regressor...")
    ltv_model = RandomForestRegressor(n_estimators=100, random_state=42)
    ltv_model.fit(X_train, y_train)
    
    # Make Predictions
    print("Evaluating model...")
    ltv_predictions = ltv_model.predict(X_test)
    
    # Regression Metrics
    mae = mean_absolute_error(y_test, ltv_predictions)
    mse = mean_squared_error(y_test, ltv_predictions)
    rmse = mse ** 0.5
    r2 = r2_score(y_test, ltv_predictions)
    
    print("\nModel Performance Metrics:")
    print(f"MAE: {mae:.2f}")
    print(f"MSE: {mse:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R2 Score: {r2:.4f}\n")
    
    # Save Model
    print("Saving LTV model...")
    joblib.dump(ltv_model, "app/models/ltv_prediction_model.pkl")
    
    # Business Segmentation Logic
    print("Generating business segmentation...")
    results_df = X_test.copy()
    results_df["Predicted_LTV"] = ltv_predictions
    
    def segment_customer(ltv):
        if ltv > 5000:
            return "High Value"
        elif ltv > 2000:
            return "Medium Value"
        else:
            return "Low Value"
            
    results_df["Segment"] = results_df["Predicted_LTV"].apply(segment_customer)
    
    # Save Results
    results_df.to_csv("data/ltv_predictions.csv", index=False)
    print("Business predictions saved to data/ltv_predictions.csv")
    print("Day 15 tasks completed successfully!")

if __name__ == "__main__":
    main()
