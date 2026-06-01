# Day 17: Advanced Feature Engineering & Behavioral Analytics

## Overview
Today, we boosted our models' predictive power by designing advanced behavioral and interaction features, retraining the models, and updating our preprocessing services.

## Accomplishments
- ✅ **Behavioral Feature Engineering:** Created new features in `app/services/feature_engineering.py`:
  - `Interaction_Score`: Interaction metric of tenure and charges.
  - `Charges_Ratio`: Proportion of monthly charges to total charges.
- ✅ **Model Retraining:** Re-trained models with the new feature space (updating `xgboost_model.pkl` and `ltv_prediction_model.pkl`).
- ✅ **Engineered Dataset:** Exported the newly processed dataset to `data/engineered_telco_data.csv`.
