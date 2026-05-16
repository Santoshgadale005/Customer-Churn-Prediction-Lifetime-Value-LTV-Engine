import pandas as pd
import shap
import joblib
import os
import matplotlib.pyplot as plt

def generate_shap_explanations():
    print("🚀 Starting SHAP Explainability Analysis...")

    # Create directory for reports if it doesn't exist
    report_dir = "reports/shap"
    os.makedirs(report_dir, exist_ok=True)

    # 1. Load Dataset
    print("📂 Loading preprocessed data...")
    df = pd.read_csv("data/preprocessed_telco_data.csv")

    # 2. Separate Features and Target
    X = df.drop("Churn", axis=1)
    y = df["Churn"]

    # 3. Load Trained Model (XGBoost)
    print("🤖 Loading trained XGBoost model...")
    try:
        model = joblib.load("app/models/xgboost_model.pkl")
    except FileNotFoundError:
        print("❌ Error: XGBoost model not found at app/models/xgboost_model.pkl")
        return

    # 4. Create SHAP Explainer
    print("🧠 Initializing SHAP TreeExplainer...")
    explainer = shap.TreeExplainer(model)

    # 5. Generate SHAP Values
    print("🔢 Generating SHAP values (this may take a moment)...")
    shap_values = explainer.shap_values(X)

    # 6. Global Explainability - Summary Plot
    print("📊 Generating Global Summary Plot...")
    plt.figure(figsize=(10, 6))
    shap.summary_plot(shap_values, X, show=False)
    plt.tight_layout()
    plt.savefig(f"{report_dir}/shap_summary_plot.png")
    plt.close()
    print(f"✅ Summary plot saved to {report_dir}/shap_summary_plot.png")

    # 7. Feature Dependence Plot (e.g., tenure)
    print("📈 Generating Feature Dependence Plot for 'tenure'...")
    plt.figure(figsize=(8, 5))
    shap.dependence_plot("tenure", shap_values, X, show=False)
    plt.tight_layout()
    plt.savefig(f"{report_dir}/shap_dependence_tenure.png")
    plt.close()
    print(f"✅ Dependence plot saved to {report_dir}/shap_dependence_tenure.png")

    # 8. Local Explainability - Individual Prediction
    customer_index = 10
    print(f"👤 Explaining prediction for Customer at index {customer_index}...")
    
    # Force plot usually generates HTML. For a script, we'll save it as HTML.
    force_plot = shap.force_plot(
        explainer.expected_value,
        shap_values[customer_index],
        X.iloc[customer_index],
        matplotlib=False # Set to False to get the Javascript-based HTML plot
    )
    shap.save_html(f"{report_dir}/customer_{customer_index}_explanation.html", force_plot)
    print(f"✅ Local explanation (HTML) saved to {report_dir}/customer_{customer_index}_explanation.html")

    # 9. Save Feature Importance DataFrame
    print("📋 Calculating Global Feature Importance...")
    importance_df = pd.DataFrame({
        "Feature": X.columns,
        "Importance": pd.Series(shap_values).apply(lambda x: abs(x).mean()) if isinstance(shap_values, list) else abs(shap_values).mean(axis=0)
    })
    
    # Handle multi-class or list output from shap_values if necessary 
    # (XGBoost binary classification usually returns a single array or list of one array)
    if isinstance(shap_values, list):
        # If it's a list (common in some versions for binary), take the first one or the one for the positive class
        shap_vals_matrix = shap_values[1] if len(shap_values) > 1 else shap_values[0]
        importance_df["Importance"] = abs(shap_vals_matrix).mean(axis=0)
    else:
        importance_df["Importance"] = abs(shap_values).mean(axis=0)

    importance_df = importance_df.sort_values(by="Importance", ascending=False)
    
    print("\n🔥 Top 10 Most Influential Features (Global):")
    print(importance_df.head(10).to_string(index=False))
    
    importance_df.to_csv(f"{report_dir}/feature_importance_shap.csv", index=False)
    print(f"\n✅ Feature importance data saved to {report_dir}/feature_importance_shap.csv")
    
    print("\n✨ SHAP Explainability Analysis Complete!")

if __name__ == "__main__":
    generate_shap_explanations()
