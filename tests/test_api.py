from fastapi.testclient import TestClient
from types import SimpleNamespace
from unittest.mock import MagicMock
from app.main import app
from app.database.db_dependency import get_db
from app.services.auth_service import get_current_user, require_admin

# Override the database dependency to avoid requiring a live DB in tests
mock_db = MagicMock()
app.dependency_overrides[get_db] = lambda: mock_db
mock_user = SimpleNamespace(
    id=1,
    username="test_admin",
    email="admin@example.com",
    role="admin"
)
app.dependency_overrides[get_current_user] = lambda: mock_user
app.dependency_overrides[require_admin] = lambda: mock_user

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API Working Successfully"}

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_model_info():
    response = client.get("/api/v1/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "xgboost_churn_model"
    assert data["version"] == "v1"
    assert "accuracy" in data

def test_prediction():
    payload = {
        "gender_Male": 1,
        "SeniorCitizen": 0,
        "tenure": 5,
        "MonthlyCharges": 90,
        "TotalCharges": 400
    }
    response = client.post(
        "/api/v1/predict",
        json=payload
    )
    assert response.status_code == 200
    data = response.json()
    assert "churn_prediction" in data
    assert "churn_probability" in data
    assert "predicted_ltv" in data
    assert "customer_segment" in data
    assert "recommendation" in data
