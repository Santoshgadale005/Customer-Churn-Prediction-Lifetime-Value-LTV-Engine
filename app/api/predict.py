"""
Prediction API routes.

Provides endpoints for:
  - Single churn prediction
  - Single prediction with SHAP explanation
  - Batch churn predictions
  - Global feature importance
"""

from fastapi import APIRouter, HTTPException
import joblib
import shap
import numpy as np
import os

from app.api.schemas import (
    CustomerData,
    BatchCustomerData,
    PredictionResponse,
    ExplainedPredictionResponse,
    BatchPredictionResponse,
    FeatureImportanceResponse,
    FeatureScore,
)
from app.services.preprocessing import (
    preprocess_customer,
    preprocess_batch,
    get_risk_level,
    MODEL_FEATURE_COLUMNS,
)

router = APIRouter(prefix="/predict", tags=["Predictions"])

# ─── Load Model & Explainer at Startup ─────────────────────────────
MODEL_PATH = os.path.join("app", "models", "xgboost_model.pkl")

try:
    model = joblib.load(MODEL_PATH)
    explainer = shap.TreeExplainer(model)
    MODEL_LOADED = True
    print(f"✅ XGBoost model loaded from {MODEL_PATH}")
except Exception as e:
    model = None
    explainer = None
    MODEL_LOADED = False
    print(f"❌ Failed to load model: {e}")


def _check_model():
    """Raise 503 if the model is not loaded."""
    if not MODEL_LOADED or model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded. Please check server logs."
        )


# ─── Endpoint: Single Prediction ──────────────────────────────────

@router.post(
    "/",
    response_model=PredictionResponse,
    summary="Predict churn for a single customer",
)
def predict_churn(customer: CustomerData):
    """
    Accepts a single customer's raw data and returns a churn prediction
    with probability and risk level.
    """
    _check_model()

    # Preprocess
    features = preprocess_customer(customer.model_dump())

    # Predict
    prediction = int(model.predict(features)[0])
    probability = float(model.predict_proba(features)[0][1])
    risk = get_risk_level(probability)

    message = (
        f"Customer is {'likely' if prediction == 1 else 'unlikely'} to churn. "
        f"Risk Level: {risk} ({probability:.1%} probability)."
    )

    return PredictionResponse(
        churn_prediction=prediction,
        churn_probability=round(probability, 4),
        risk_level=risk,
        message=message,
    )


# ─── Endpoint: Prediction with SHAP Explanation ───────────────────

@router.post(
    "/explain",
    response_model=ExplainedPredictionResponse,
    summary="Predict churn with SHAP explanation",
)
def predict_and_explain(customer: CustomerData):
    """
    Returns a churn prediction along with a full SHAP explanation
    showing which features pushed the prediction higher or lower.
    """
    _check_model()

    features = preprocess_customer(customer.model_dump())

    # Predict
    prediction = int(model.predict(features)[0])
    probability = float(model.predict_proba(features)[0][1])
    risk = get_risk_level(probability)

    # SHAP explanation
    shap_values = explainer.shap_values(features)
    base_value = float(explainer.expected_value)

    # Build sorted feature-contribution list
    shap_row = shap_values[0]  # single row
    explanations = []
    churn_drivers = []
    retention_factors = []

    # Pair features with their SHAP values and sort by absolute impact
    feature_impacts = sorted(
        zip(MODEL_FEATURE_COLUMNS, shap_row),
        key=lambda x: abs(x[1]),
        reverse=True,
    )

    for feature_name, shap_val in feature_impacts:
        explanations.append({feature_name: round(float(shap_val), 4)})
        if shap_val > 0:
            churn_drivers.append(f"{feature_name} (+{shap_val:.4f})")
        else:
            retention_factors.append(f"{feature_name} ({shap_val:.4f})")

    message = (
        f"Customer is {'likely' if prediction == 1 else 'unlikely'} to churn. "
        f"Risk Level: {risk} ({probability:.1%} probability)."
    )

    return ExplainedPredictionResponse(
        churn_prediction=prediction,
        churn_probability=round(probability, 4),
        risk_level=risk,
        message=message,
        base_value=round(base_value, 4),
        shap_explanations=explanations,
        top_churn_drivers=churn_drivers[:5],
        top_retention_factors=retention_factors[:5],
    )


# ─── Endpoint: Batch Prediction ───────────────────────────────────

@router.post(
    "/batch",
    response_model=BatchPredictionResponse,
    summary="Predict churn for multiple customers",
)
def predict_batch(data: BatchCustomerData):
    """
    Accepts a batch of customer records and returns predictions for all.
    """
    _check_model()

    customers_dicts = [c.model_dump() for c in data.customers]
    features = preprocess_batch(customers_dicts)

    predictions = model.predict(features)
    probabilities = model.predict_proba(features)[:, 1]

    results = []
    for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
        risk = get_risk_level(float(prob))
        results.append(
            PredictionResponse(
                customer_index=i,
                churn_prediction=int(pred),
                churn_probability=round(float(prob), 4),
                risk_level=risk,
                message=f"Customer {i}: {'Churn' if pred == 1 else 'No Churn'} "
                        f"(Risk: {risk}, {float(prob):.1%})",
            )
        )

    churn_count = int(sum(predictions))
    total = len(predictions)

    return BatchPredictionResponse(
        total_customers=total,
        churn_count=churn_count,
        no_churn_count=total - churn_count,
        churn_rate=round(churn_count / total, 4) if total > 0 else 0.0,
        predictions=results,
    )


# ─── Endpoint: Global Feature Importance ──────────────────────────

@router.get(
    "/feature-importance",
    response_model=FeatureImportanceResponse,
    summary="Get global feature importance from the model",
)
def get_feature_importance():
    """
    Returns the built-in feature importance scores from the XGBoost model,
    sorted by importance.
    """
    _check_model()

    importances = model.feature_importances_
    feature_list = sorted(
        [
            FeatureScore(feature=name, importance=round(float(imp), 4))
            for name, imp in zip(MODEL_FEATURE_COLUMNS, importances)
        ],
        key=lambda x: x.importance,
        reverse=True,
    )

    return FeatureImportanceResponse(
        features=feature_list,
        model_type="XGBoost",
    )
