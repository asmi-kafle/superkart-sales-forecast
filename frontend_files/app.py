import streamlit as st
import pandas as pd
import requests

# Configure Streamlit page layout and title
st.set_page_config(page_title="SuperKart Sales Forecast", layout="centered")
st.title("SuperKart Quarterly Sales Revenue Predictor")
st.markdown(
    "Enter product and store details below for a real-time sales forecast, "
    "or upload a CSV file for batch forecasting across multiple SKUs."
)

# Backend API base URL (resolves via shared Docker network inside GitHub Codespaces)
BACKEND_URL = "http://backend:7860"

tab1, tab2 = st.tabs(["Single Product Forecast", "Batch CSV Forecast"])

# --- TAB 1: ONLINE / SINGLE PREDICTION ---
with tab1:
    st.subheader("Product & Store Attributes")

    col1, col2 = st.columns(2)
    with col1:
        product_weight = st.number_input("Product Weight", min_value=1.0, max_value=30.0, value=12.66, step=0.1)
        product_sugar_content = st.selectbox("Product Sugar Content", ["Low Sugar", "Regular", "No Sugar"])
        product_allocated_area = st.number_input(
            "Product Allocated Area (Ratio)", min_value=0.001, max_value=0.500, value=0.056, step=0.005, format="%.3f"
        )
        product_type = st.selectbox(
            "Product Type",
            [
                "Fruits and Vegetables", "Snack Foods", "Frozen Foods", "Dairy",
                "Household", "Baking Goods", "Canned", "Health and Hygiene",
                "Meat", "Soft Drinks", "Breads", "Hard Drinks",
                "Others", "Starchy Foods", "Breakfast", "Seafood"
            ],
        )
        product_mrp = st.number_input("Product MRP (USD)", min_value=10.0, max_value=500.0, value=146.74, step=1.0)

    with col2:
        store_id = st.selectbox("Store ID", ["OUT004", "OUT001", "OUT003", "OUT002"])
        store_est_year = st.selectbox("Store Establishment Year", [2009, 1999, 1998, 1987])
        store_size = st.selectbox("Store Size", ["Medium", "High", "Small"])
        store_city_type = st.selectbox("Store Location City Type", ["Tier 2", "Tier 1", "Tier 3"])
        store_type = st.selectbox(
            "Store Type",
            ["Supermarket Type2", "Supermarket Type1", "Departmental Store", "Food Mart"],
        )

    if st.button("Predict Quarterly Sales", type="primary"):
        payload = {
            "Product_Weight": product_weight,
            "Product_Sugar_Content": product_sugar_content,
            "Product_Allocated_Area": product_allocated_area,
            "Product_Type": product_type,
            "Product_MRP": product_mrp,
            "Store_Id": store_id,
            "Store_Establishment_Year": store_est_year,
            "Store_Size": store_size,
            "Store_Location_City_Type": store_city_type,
            "Store_Type": store_type,
        }
        try:
            response = requests.post(f"{BACKEND_URL}/v1/predict", json=payload, timeout=15)
            if response.status_code == 200:
                pred_val = response.json()["Predicted_Product_Store_Sales_Total_USD"]
                st.success(f"Forecasted Quarterly Sales Revenue: **USD {pred_val:,.2f}**")
            else:
                st.error(f"API Error ({response.status_code}): {response.text}")
        except Exception as e:
            st.error(f"Could not connect to backend API at {BACKEND_URL}: {e}")

# --- TAB 2: BATCH CSV PREDICTION ---
with tab2:
    st.subheader("Upload Batch Product-Store CSV")
    uploaded_file = st.file_uploader("Choose a CSV file matching SuperKart input columns", type=["csv"])

    if uploaded_file is not None:
        preview_df = pd.read_csv(uploaded_file)
        st.write("Preview of Uploaded Data:", preview_df.head())
        uploaded_file.seek(0)

        if st.button("Run Batch Forecast", type="primary"):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                response = requests.post(f"{BACKEND_URL}/v1/predictbatch", files=files, timeout=30)
                if response.status_code == 200:
                    preds_dict = response.json()
                    results_df = pd.DataFrame(
                        list(preds_dict.items()),
                        columns=["Product_Id_or_Index", "Predicted_Sales_USD"],
                    )
                    st.success(f"Generated {len(results_df)} forecasts successfully!")
                    st.dataframe(results_df)
                    csv_out = results_df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "Download Predictions CSV",
                        data=csv_out,
                        file_name="superkart_batch_predictions.csv",
                        mime="text/csv",
                    )
                else:
                    st.error(f"Batch API Error ({response.status_code}): {response.text}")
            except Exception as e:
                st.error(f"Batch prediction request failed: {e}")
