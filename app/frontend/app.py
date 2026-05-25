import streamlit as st
import requests

st.set_page_config(
    page_title="Customer Churn Prediction",
    layout="centered"
)

st.title("Customer Churn Prediction & LTV Engine")

st.subheader("Enter Customer Details")

tenure = st.number_input("Tenure", min_value=0)

monthly_charges = st.number_input(
    "Monthly Charges",
    min_value=0.0
)

total_charges = st.number_input(
    "Total Charges",
    min_value=0.0
)

if st.button("Predict"):

    data = {
        "tenure": tenure,
        "MonthlyCharges": monthly_charges,
        "TotalCharges": total_charges
    }

    response = requests.post(
        "http://127.0.0.1:8000/predict",
        json=data
    )

    result = response.json()

    st.success(f"Prediction Result: {result}")