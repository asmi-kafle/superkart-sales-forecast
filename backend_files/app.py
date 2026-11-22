# Import necessary libraries
import joblib
import pandas as pd
from flask import Flask, request, jsonify

# Initialize the Flask application
superkart_api = Flask("SuperKart Sales Forecast Predictor")

# Load the serialized preprocessing + model pipeline
model = joblib.load("superkart_model.joblib")


def prepare_features(df_input):
    """
    Applies the exact pre-pipeline feature transformations used during training:
    - Standardizes 'reg' -> 'Regular' in Product_Sugar_Content
    - Derives Store_Age = 2026 - Store_Establishment_Year
    """
    df_proc = df_input.copy()
    if "Product_Sugar_Content" in df_proc.columns:
        df_proc["Product_Sugar_Content"] = df_proc["Product_Sugar_Content"].replace({"reg": "Regular"})
    if "Store_Establishment_Year" in df_proc.columns and "Store_Age" not in df_proc.columns:
        df_proc["Store_Age"] = 2026 - df_proc["Store_Establishment_Year"]
    return df_proc


# Define home route (GET request)
@superkart_api.get("/")
def home():
    """Health-check endpoint confirming the SuperKart prediction service is live."""
    return "Welcome to the SuperKart Sales Revenue Forecast API!"


# Define endpoint for single product-store prediction (POST request)
@superkart_api.post("/v1/predict")
def predict_sales():
    """
    Accepts JSON payload for a single product-store record and returns
    the forecasted quarterly sales revenue in USD.
    """
    payload = request.get_json()

    sample = {
        "Product_Weight": float(payload["Product_Weight"]),
        "Product_Sugar_Content": payload["Product_Sugar_Content"],
        "Product_Allocated_Area": float(payload["Product_Allocated_Area"]),
        "Product_Type": payload["Product_Type"],
        "Product_MRP": float(payload["Product_MRP"]),
        "Store_Id": payload["Store_Id"],
        "Store_Establishment_Year": int(payload["Store_Establishment_Year"]),
        "Store_Size": payload["Store_Size"],
        "Store_Location_City_Type": payload["Store_Location_City_Type"],
        "Store_Type": payload["Store_Type"],
    }

    input_df = prepare_features(pd.DataFrame([sample]))
    predicted_sales = round(float(model.predict(input_df)[0]), 2)

    return jsonify({"Predicted_Product_Store_Sales_Total_USD": predicted_sales})


# Define endpoint for batch predictions via CSV upload (POST request)
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    """
    Accepts a CSV file upload containing multiple product-store records
    and returns a JSON dictionary mapping Product_Id (or row index) to forecasted sales.
    """
    file = request.files["file"]
    raw_df = pd.read_csv(file)
    input_df = prepare_features(raw_df)

    predictions = [round(float(val), 2) for val in model.predict(input_df)]

    if "Product_Id" in raw_df.columns:
        keys = raw_df["Product_Id"].astype(str).tolist()
    else:
        keys = [str(i) for i in range(len(predictions))]

    return jsonify(dict(zip(keys, predictions)))


if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=True)
