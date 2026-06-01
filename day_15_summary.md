# Day 15: LTV Prediction Engine & Customer Segmentation

## Overview
Today, we expanded our modeling capabilities by building the Customer Lifetime Value (LTV) Prediction Engine. Additionally, we categorized customers into risk segments to power targeted retention campaigns.

## Accomplishments
- ✅ **LTV Model Training:** Trained a regression model for LTV in `app/models/train_ltv_model.py`.
- ✅ **Model Persistence:** Saved the trained model file `app/models/ltv_prediction_model.pkl`.
- ✅ **Customer Segmentation Rules:** Established intelligence rules combining churn risk and LTV:
  - **High Value - High Risk**
  - **Low Value - High Risk**
  - **High Value - Low Risk**
  - **Standard Customer**
- ✅ **Dataset Output:** Exported segmented results to `data/ltv_predictions.csv` for downstream BI dashboard analysis.
