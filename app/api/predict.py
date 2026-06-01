"""
Prediction API routes.

Provides endpoints for:
  - Single churn prediction
  - Single prediction with SHAP explanation
  - Batch churn predictions
  - Global feature importance
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import joblib
import shap
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
from app.database.db_dependency import get_db
from app.services.prediction_service import predict_customer_intelligence
from app.logger import log_prediction

router = APIRouter(prefix="/api/v1", tags=["Predictions"])

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


MODEL_INFO = {
    "model_name": "xgboost_churn_model",
    "version": "v1",
    "accuracy": 0.791,
}


def _check_model():
    """Raise 503 if the model is not loaded."""
    if not MODEL_LOADED or model is None:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded. Please check server logs."
        )


# ─── Endpoint: Single Prediction ──────────────────────────────────

@router.post(
    "/predict",
    summary="Predict churn and LTV for a single customer",
)
def predict(data: dict, db: Session = Depends(get_db)):
    """
    Accepts a single customer's raw data and returns a combined churn prediction,
    LTV prediction, and business recommendation.
    """
    _check_model()

    try:
        return predict_customer_intelligence(data, db)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid prediction input: {exc}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Prediction failed",
        ) from exc


# ─── Endpoint: Prediction with SHAP Explanation ───────────────────

@router.post(
    "/predict/explain",
    response_model=ExplainedPredictionResponse,
    summary="Predict churn with SHAP explanation",
)
def predict_and_explain(customer: CustomerData):
    """
    Returns a churn prediction along with a full SHAP explanation
    showing which features pushed the prediction higher or lower.
    """
    _check_model()

    try:
        features = preprocess_customer(customer.model_dump())

        prediction = int(model.predict(features)[0])
        probability = float(model.predict_proba(features)[0][1])
        risk = get_risk_level(probability)

        shap_values = explainer.shap_values(features)
        base_value = float(explainer.expected_value)

        shap_row = shap_values[0]
        explanations = []
        churn_drivers = []
        retention_factors = []

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
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid explanation input: {exc}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="SHAP explanation failed",
        ) from exc


# ─── Endpoint: Batch Prediction ───────────────────────────────────

@router.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    summary="Predict churn for multiple customers",
)
def predict_batch(data: BatchCustomerData):
    """
    Accepts a batch of customer records and returns predictions for all.
    """
    _check_model()

    try:
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
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid batch prediction input: {exc}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Batch prediction failed",
        ) from exc


# ─── Endpoint: Global Feature Importance ──────────────────────────

@router.get(
    "/predict/feature-importance",
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
    log_prediction("Prediction completed successfully")
    return FeatureImportanceResponse(
        features=feature_list,
        model_type="XGBoost",
    )


@router.get(
    "/model-info",
    summary="Get deployed model metadata",
)
def get_model_info():
    _check_model()
    return MODEL_INFO
