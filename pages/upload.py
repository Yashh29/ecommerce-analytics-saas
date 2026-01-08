import streamlit as st
import pandas as pd
from firebase_admin import storage
from core.db import save_dataset_metadata
import uuid

# ---------------------------------------------
# Redirect if not logged in
# ---------------------------------------------
if "user" not in st.session_state or st.session_state["user"] is None:
    st.switch_page("pages/login.py")


# ---------------------------------------------
# Upload Function
# ---------------------------------------------
def upload_user_file(user_email):
    st.title("📤 Upload Your E-Commerce Data")

    uploaded_file = st.file_uploader(
        "Upload Orders CSV (orders.csv only)",
        type=["csv"]
    )

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")

        # ---------------------------------------------
        # Upload raw CSV → Firebase Storage
        # ---------------------------------------------
        bucket = storage.bucket()
        blob = bucket.blob(f"{user_email}/raw/orders.csv")

        blob.upload_from_string(
            uploaded_file.getvalue(),
            content_type='text/csv'
        )

        st.info("Your file has been securely saved to cloud storage.")

        # ---------------------------------------------
        # Store metadata in Firestore
        # ---------------------------------------------
        save_dataset_metadata(
            email=user_email,
            filename="orders.csv",
            processed=False
        )

        st.success("Metadata saved to your SaaS workspace.")

        return df

    return None


# MAIN EXECUTION
user_email = st.session_state["user"]
upload_user_file(user_email)
