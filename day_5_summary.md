# Day 5: Logistic Regression — Your First ML Model

## Overview
Today we trained our first real churn prediction model using Logistic Regression. This step marks the transition from data engineering to predictive analytics.

## Accomplishments
- ✅ **Model Training**: Trained a Logistic Regression model with `max_iter=1000` to predict churn probabilities.
- ✅ **Evaluation Metrics**:
    - **Accuracy**: Achieved ~79% accuracy on the test set.
    - **Confusion Matrix**: Identified True Positives, False Positives, False Negatives, and True Negatives.
    - **Classification Report**: Evaluated Precision, Recall, and F1-Score to understand the model's performance on both churners and non-churners.
- ✅ **Probabilistic Predictions**: Generated churn probabilities, which are essential for business retention strategies.
- ✅ **Model Serialization**: Saved the trained model to `app/models/logistic_regression_model.pkl` for future use in APIs and deployment.

## Key Insights
- **Interpretable Baseline**: Logistic Regression serves as a reliable and interpretable baseline for classification tasks.
- **Accuracy isn't Everything**: In imbalanced datasets like churn, Recall is often more important for identifying customers at risk of leaving.
- **Model Persistence**: Serializing models allows us to deploy them without needing to retrain every time.

## Next Steps
We will move on to more advanced models (Random Forest, XGBoost) to improve our prediction performance.

---
*Internship Progress: Week 1, Day 5 Complete.*
