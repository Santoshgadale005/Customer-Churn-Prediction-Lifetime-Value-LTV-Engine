"""
Preprocessing service for the Churn Prediction API.

Transforms raw customer data (human-readable values) into the exact
feature format expected by the trained XGBoost model. This replicates
the same one-hot encoding logic used during training (pd.get_dummies
with drop_first=True).
"""

import pandas as pd
import numpy as np


# The exact column order the model was trained on.
# This MUST match the output of the preprocessing pipeline used during training.
MODEL_FEATURE_COLUMNS = [
    "SeniorCitizen",
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
    "gender_Male",
    "Partner_Yes",
    "Dependents_Yes",
    "PhoneService_Yes",
    "MultipleLines_No phone service",
    "MultipleLines_Yes",
    "InternetService_Fiber optic",
    "InternetService_No",
    "OnlineSecurity_No internet service",
    "OnlineSecurity_Yes",
    "OnlineBackup_No internet service",
    "OnlineBackup_Yes",
    "DeviceProtection_No internet service",
    "DeviceProtection_Yes",
    "TechSupport_No internet service",
    "TechSupport_Yes",
    "StreamingTV_No internet service",
    "StreamingTV_Yes",
    "StreamingMovies_No internet service",
    "StreamingMovies_Yes",
    "Contract_One year",
    "Contract_Two year",
    "PaperlessBilling_Yes",
    "PaymentMethod_Credit card (automatic)",
    "PaymentMethod_Electronic check",
    "PaymentMethod_Mailed check",
]


def preprocess_customer(customer_data: dict) -> pd.DataFrame:
    """
    Transform a single customer's raw data into model-ready features.

    Args:
        customer_data: Dictionary of raw customer attributes.

    Returns:
        A single-row DataFrame with columns matching MODEL_FEATURE_COLUMNS.
    """
    # Create a DataFrame from the raw input
    df = pd.DataFrame([customer_data])

    # Apply one-hot encoding (same as training: drop_first=True)
    df_encoded = pd.get_dummies(df, drop_first=True)

    # Ensure all expected columns exist (fill missing ones with 0)
    for col in MODEL_FEATURE_COLUMNS:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    # Select only the columns the model expects, in the correct order
    df_final = df_encoded[MODEL_FEATURE_COLUMNS]

    return df_final


def preprocess_batch(customers: list[dict]) -> pd.DataFrame:
    """
    Transform a batch of customer records into model-ready features.

    Args:
        customers: List of dictionaries, each containing raw customer attributes.

    Returns:
        A DataFrame with rows for each customer and columns matching MODEL_FEATURE_COLUMNS.
    """
    df = pd.DataFrame(customers)
    df_encoded = pd.get_dummies(df, drop_first=True)

    for col in MODEL_FEATURE_COLUMNS:
        if col not in df_encoded.columns:
            df_encoded[col] = 0

    df_final = df_encoded[MODEL_FEATURE_COLUMNS]

    return df_final


def get_risk_level(probability: float) -> str:
    """Classify churn probability into a human-readable risk level."""
    if probability >= 0.7:
        return "High"
    elif probability >= 0.4:
        return "Medium"
    else:
        return "Low"
