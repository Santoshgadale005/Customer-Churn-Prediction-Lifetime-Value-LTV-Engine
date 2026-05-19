import streamlit as st
import requests

st.set_page_config(
    page_title="Customer Churn Dashboard",
    layout="wide"
)

st.title("Customer Churn Prediction & LTV Dashboard")

st.sidebar.header("Customer Details")

tenure = st.sidebar.number_input(
    "Tenure (Months)",
    min_value=0,
    max_value=100,
    value=12
)

monthly_charges = st.sidebar.number_input(
    "Monthly Charges",
    min_value=0.0,
    value=70.0
)

total_charges = st.sidebar.number_input(
    "Total Charges",
    min_value=0.0,
    value=1000.0
)

if st.sidebar.button("Predict Churn"):

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

    st.subheader("Prediction Result")

    st.write(result)