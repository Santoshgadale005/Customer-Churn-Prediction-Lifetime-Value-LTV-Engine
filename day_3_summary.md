# Day 3: Exploratory Data Analysis (EDA)

## Overview
The goal of Day 3 was to dive deep into the dataset to understand the drivers behind customer churn. We focused on statistical analysis and visualization to identify key features that correlate with customer attrition.

## Accomplishments
- ✅ **Setup Analysis Environment**: Initialized Jupyter notebooks for structured data exploration.
- ✅ **Churn Pattern Identification**:
    - Discovered that **Contract type** (Month-to-month) is the strongest indicator of churn.
    - Identified that customers with **Electronic check** payment methods have higher churn rates.
- ✅ **Correlation Analysis**:
    - Performed correlation matrix mapping to see relationships between tenure, monthly charges, and churn.
    - Visualized the impact of **Tenure** (new customers are more likely to leave).
- ✅ **Data Profiling**:
    - Analyzed distributions of numerical features (`MonthlyCharges`, `TotalCharges`).
    - Checked for class imbalance (found ~26% churn rate).

## Key Insights
1. **Tenure**: The risk of churn decreases significantly after the first 12 months.
2. **Monthly Charges**: High monthly charges are positively correlated with churn.
3. **Services**: Customers with Fiber Optic internet service churn at a higher rate than DSL.

## Current Status
The exploratory phase is complete, providing the necessary insights to drive the feature engineering process.

---
*Internship Progress: Week 1, Day 3 Complete.*
