import streamlit as st
import pandas as pd
from firebase_admin import storage
from core.db import save_dataset_metadata


# ---------------------------------------------
# Redirect if not logged in
# ---------------------------------------------
if "user" not in st.session_state or st.session_state["user"] is None:
    st.switch_page("login.py")


st.set_page_config(page_title="Upload Data — SaaS Platform")


# ---------------------------------------------
# Upload CSV → Firebase + Save Metadata
# ---------------------------------------------
def upload_user_file(user_email):
    st.title("📤 Upload Your E-Commerce Data")

    uploaded_file = st.file_uploader(
        "Upload Orders CSV (file name must be orders.csv)",
        type=["csv"]
    )

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")

        # ---------------------------------------------
        # Upload to Firebase Storage
        # ---------------------------------------------
        try:
            bucket = storage.bucket()
            blob = bucket.blob(f"{user_email}/raw/orders.csv")

            blob.upload_from_string(
                uploaded_file.getvalue(),
                content_type="text/csv"
            )

            st.info("📦 Your dataset was saved to Firebase Storage.")

        except Exception as e:
            st.error(f"Storage error: {e}")
            return None

        # ---------------------------------------------
        # Save metadata → Firestore
        # ---------------------------------------------
        try:
            save_dataset_metadata(
                email=user_email,
                filename="orders.csv",
                processed=False
            )
            st.success("📝 Metadata saved to Firestore.")

        except Exception as e:
            st.error(f"Metadata error: {e}")

        return df

    return None


# MAIN EXECUTION
user_email = st.session_state["user"]
upload_user_file(user_email)
