import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report
)
import joblib
import os

def train_logistic_regression():
    # Step 4: Load Dataset
    print("Step 4: Loading preprocessed dataset...")
    df = pd.read_csv("data/preprocessed_telco_data.csv")

    # Step 5: Separate Features and Target
    print("Step 5: Separating features and target...")
    X = df.drop("Churn", axis=1)
    y = df["Churn"]

    # Step 6: Train-Test Split
    print("Step 6: Performing Train-Test Split...")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    # Step 7: Create Logistic Regression Model
    print("Step 7: Creating Logistic Regression model...")
    model = LogisticRegression(max_iter=1000)

    # Step 8: Train Model
    print("Step 8: Training model...")
    model.fit(X_train, y_train)

    # Step 9: Make Predictions
    print("Step 9: Making predictions...")
    y_pred = model.predict(X_test)

    # Step 10: Evaluate Accuracy
    print("Step 10: Evaluating accuracy...")
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)

    # Step 11: Confusion Matrix
    print("Step 11: Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)

    # Step 12: Classification Report
    print("Step 12: Classification Report:")
    print(classification_report(y_test, y_pred))

    # Step 13: Predict Probabilities
    print("Step 13: Sample probabilities (first 5):")
    probabilities = model.predict_proba(X_test)
    print(probabilities[:5])

    # Step 14: Save Model
    print("Step 14: Saving model...")
    # Ensure directory exists
    os.makedirs("app/models", exist_ok=True)
    joblib.dump(
        model,
        "app/models/logistic_regression_model.pkl"
    )
    print("Model saved to app/models/logistic_regression_model.pkl")

if __name__ == "__main__":
    train_logistic_regression()
