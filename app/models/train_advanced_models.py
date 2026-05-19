import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

def train_advanced_models():
    # Step 8: Load Dataset
    data_path = "data/preprocessed_telco_data.csv"
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return

    df = pd.read_csv(data_path)
    print(f"Dataset loaded: {df.shape}")

    # Step 9: Separate Features and Target
    X = df.drop("Churn", axis=1)
    y = df["Churn"]

    # Step 10: Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )
    print("Data split into train and test sets.")

    # Step 11: Train Random Forest
    print("\n--- Training Random Forest ---")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )
    rf_model.fit(X_train, y_train)

    # Step 12: Make Random Forest Predictions
    rf_predictions = rf_model.predict(X_test)

    # Step 13: Evaluate Random Forest
    rf_accuracy = accuracy_score(y_test, rf_predictions)
    print(f"Random Forest Accuracy: {rf_accuracy:.4f}")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, rf_predictions))
    print("\nClassification Report:")
    print(classification_report(y_test, rf_predictions))

    # Step 14: Train XGBoost Model
    print("\n--- Training XGBoost ---")
    xgb_model = XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    xgb_model.fit(X_train, y_train)

    # Step 15: Make XGBoost Predictions
    xgb_predictions = xgb_model.predict(X_test)

    # Step 16: Evaluate XGBoost
    xgb_accuracy = accuracy_score(y_test, xgb_predictions)
    print(f"XGBoost Accuracy: {xgb_accuracy:.4f}")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, xgb_predictions))
    print("\nClassification Report:")
    print(classification_report(y_test, xgb_predictions))

    # Step 17: Compare Models
    print("\n--- Model Comparison ---")
    print(f"Random Forest Accuracy: {rf_accuracy:.4f}")
    print(f"XGBoost Accuracy:       {xgb_accuracy:.4f}")

    # Step 18: Feature Importance (Random Forest)
    print("\n--- Feature Importance (Random Forest) ---")
    feature_importance = pd.DataFrame({
        "Feature": X.columns,
        "Importance": rf_model.feature_importances_
    })
    feature_importance = feature_importance.sort_values(
        by="Importance",
        ascending=False
    )
    print(feature_importance.head(10))

    # Step 20: Save Models
    models_dir = "app/models"
    os.makedirs(models_dir, exist_ok=True)
    
    rf_path = os.path.join(models_dir, "random_forest_model.pkl")
    xgb_path = os.path.join(models_dir, "xgboost_model.pkl")
    
    joblib.dump(rf_model, rf_path)
    joblib.dump(xgb_model, xgb_path)
    
    print(f"\nModels saved successfully:")
    print(f"- {rf_path}")
    print(f"- {xgb_path}")

if __name__ == "__main__":
    train_advanced_models()
