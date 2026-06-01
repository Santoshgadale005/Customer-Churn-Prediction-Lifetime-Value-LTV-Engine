# Final Results Report

## Churn Model

Primary deployed model: XGBoost classifier.

| Metric | Value |
|---|---:|
| Accuracy | 0.791045 |
| Precision | 0.633333 |
| Recall | 0.508021 |
| F1 Score | 0.563798 |

These metrics were computed against the existing `data/engineered_telco_data.csv` train/test split using `random_state=42`, matching the training scripts.

## LTV Model

Primary deployed model: Random Forest regressor.

| Metric | Value |
|---|---:|
| MAE | 1.088890 |
| RMSE | 1.994715 |
| R2 | 0.999999 |

The current LTV target is engineered as `MonthlyCharges * tenure`, so the very high R2 is expected. In a real production deployment, LTV should be validated against future realized revenue windows to avoid overly optimistic offline metrics.

## Validation Command

```bash
.venv/bin/python - <<'PY'
import joblib, pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

df = pd.read_csv("data/engineered_telco_data.csv")
X = df.drop("Churn", axis=1)
y = df["Churn"]
_, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = joblib.load("app/models/xgboost_model.pkl")
y_pred = model.predict(X_test)

print("accuracy", accuracy_score(y_test, y_pred))
print("precision", precision_score(y_test, y_pred, zero_division=0))
print("recall", recall_score(y_test, y_pred, zero_division=0))
print("f1", f1_score(y_test, y_pred, zero_division=0))

df["LTV"] = df["MonthlyCharges"] * df["tenure"]
X_ltv = df.drop(["LTV", "Churn"], axis=1)
y_ltv = df["LTV"]
_, X_ltv_test, _, y_ltv_test = train_test_split(
    X_ltv, y_ltv, test_size=0.2, random_state=42
)
ltv_model = joblib.load("app/models/ltv_prediction_model.pkl")
ltv_pred = ltv_model.predict(X_ltv_test)

print("mae", mean_absolute_error(y_ltv_test, ltv_pred))
print("rmse", mean_squared_error(y_ltv_test, ltv_pred) ** 0.5)
print("r2", r2_score(y_ltv_test, ltv_pred))
PY
```
