"""
Pydantic schemas for request validation and response models.

These schemas define the data contracts for the Churn Prediction API,
ensuring all incoming requests are validated and responses are structured.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


# ─── Request Schemas ───────────────────────────────────────────────

class CustomerData(BaseModel):
    """
    Schema for a single customer's raw features.
    Accepts human-readable values exactly as they appear in the Telco dataset.
    The API handles all preprocessing internally.
    """
    gender: str = Field(..., description="Customer gender: 'Male' or 'Female'")
    SeniorCitizen: int = Field(..., description="Is senior citizen: 1 = Yes, 0 = No")
    Partner: str = Field(..., description="Has partner: 'Yes' or 'No'")
    Dependents: str = Field(..., description="Has dependents: 'Yes' or 'No'")
    tenure: int = Field(..., ge=0, description="Number of months with the company")
    PhoneService: str = Field(..., description="Has phone service: 'Yes' or 'No'")
    MultipleLines: str = Field(..., description="'Yes', 'No', or 'No phone service'")
    InternetService: str = Field(..., description="'DSL', 'Fiber optic', or 'No'")
    OnlineSecurity: str = Field(..., description="'Yes', 'No', or 'No internet service'")
    OnlineBackup: str = Field(..., description="'Yes', 'No', or 'No internet service'")
    DeviceProtection: str = Field(..., description="'Yes', 'No', or 'No internet service'")
    TechSupport: str = Field(..., description="'Yes', 'No', or 'No internet service'")
    StreamingTV: str = Field(..., description="'Yes', 'No', or 'No internet service'")
    StreamingMovies: str = Field(..., description="'Yes', 'No', or 'No internet service'")
    Contract: str = Field(..., description="'Month-to-month', 'One year', or 'Two year'")
    PaperlessBilling: str = Field(..., description="'Yes' or 'No'")
    PaymentMethod: str = Field(
        ...,
        description="'Electronic check', 'Mailed check', 'Bank transfer (automatic)', or 'Credit card (automatic)'"
    )
    MonthlyCharges: float = Field(..., ge=0, description="Monthly charge amount")
    TotalCharges: float = Field(..., ge=0, description="Total charges to date")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "gender": "Female",
                    "SeniorCitizen": 0,
                    "Partner": "Yes",
                    "Dependents": "No",
                    "tenure": 1,
                    "PhoneService": "No",
                    "MultipleLines": "No phone service",
                    "InternetService": "DSL",
                    "OnlineSecurity": "No",
                    "OnlineBackup": "Yes",
                    "DeviceProtection": "No",
                    "TechSupport": "No",
                    "StreamingTV": "No",
                    "StreamingMovies": "No",
                    "Contract": "Month-to-month",
                    "PaperlessBilling": "Yes",
                    "PaymentMethod": "Electronic check",
                    "MonthlyCharges": 29.85,
                    "TotalCharges": 29.85
                }
            ]
        }
    }


class BatchCustomerData(BaseModel):
    """Schema for batch prediction requests."""
    customers: List[CustomerData] = Field(..., description="List of customer records")


class UserCreate(BaseModel):
    """Schema for user registration."""
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    """Schema for username/password login."""
    username: str
    password: str


# ─── Response Schemas ──────────────────────────────────────────────

class PredictionResponse(BaseModel):
    """Response schema for a single churn prediction."""
    customer_index: Optional[int] = Field(None, description="Index of customer in batch")
    churn_prediction: int = Field(..., description="0 = No Churn, 1 = Churn")
    churn_probability: float = Field(..., description="Probability of churn (0.0 to 1.0)")
    risk_level: str = Field(..., description="'Low', 'Medium', or 'High'")
    message: str = Field(..., description="Human-readable prediction summary")


class ExplainedPredictionResponse(BaseModel):
    """Response schema for a prediction with SHAP explanations."""
    churn_prediction: int = Field(..., description="0 = No Churn, 1 = Churn")
    churn_probability: float = Field(..., description="Probability of churn (0.0 to 1.0)")
    risk_level: str = Field(..., description="'Low', 'Medium', or 'High'")
    message: str = Field(..., description="Human-readable prediction summary")
    base_value: float = Field(..., description="SHAP base value (average model output)")
    shap_explanations: List[Dict[str, float]] = Field(
        ...,
        description="List of feature contributions sorted by impact"
    )
    top_churn_drivers: List[str] = Field(
        ...,
        description="Top features pushing toward churn"
    )
    top_retention_factors: List[str] = Field(
        ...,
        description="Top features pushing away from churn"
    )


class BatchPredictionResponse(BaseModel):
    """Response schema for batch predictions."""
    total_customers: int
    churn_count: int
    no_churn_count: int
    churn_rate: float
    predictions: List[PredictionResponse]


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""
    status: str
    model_loaded: bool
    api_version: str
    model_type: str


class FeatureScore(BaseModel):
    """A single feature and its importance score."""
    feature: str
    importance: float


class FeatureImportanceResponse(BaseModel):
    """Response schema for global feature importance."""
    features: List[FeatureScore]
    model_type: str


class TokenResponse(BaseModel):
    """Response schema returned after successful login."""
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    """Public user fields returned by auth endpoints."""
    id: int
    username: str
    email: str
    role: str

    model_config = {"from_attributes": True}
