import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from imblearn.over_sampling import SMOTE

def preprocess_data():
    # Paths
    input_path = "data/cleaned_telco_data.csv"
    output_dir = "data/processed"
    artifact_dir = "models/artifacts"
    
    # Load data
    print("Loading cleaned dataset...")
    df = pd.read_csv(input_path)
    
    # 1. Drop customerID (not a feature)
    if 'customerID' in df.columns:
        df.drop('customerID', axis=1, inplace=True)
    
    # 2. Identify Column Types
    binary_cols = []
    multi_cols = []
    num_cols = ['tenure', 'MonthlyCharges', 'TotalCharges']
    
    for col in df.select_dtypes('object').columns:
        if col == 'Churn':
            continue
        if df[col].nunique() == 2:
            binary_cols.append(col)
        else:
            multi_cols.append(col)
            
    print(f"Binary columns: {binary_cols}")
    print(f"Multiclass columns: {multi_cols}")
    print(f"Numerical columns: {num_cols}")
    
    # 3. Label Encoding (Binary Categorical)
    le = LabelEncoder()
    for col in binary_cols:
        df[col] = le.fit_transform(df[col])
        joblib.dump(le, f"{artifact_dir}/le_{col}.joblib")
        
    # 4. One-Hot Encoding (Multiclass Categorical)
    df = pd.get_dummies(df, columns=multi_cols)
    
    # 5. Encoding Target (Churn)
    df['Churn'] = df['Churn'].map({'Yes': 1, 'No': 0})
    
    # 6. Train/Test Split
    X = df.drop('Churn', axis=1)
    y = df['Churn']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 7. Scaling Numerical Features
    scaler = StandardScaler()
    X_train[num_cols] = scaler.fit_transform(X_train[num_cols])
    X_test[num_cols] = scaler.transform(X_test[num_cols])
    
    joblib.dump(scaler, f"{artifact_dir}/scaler.joblib")
    print("Scalers and encoders saved to models/artifacts/")
    
    # 8. Handling Imbalance (SMOTE)
    print(f"Before SMOTE - Class 0: {sum(y_train==0)}, Class 1: {sum(y_train==1)}")
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    print(f"After SMOTE - Class 0: {sum(y_train_resampled==0)}, Class 1: {sum(y_train_resampled==1)}")
    
    # 9. Save Processed Data
    pd.concat([X_train_resampled, y_train_resampled], axis=1).to_csv(f"{output_dir}/train_processed.csv", index=False)
    pd.concat([X_test, y_test], axis=1).to_csv(f"{output_dir}/test_processed.csv", index=False)
    
    print(f"Processed data saved to {output_dir}/")
    print("Preprocessing complete!")

if __name__ == "__main__":
    preprocess_data()
