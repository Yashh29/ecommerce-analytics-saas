import streamlit as st
import pandas as pd
import firebase_admin
from firebase_admin import credentials, storage
from core.db import save_dataset_metadata


# ----------------------------------------------------
# Initialize Firebase (using Streamlit Secrets)
# ----------------------------------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["gcp_service_account"])
    firebase_admin.initialize_app(cred, {
        "storageBucket": "ecommerce-analytics-saas-f2a2f.appspot.com"
    })


# ----------------------------------------------------
# Redirect if not logged in
# ----------------------------------------------------
if "user" not in st.session_state or st.session_state["user"] is None:
    st.switch_page("pages/login.py")


# ----------------------------------------------------
# File Upload Function
# ----------------------------------------------------
def upload_user_file(user_email):
    st.title("📤 Upload Your E-Commerce Data")

    uploaded_file = st.file_uploader(
        "Upload Orders CSV (orders.csv only)",
        type=["csv"]
    )

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")

        # ------------------------------------------------
        # Save file to Firebase Storage (raw data)
        # ------------------------------------------------
        bucket = storage.bucket()
        blob = bucket.blob(f"{user_email}/raw/orders.csv")

        blob.upload_from_string(
            uploaded_file.getvalue(),
            content_type='text/csv'
        )

        st.info("Your file has been securely saved to cloud storage.")

        # ------------------------------------------------
        # Save metadata to Firestore
        # ------------------------------------------------
        save_dataset_metadata(
            email=user_email,
            filename="orders.csv",
            processed=False
        )

        st.success("Metadata saved to your SaaS workspace.")

        return df

    return None


# ----------------------------------------------------
# MAIN EXECUTION
# ----------------------------------------------------
user_email = st.session_state["user"]
upload_user_file(user_email)
