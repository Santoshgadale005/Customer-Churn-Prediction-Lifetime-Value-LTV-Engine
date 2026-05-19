# Day 6 Summary — Advanced ML Models

## Progress Overview
Today marked a significant transition from a simple baseline model to production-grade predictive modeling. We implemented **Random Forest** and **XGBoost**, two powerful ensemble methods that are industry standards for tabular data.

## Key Concepts Covered
- **Decision Trees:** Hierarchical branching logic for decision making.
- **Ensemble Learning:** Combining multiple "weak" models to create a "strong" model.
- **Bagging (Random Forest):** Training multiple trees independently on random subsets of data and averaging their predictions.
- **Boosting (XGBoost):** Training trees sequentially, where each new tree corrects the errors of the previous ones.
- **Bias vs. Variance:** Balancing model simplicity with its ability to capture complex patterns.

## Model Performance Results

| Model | Accuracy | F1-Score (Churn) |
| :--- | :--- | :--- |
| Random Forest | 78.54% | 0.54 |
| **XGBoost** | **79.67%** | **0.57** |

### Confusion Matrix (XGBoost)
```
[[931 102]
 [184 190]]
```
*   **True Negatives (Non-churners):** 931
*   **True Positives (Churners):** 190
*   **False Positives:** 102
*   **False Negatives:** 184 (Area for improvement: high number of missed churners)

## Top 10 Feature Importance (Random Forest)
The model identified the following features as the most influential in predicting customer churn:

1.  **TotalCharges** (19.28%)
2.  **MonthlyCharges** (16.97%)
3.  **Tenure** (16.91%)
4.  **InternetService_Fiber optic** (3.99%)
5.  **PaymentMethod_Electronic check** (3.45%)
6.  **OnlineSecurity_Yes** (2.92%)
7.  **Contract_Two year** (2.80%)
8.  **Gender_Male** (2.70%)
9.  **TechSupport_Yes** (2.58%)
10. **PaperlessBilling_Yes** (2.51%)

## Artifacts Created
- `app/models/train_advanced_models.py`: Main training script.
- `app/models/random_forest_model.pkl`: Saved Random Forest model.
- `app/models/xgboost_model.pkl`: Saved XGBoost model.

## Next Steps
In the next phase, we will dive into **Model Explainability** using SHAP values to understand *why* the model makes specific predictions for individual customers.
