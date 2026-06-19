"""
Script to generate a realistic production_predictions.csv dataset for Day 28.

This creates a simulated production dataset that:
  - Uses the same feature schema as the training data
  - Introduces controlled drift in MonthlyCharges and RevenuePerMonth
    (simulating market pricing shifts)
  - Includes predicted_churn and churn_probability columns
  - Deliberately omits actual_churn (as is common in real production)

Run once to seed the file:
    python scripts/generate_production_data.py
"""

import os
import numpy as np
import pandas as pd

TRAINING_DATA_PATH  = "data/engineered_telco_data.csv"
PRODUCTION_DATA_PATH = "data/production_predictions.csv"
N_PRODUCTION_RECORDS = 500
RANDOM_SEED = 99


def main():
    print("Loading training data baseline...")
    df = pd.read_csv(TRAINING_DATA_PATH)
    
    # Sample a subset to form our simulated production records
    rng = np.random.default_rng(RANDOM_SEED)
    sample = df.sample(n=min(N_PRODUCTION_RECORDS, len(df)), random_state=RANDOM_SEED).copy()
    sample = sample.reset_index(drop=True)

    # ── Introduce controlled DATA DRIFT ──────────────────────────────────────
    # Simulate a market pricing shift: MonthlyCharges has drifted upward ~35%
    if "MonthlyCharges" in sample.columns:
        drift_factor = rng.normal(loc=1.35, scale=0.05, size=len(sample))
        sample["MonthlyCharges"] = (sample["MonthlyCharges"] * drift_factor).round(2)

    if "TotalCharges" in sample.columns:
        drift_factor = rng.normal(loc=1.30, scale=0.06, size=len(sample))
        sample["TotalCharges"] = (sample["TotalCharges"] * drift_factor).round(2)

    # Derived engineered feature — recompute after drift
    if "RevenuePerMonth" in sample.columns and "tenure" in sample.columns:
        sample["RevenuePerMonth"] = (
            sample["TotalCharges"] / sample["tenure"].clip(lower=1)
        ).round(2)

    # ── Add production metadata columns ──────────────────────────────────────
    # Simulated prediction timestamps spread over the last 30 days
    base_ts = pd.Timestamp("2026-06-01")
    timestamps = [
        base_ts + pd.Timedelta(days=float(rng.uniform(0, 18)))
        for _ in range(len(sample))
    ]
    sample["prediction_timestamp"] = [ts.isoformat() for ts in timestamps]

    # Simulate churn probabilities (slightly higher than training due to drift)
    churn_proba = rng.beta(a=2.5, b=5.5, size=len(sample))
    sample["churn_probability"]  = churn_proba.round(4)
    sample["predicted_churn"]    = (churn_proba > 0.5).astype(int)
    sample["predicted_ltv"]      = rng.normal(loc=4800, scale=1500, size=len(sample)).round(2)

    # actual_churn intentionally left out to simulate real production scenario
    # (ground truth labels not yet collected)

    os.makedirs("data", exist_ok=True)
    sample.to_csv(PRODUCTION_DATA_PATH, index=False)

    print(f"✅ Production predictions saved: {PRODUCTION_DATA_PATH}")
    print(f"   Records        : {len(sample)}")
    print(f"   Predicted churn rate: {sample['predicted_churn'].mean():.2%}")
    if "MonthlyCharges" in sample.columns:
        train_mean = pd.read_csv(TRAINING_DATA_PATH)["MonthlyCharges"].mean()
        prod_mean  = sample["MonthlyCharges"].mean()
        print(f"   MonthlyCharges : Train μ={train_mean:.2f} → Prod μ={prod_mean:.2f}  (Δ={prod_mean - train_mean:+.2f})")


if __name__ == "__main__":
    main()
