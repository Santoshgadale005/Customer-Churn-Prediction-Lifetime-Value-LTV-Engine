# Week 2 — Day 8: FastAPI Backend & Prediction API

Today, the ML system became a **real deployable backend service**. We built a production-grade REST API using **FastAPI** that serves churn predictions with SHAP-powered explainability in real-time.

## 🎯 Objectives Completed
- [x] **FastAPI application created** with modular router architecture
- [x] **Pydantic request validation** for all incoming customer data
- [x] **Single prediction endpoint** (`POST /predict/`)
- [x] **SHAP-explained prediction endpoint** (`POST /predict/explain`)
- [x] **Batch prediction endpoint** (`POST /predict/batch`)
- [x] **Feature importance endpoint** (`GET /predict/feature-importance`)
- [x] **Health check endpoint** (`GET /health`)
- [x] **CORS middleware** configured for frontend integration
- [x] **Auto-generated API docs** at `/docs` (Swagger) and `/redoc`

## 🏗️ Architecture

```
app/
├── __init__.py
├── main.py                    ← FastAPI entry point
├── api/
│   ├── __init__.py
│   ├── schemas.py             ← Pydantic request/response models
│   ├── predict.py             ← Prediction + SHAP endpoints
│   └── health.py              ← Health check endpoint
├── services/
│   ├── __init__.py
│   └── preprocessing.py       ← Feature engineering for API input
└── models/
    ├── xgboost_model.pkl      ← Trained model (loaded at startup)
    └── ...
```

## 🔌 API Endpoints

| Method | Endpoint                     | Description                          |
| :----- | :--------------------------- | :----------------------------------- |
| GET    | `/`                          | Welcome message & API overview       |
| GET    | `/health`                    | Health check (model status)          |
| POST   | `/predict/`                  | Single churn prediction              |
| POST   | `/predict/explain`           | Prediction + SHAP explanation        |
| POST   | `/predict/batch`             | Batch predictions                    |
| GET    | `/predict/feature-importance`| Global feature importance            |

## 🧪 Test Results

All endpoints tested successfully:

- **Root** → Returns API overview with available endpoints
- **Health** → `{"status": "healthy", "model_loaded": true}`
- **Predict** → `{"churn_prediction": 1, "churn_probability": 0.5075, "risk_level": "Medium"}`
- **Explain** → Full SHAP breakdown with top churn drivers and retention factors
- **Feature Importance** → All 30 features ranked by XGBoost importance

## 🚀 How to Run

```bash
source .venv/bin/activate
uvicorn app.main:app --reload
# API docs at http://localhost:8000/docs
```

---
**Next Step (Day 9):** Build the interactive dashboard for visualizing predictions and SHAP explanations.
