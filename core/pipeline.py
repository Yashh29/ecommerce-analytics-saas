import pandas as pd
from firebase_admin import storage
import io

def process_user_data(user_id):
    bucket = storage.bucket()

    # Read raw file
    blob = bucket.blob(f"users/{user_id}/raw/orders.csv")
    raw_data = blob.download_as_bytes()

    df = pd.read_csv(io.BytesIO(raw_data))

    # ---- YOUR EXISTING PIPELINE LOGIC ----
    # CLEANING, FEATURE ENGINEERING, CLV, CHURN, SEGMENTATION

    df["clv_proxy"] = df["order_amount"]  # placeholder
    df["churn_probability"] = df["customer_id"].astype(str).str.len() / 10
    df["risk_level"] = df["churn_probability"].apply(
        lambda x: "High Risk" if x > 0.5 else "Low Risk"
    )

    # Save processed output
    processed_blob = bucket.blob(f"users/{user_id}/processed/dashboard_data.csv")
    processed_blob.upload_from_string(df.to_csv(index=False), content_type="text/csv")

    return df
