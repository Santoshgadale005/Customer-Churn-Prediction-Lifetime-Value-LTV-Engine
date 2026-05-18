"""
Customer Churn Prediction API — Main Application

Enterprise-grade FastAPI backend that serves real-time churn predictions
with SHAP-powered explainability.

Endpoints:
  GET  /                         → Welcome message
  GET  /health                   → API health check
  POST /predict/                 → Single churn prediction
  POST /predict/explain          → Prediction + SHAP explanation
  POST /predict/batch            → Batch churn predictions
  GET  /predict/feature-importance → Global feature importance

Run with:
  uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.predict import router as predict_router
from app.api.health import router as health_router

# ─── Application Setup ─────────────────────────────────────────────

app = FastAPI(
    title="Customer Churn Prediction API",
    description=(
        "Enterprise-level Machine Learning API for predicting customer churn "
        "with SHAP-based model explainability. Built with FastAPI and XGBoost."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS Middleware ───────────────────────────────────────────────
# Allow all origins for development; restrict in production.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register Routers ─────────────────────────────────────────────

app.include_router(health_router)
app.include_router(predict_router)


# ─── Root Endpoint ─────────────────────────────────────────────────

@app.get("/", tags=["Root"])
def root():
    """Welcome endpoint with API overview."""
    return {
        "message": "🚀 Customer Churn Prediction API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "predict": "POST /predict/",
            "explain": "POST /predict/explain",
            "batch": "POST /predict/batch",
            "feature_importance": "GET /predict/feature-importance",
        },
    }
