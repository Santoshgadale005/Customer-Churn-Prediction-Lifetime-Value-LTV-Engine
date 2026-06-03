# Day 22: MLflow & Professional Experiment Tracking

## Overview
Today, the project evolved into a professionally managed MLOps platform by integrating **MLflow**. We established automated tracking for machine learning experiments, which logs all parameters, metrics, and models.

## Accomplishments
- ✅ **MLflow Installation:** Installed `mlflow` for professional experiment tracking.
- ✅ **Tracking Scripts Created:** 
  - `app/models/train_with_mlflow.py`: A script to train and log Logistic Regression, Random Forest, and XGBoost models for Churn Prediction.
  - `app/models/train_ltv_with_mlflow.py`: A script to train and log Linear Regression, Random Forest, and XGBoost models for LTV Prediction.
- ✅ **Hyperparameter Tracking:** Automatically logged hyperparameters like `n_estimators`, `max_depth`, and `learning_rate` for every run.
- ✅ **Metrics Tracking:** Automatically logged critical evaluation metrics:
  - Churn Models: Accuracy, Precision, Recall, F1 Score
  - LTV Models: RMSE, MAE, R2 Score
- ✅ **Model Artifacts & Registry:** Saved model artifacts directly to MLflow and registered them under version-controlled names:
  - `CustomerChurnModel`
  - `CustomerLTVModel`
- ✅ **MLflow UI Server Ready:** The MLflow Dashboard can now be launched locally using `mlflow ui` on `http://127.0.0.1:5000` to visually compare and manage all models.

## Impact
Without MLflow, keeping track of which model performed best with which parameters is nearly impossible at scale. With MLflow, we have full visibility and reproducibility for every training run, moving us closer to an enterprise-grade ML infrastructure.
