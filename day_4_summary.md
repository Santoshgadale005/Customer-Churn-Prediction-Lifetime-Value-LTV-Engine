# Day 4: Data Preprocessing & Feature Engineering

## Overview
Today we transformed the raw cleaned data into a format ready for machine learning. This is a critical step in the pipeline where we handle categorical data, normalize scales, and address dataset imbalances.

## Accomplishments
- ✅ **Created `app/services/preprocessing.py`**: A robust pipeline for data transformation.
- ✅ **Categorical Encoding**:
    - Applied **Label Encoding** to binary features (Gender, Partner, etc.).
    - Applied **One-Hot Encoding** to multiclass features (Contract, Payment Method, etc.).
- ✅ **Numerical Scaling**:
    - Used **StandardScaler** to normalize `tenure`, `MonthlyCharges`, and `TotalCharges`.
- ✅ **Train/Test Split**:
    - Split the data into 80% training and 20% testing sets using stratified sampling to maintain churn proportions.
- ✅ **Handling Imbalance**:
    - Implemented **SMOTE (Synthetic Minority Over-sampling Technique)** to balance the Churn classes (from ~26% to 50/50).
- ✅ **Artifact Persistence**:
    - Saved scalers and encoders to `models/artifacts/` for consistent inference.
    - Saved processed datasets to `data/processed/`.

## Current Status
We now have two balanced, scaled, and encoded datasets:
- `data/processed/train_processed.csv`
- `data/processed/test_processed.csv`

## Next Steps
Tomorrow, we move to **Phase 2: Machine Learning & Modeling (Day 1)**, where we will train our **Baseline Churn Model (Logistic Regression)** and evaluate its performance.

---
*Internship Progress: Week 1, Day 4 Complete.*
