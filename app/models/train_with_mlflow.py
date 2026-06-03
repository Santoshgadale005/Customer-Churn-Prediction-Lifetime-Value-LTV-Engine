import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
import os

def train_churn_model(model_type="random_forest", params=None):
    if params is None:
        params = {}
        
    print(f"Training {model_type} model...")

    # Load Dataset
    df = pd.read_csv("data/engineered_telco_data.csv")

    # Create Features
    X = df.drop(["Churn"], axis=1) # Need to ensure only Churn is dropped, maybe LTV related columns too if present
    # Keep only the columns used for churn prediction during Day 17
    target_col = 'Churn'
    
    # We might need to handle specific preprocessing depending on the exact schema, assuming engineered_telco_data.csv is ready.
    if target_col not in df.columns:
        print("Error: Target column not found.")
        return
        
    # Drop LTV if it's in the dataset so it doesn't leak
    if 'Customer Lifetime Value' in X.columns:
        X = X.drop('Customer Lifetime Value', axis=1)
    if 'CLV' in X.columns:
        X = X.drop('CLV', axis=1)
        
    y = df[target_col]

    # Train Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    # Start MLflow Run
    with mlflow.start_run(run_name=f"{model_type}_churn_experiment"):
        
        # Log Parameters
        mlflow.log_param("model_type", model_type)
        for key, value in params.items():
            mlflow.log_param(key, value)

        # Create model
        if model_type == "logistic_regression":
            model = LogisticRegression(max_iter=1000, random_state=42, **params)
        elif model_type == "random_forest":
            model = RandomForestClassifier(random_state=42, **params)
        elif model_type == "xgboost":
            model = XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss', **params)
        else:
            raise ValueError("Unknown model type")

        # Train Model
        model.fit(X_train, y_train)

        # Generate Predictions
        predictions = model.predict(X_test)

        # Calculate Metrics
        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions)
        recall = recall_score(y_test, predictions)
        f1 = f1_score(y_test, predictions)
        
        print(f"Accuracy: {accuracy:.4f}")

        # Log Metrics
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("f1_score", f1)

        # Log Model Artifact and Register Model
        mlflow.sklearn.log_model(
            model,
            artifact_path="model",
            registered_model_name="CustomerChurnModel"
        )
        print(f"Successfully logged {model_type} to MLflow.")

if __name__ == "__main__":
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("Customer_Churn_Prediction")
    
    train_churn_model("logistic_regression", {"C": 1.0})
    train_churn_model("random_forest", {"n_estimators": 100, "max_depth": 10})
    train_churn_model("xgboost", {"n_estimators": 300, "learning_rate": 0.05, "max_depth": 6})
