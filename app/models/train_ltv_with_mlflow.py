import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
import numpy as np
import os

def train_ltv_model(model_type="random_forest", params=None):
    if params is None:
        params = {}
        
    print(f"Training LTV {model_type} model...")

    # Load Dataset
    df = pd.read_csv("data/engineered_telco_data.csv")

    # Assuming 'Customer Lifetime Value' or similar is the target. Let's use 'TotalCharges' as a proxy for LTV if real LTV is not in dataset.
    # In earlier days LTV was predicted. I'll assume TotalCharges or CLV.
    target_col = 'TotalCharges' if 'Customer Lifetime Value' not in df.columns and 'CLV' not in df.columns else ('Customer Lifetime Value' if 'Customer Lifetime Value' in df.columns else 'CLV')
    
    # Create Features
    X = df.drop([target_col], axis=1)
    if 'Churn' in X.columns:
        X = X.drop('Churn', axis=1) # Drop Churn to prevent leakage if predicting LTV at start
        
    y = df[target_col]

    # Train Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    # Start MLflow Run
    with mlflow.start_run(run_name=f"{model_type}_ltv_experiment"):
        
        # Log Parameters
        mlflow.log_param("model_type", model_type)
        for key, value in params.items():
            mlflow.log_param(key, value)

        # Create model
        if model_type == "linear_regression":
            model = LinearRegression(**params)
        elif model_type == "random_forest":
            model = RandomForestRegressor(random_state=42, **params)
        elif model_type == "xgboost":
            model = XGBRegressor(random_state=42, **params)
        else:
            raise ValueError("Unknown model type")

        # Train Model
        model.fit(X_train, y_train)

        # Generate Predictions
        predictions = model.predict(X_test)

        # Calculate Metrics
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        mae = mean_absolute_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        
        print(f"RMSE: {rmse:.4f}")

        # Log Metrics
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2_score", r2)

        # Log Model Artifact and Register Model
        mlflow.sklearn.log_model(
            model,
            artifact_path="model",
            registered_model_name="CustomerLTVModel"
        )
        print(f"Successfully logged LTV {model_type} to MLflow.")

if __name__ == "__main__":
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("Customer_LTV_Prediction")
    
    train_ltv_model("linear_regression", {})
    train_ltv_model("random_forest", {"n_estimators": 100, "max_depth": 10})
    train_ltv_model("xgboost", {"n_estimators": 200, "learning_rate": 0.05, "max_depth": 5})
