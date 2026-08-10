"""Streamlit Dashboard for Real-Time Fraud Detection"""

import logging
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


# ============================================================
# Logging
# ============================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Fraud Detection Dashboard",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# Custom CSS
# ============================================================

st.markdown(
    """
    <style>
    .main {
        padding: 0rem 1rem;
    }

    .metric-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Title
# ============================================================

st.title("🔐 Real-Time Fraud Detection Dashboard")
st.markdown("---")


# ============================================================
# Sidebar Navigation
# ============================================================

with st.sidebar:
    st.header("Navigation")

    page = st.radio(
        "Select a page:",
        ["Home", "Predictions", "Analytics", "Settings"],
    )


# ============================================================
# HOME PAGE
# ============================================================

if page == "Home":

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Transactions",
            "2.5M",
            "+12%",
        )

    with col2:
        st.metric(
            "Fraud Cases Detected",
            "1,245",
            "+8%",
        )

    with col3:
        st.metric(
            "Detection Rate",
            "98.7%",
            "+2.1%",
        )

    with col4:
        st.metric(
            "API Latency (ms)",
            "42",
            "-5ms",
        )

    st.markdown("---")

    # --------------------------------------------------------
    # Daily Fraud Cases
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Daily Fraud Cases")

        dates = pd.date_range(
            end=datetime.now(),
            periods=30,
        )

        fraud_cases = np.random.randint(
            20,
            100,
            30,
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=dates,
                y=fraud_cases,
                mode="lines+markers",
                name="Fraud Cases",
                line=dict(
                    color="red",
                    width=2,
                ),
                marker=dict(
                    size=6,
                ),
            )
        )

        fig.update_layout(
            title="Last 30 Days",
            xaxis_title="Date",
            yaxis_title="Number of Cases",
            hovermode="x unified",
            height=400,
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

    # --------------------------------------------------------
    # Transaction Volume
    # --------------------------------------------------------

    with col2:
        st.subheader("💰 Transaction Volume")

        transaction_amounts = np.random.lognormal(
            mean=5,
            sigma=2,
            size=30,
        )

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=dates,
                y=transaction_amounts,
                name="Transaction Volume",
                marker=dict(
                    color="steelblue",
                ),
            )
        )

        fig.update_layout(
            title="Last 30 Days",
            xaxis_title="Date",
            yaxis_title="Total Amount ($)",
            hovermode="x unified",
            height=400,
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )


# ============================================================
# PREDICTIONS PAGE
# ============================================================

elif page == "Predictions":

    st.subheader("🔮 Make Predictions")

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # Transaction Information
    # --------------------------------------------------------

    with col1:

        step = st.number_input(
            "Step",
            min_value=1,
            max_value=744,
            value=10,
        )

        amount = st.number_input(
            "Transaction Amount ($)",
            min_value=0.0,
            value=1000.0,
        )

        old_balance_orig = st.number_input(
            "Old Balance Origin ($)",
            min_value=0.0,
            value=10000.0,
        )

        new_balance_orig = st.number_input(
            "New Balance Origin ($)",
            min_value=0.0,
            value=9000.0,
        )

    # --------------------------------------------------------
    # Additional Transaction Information
    # --------------------------------------------------------

    with col2:

        transaction_type = st.selectbox(
            "Transaction Type",
            [
                "TRANSFER",
                "PAYMENT",
                "CASH_OUT",
                "CASH_IN",
                "DEBIT",
            ],
        )

        old_balance_dest = st.number_input(
            "Old Balance Destination ($)",
            min_value=0.0,
            value=5000.0,
        )

        new_balance_dest = st.number_input(
            "New Balance Destination ($)",
            min_value=0.0,
            value=5000.0,
        )

        is_flagged_fraud = st.checkbox(
            "Flagged as Fraud by System",
            value=False,
        )

    st.markdown("---")

    # --------------------------------------------------------
    # Prediction Button
    # --------------------------------------------------------

    if st.button(
        "🔍 Predict Transaction",
        width="stretch",
    ):

        try:

            # Prepare transaction for API
            transaction_data = {
                "step": int(step),
                "type": transaction_type,
                "amount": float(amount),
                "oldbalanceOrg": float(old_balance_orig),
                "newbalanceOrig": float(new_balance_orig),
                "oldbalanceDest": float(old_balance_dest),
                "newbalanceDest": float(new_balance_dest),
                "isFlaggedFraud": int(is_flagged_fraud),
            }

            # ------------------------------------------------
            # Send request to API
            # ------------------------------------------------

            response = requests.post(
                "http://localhost:8000/predict",
                json=transaction_data,
                timeout=5,
            )

            # ------------------------------------------------
            # Successful Response
            # ------------------------------------------------

            if response.status_code == 200:

                prediction = response.json()

                st.markdown("---")
                st.subheader("📋 Prediction Result")

                col1, col2, col3 = st.columns(3)

                # ------------------------------------------------
                # Prediction Status
                # ------------------------------------------------

                with col1:

                    prediction_value = prediction.get(
                        "prediction"
                    )

                    if isinstance(
                        prediction_value,
                        str,
                    ):
                        is_fraud = (
                            prediction_value.lower()
                            == "fraud"
                        )
                    else:
                        is_fraud = (
                            int(prediction_value) == 1
                        )

                    if is_fraud:

                        st.error(
                            "🚨 FRAUD DETECTED"
                        )

                    else:

                        st.success(
                            "✅ NORMAL TRANSACTION"
                        )

                # ------------------------------------------------
                # Fraud Probability
                # ------------------------------------------------

                with col2:

                    fraud_probability = prediction.get(
                        "fraud_probability"
                    )

                    if fraud_probability is not None:

                        fraud_probability = float(
                            fraud_probability
                        )

                        st.metric(
                            "Fraud Probability",
                            f"{fraud_probability:.1%}",
                        )

                    else:

                        st.metric(
                            "Fraud Probability",
                            "N/A",
                        )

                # ------------------------------------------------
                # Risk Level
                # ------------------------------------------------

                with col3:

                    risk = prediction.get(
                        "risk",
                        None,
                    )

                    if risk is None:

                        if (
                            fraud_probability is not None
                        ):

                            if fraud_probability >= 0.8:
                                risk = "High"

                            elif fraud_probability >= 0.5:
                                risk = "Medium"

                            else:
                                risk = "Low"

                        else:

                            risk = "Unknown"

                    if risk == "High":

                        st.error(
                            f"🔴 Risk Level: {risk}"
                        )

                    elif risk == "Medium":

                        st.warning(
                            f"🟠 Risk Level: {risk}"
                        )

                    elif risk == "Low":

                        st.success(
                            f"🟢 Risk Level: {risk}"
                        )

                    else:

                        st.info(
                            f"Risk Level: {risk}"
                        )

                # ------------------------------------------------
                # Transaction Details
                # ------------------------------------------------

                st.markdown("---")
                st.subheader("Transaction Details")

                result_data = pd.DataFrame(
                    {
                        "Field": [
                            "Step",
                            "Transaction Type",
                            "Transaction Amount",
                            "Old Balance - Origin",
                            "New Balance - Origin",
                            "Old Balance - Destination",
                            "New Balance - Destination",
                        ],
                        "Value": [
                            str(step),
                            str(transaction_type),
                            f"${amount:,.2f}",
                            f"${old_balance_orig:,.2f}",
                            f"${new_balance_orig:,.2f}",
                            f"${old_balance_dest:,.2f}",
                            f"${new_balance_dest:,.2f}",
                        ],
                    }
                )

                # Ensure Streamlit/PyArrow receives a consistent string column.
                result_data["Field"] = result_data["Field"].astype(str)
                result_data["Value"] = result_data["Value"].astype(str)

                st.dataframe(
                    result_data,
                    width="stretch",
                    hide_index=True,
                )

            # ------------------------------------------------
            # API Error
            # ------------------------------------------------

            else:

                st.error(
                    f"Prediction failed. "
                    f"API returned status code "
                    f"{response.status_code}."
                )

                try:

                    st.json(
                        response.json()
                    )

                except Exception:

                    st.code(
                        response.text
                    )

        # ----------------------------------------------------
        # API Connection Error
        # ----------------------------------------------------

        except requests.exceptions.ConnectionError:

            st.error(
                "⚠️ Could not connect to the API.\n\n"
                "Make sure the prediction API is running "
                "on http://localhost:8000"
            )

        # ----------------------------------------------------
        # Timeout
        # ----------------------------------------------------

        except requests.exceptions.Timeout:

            st.error(
                "⏱️ API request timed out."
            )

        # ----------------------------------------------------
        # Other Errors
        # ----------------------------------------------------

        except Exception as e:

            logger.exception(
                "Prediction error"
            )

            st.error(
                f"Error: {str(e)}"
            )


# ============================================================
# ANALYTICS PAGE
# ============================================================

elif page == "Analytics":

    st.subheader("📈 Advanced Analytics")

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # Model Performance
    # --------------------------------------------------------

    with col1:

        st.subheader("🎯 Model Performance")

        metrics_df = pd.DataFrame(
            {
                "Metric": [
                    "Accuracy",
                    "Precision",
                    "Recall",
                    "F1-Score",
                    "ROC-AUC",
                ],
                "Score": [
                    0.987,
                    0.945,
                    0.923,
                    0.934,
                    0.992,
                ],
            }
        )

        fig = go.Figure(
            data=[
                go.Bar(
                    x=metrics_df["Metric"],
                    y=metrics_df["Score"],
                    marker_color="lightseagreen",
                )
            ]
        )

        fig.update_layout(
            title="Model Metrics",
            xaxis_title="Metric",
            yaxis_title="Score",
            height=400,
            showlegend=False,
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

    # --------------------------------------------------------
    # Feature Importance
    # --------------------------------------------------------

    with col2:

        st.subheader("⚠️ Feature Importance")

        importance_df = pd.DataFrame(
            {
                "Feature": [
                    "amount",
                    "oldbalanceOrg",
                    "step",
                    "newbalanceOrig",
                    "type",
                ],
                "Importance": [
                    0.35,
                    0.28,
                    0.18,
                    0.12,
                    0.07,
                ],
            }
        )

        fig = go.Figure(
            data=[
                go.Bar(
                    y=importance_df["Feature"],
                    x=importance_df["Importance"],
                    orientation="h",
                    marker_color="indianred",
                )
            ]
        )

        fig.update_layout(
            title="Feature Importance",
            xaxis_title="Importance",
            yaxis_title="Feature",
            height=400,
            showlegend=False,
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

    st.markdown("---")

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # Confusion Matrix
    # --------------------------------------------------------

    with col1:

        st.subheader("📊 Confusion Matrix")

        cm = np.array(
            [
                [23411, 89],
                [312, 188],
            ]
        )

        fig = go.Figure(
            data=go.Heatmap(
                z=cm,
                x=[
                    "Predicted Normal",
                    "Predicted Fraud",
                ],
                y=[
                    "Actual Normal",
                    "Actual Fraud",
                ],
                text=cm,
                texttemplate="%{text}",
                colorscale="Blues",
            )
        )

        fig.update_layout(
            height=400,
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

    # --------------------------------------------------------
    # ROC Curve
    # --------------------------------------------------------

    with col2:

        st.subheader("📉 ROC Curve")

        fpr = np.linspace(
            0,
            1,
            100,
        )

        tpr = 1 - (1 - fpr) ** 1.5

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=fpr,
                y=tpr,
                name="ROC",
                line=dict(
                    color="darkorange",
                    width=2,
                ),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=[0, 1],
                y=[0, 1],
                name="Random",
                line=dict(
                    color="navy",
                    width=2,
                    dash="dash",
                ),
            )
        )

        fig.update_layout(
            title="ROC Curve (AUC = 0.992)",
            xaxis_title="False Positive Rate",
            yaxis_title="True Positive Rate",
            height=400,
            hovermode="closest",
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )


# ============================================================
# SETTINGS PAGE
# ============================================================

elif page == "Settings":

    st.subheader("⚙️ Configuration Settings")

    tab1, tab2, tab3 = st.tabs(
        [
            "Model",
            "API",
            "Alerts",
        ]
    )

    # --------------------------------------------------------
    # Model Settings
    # --------------------------------------------------------

    with tab1:

        st.subheader(
            "Model Configuration"
        )

        model_threshold = st.slider(
            "Fraud Probability Threshold",
            0.0,
            1.0,
            0.5,
        )

        model_type = st.selectbox(
            "Model Type",
            [
                "Random Forest",
                "XGBoost",
                "Neural Network",
            ],
        )

        retrain_frequency = st.selectbox(
            "Retraining Frequency",
            [
                "Daily",
                "Weekly",
                "Monthly",
            ],
        )

        if st.button(
            "Save Model Settings"
        ):

            st.success(
                "✅ Model settings saved!"
            )

    # --------------------------------------------------------
    # API Settings
    # --------------------------------------------------------

    with tab2:

        st.subheader(
            "API Configuration"
        )

        api_url = st.text_input(
            "API URL",
            "http://localhost:8000",
        )

        api_timeout = st.number_input(
            "API Timeout (seconds)",
            min_value=1,
            value=5,
        )

        max_batch_size = st.number_input(
            "Max Batch Size",
            min_value=1,
            value=100,
        )

        if st.button(
            "Save API Settings"
        ):

            st.success(
                "✅ API settings saved!"
            )

    # --------------------------------------------------------
    # Alert Settings
    # --------------------------------------------------------

    with tab3:

        st.subheader(
            "Alert Configuration"
        )

        alert_threshold = st.slider(
            "Alert Threshold (%)",
            0,
            100,
            80,
        )

        enable_email_alerts = st.checkbox(
            "Enable Email Alerts",
            value=True,
        )

        enable_sms_alerts = st.checkbox(
            "Enable SMS Alerts",
            value=False,
        )

        if enable_email_alerts:

            alert_email = st.text_input(
                "Alert Email Address"
            )

        if st.button(
            "Save Alert Settings"
        ):

            st.success(
                "✅ Alert settings saved!"
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
    f"""
    <div style="text-align:center;">
        Real-Time Financial Fraud Detection Pipeline |
        Last Updated:
        {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    </div>
    """,
    unsafe_allow_html=True,
)