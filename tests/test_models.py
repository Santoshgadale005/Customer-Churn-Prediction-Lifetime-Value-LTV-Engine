import joblib
import os

def test_churn_model_loading():
    model_path = os.path.join("app", "models", "xgboost_model.pkl")
    assert os.path.exists(model_path), f"Model file not found at {model_path}"
    model = joblib.load(model_path)
    assert model is not None

def test_ltv_model_loading():
    model_path = os.path.join("app", "models", "ltv_prediction_model.pkl")
    assert os.path.exists(model_path), f"Model file not found at {model_path}"
    model = joblib.load(model_path)
    assert model is not None
