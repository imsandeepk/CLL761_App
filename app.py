import streamlit as st
import requests
import json
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.io as pio
import plotly
import pandas as pd


# Backend API URL (replace with your actual endpoint)
API_URL = "http://0.0.0.0:5000/get_results"

# Index options from the image
index_options  = [
    "Gold Futures Historical Data",
    "India 10-Year Bond Yield Historical Data (1)",
    "Nifty Auto Historical Data (2)",
    "Nifty Midcap 50 Historical Data",
    "Nifty Bank Historical Data",
    "Nifty 50 Historical Data (3)",
    "S&P BSE 250 LargeMidCap Historical Data",
    "Nifty 500 Historical Data",
    "Nifty Alpha 50 Historical Data",
    "India 2-Year Bond Yield Historical Data"
]

st.title("📊 Portfolio Optimizer")

# Risk limit slider
risk_limit = st.slider("Select Risk Limit", min_value=0.0, max_value=1.0, step=0.01)

# Multi-select for indexes
selected_indexes = st.multiselect("Select Indexes", index_options)

# Submit button
if st.button("Submit"):
    if not selected_indexes:
        st.warning("Please select at least one index.")
    else:
        # Prepare form data
        form_data = {
            "risk_limit": str(risk_limit),
            "assets": json.dumps(selected_indexes)  # serialize list to JSON string
        }

        try:
            response = requests.post(API_URL, data=form_data)
            if response.status_code == 200:
                result = response.json()
                st.success("✅ Results fetched successfully!")

                # Metrics
                col1, col2 = st.columns(2)
                col1.metric("📈 Sharpe Ratio", f"{result['sharpe_ratio']:.2f}")
                col2.metric("📉 Portfolio Variance", f"{result['portfolio_variance']:.5f}")

                col3, col4 = st.columns(2)
                cagr = result['cagr']
                max_dd = result['max_drawdown']
                col3.metric("CAGR", "N/A" if cagr == -1 else f"{cagr:.2%}")
                col4.metric("Max Drawdown", "N/A" if max_dd == -1 else f"{max_dd:.2%}")

                # Weights parsing: weights is a list of dicts like [{0: 1}]
                weights_raw = result["weights"]
                weights_flat = {}

                if isinstance(weights_raw, list):
                    for i, item in enumerate(weights_raw):
                        if isinstance(item, dict):
                            for k, v in item.items():
                                weights_flat[int(k)] = v
                        elif isinstance(item, float) or isinstance(item, int):
                            weights_flat[i] = item
                else:
                    st.error("Unexpected weights format.")

                # Construct table
                weights_table = {
                    "Index": [selected_indexes[i] for i in weights_flat],
                    "Weight": [weights_flat[i] for i in weights_flat]
                }

                st.markdown("### 🧮 Portfolio Weights")
                st.table(weights_table)

                # Optional: Pie chart
                df = pd.DataFrame(weights_table)
                fig = px.pie(df, names="Index", values="Weight", title="Portfolio Allocation")
                st.plotly_chart(fig)

            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"🚫 Request failed: {e}")