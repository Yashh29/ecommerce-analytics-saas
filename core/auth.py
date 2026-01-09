import firebase_admin
from firebase_admin import credentials, auth
import streamlit as st

# Load Firebase Admin using Streamlit Secrets
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["gcp_service_account"])
    firebase_admin.initialize_app(cred)


def signup_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return user.uid
    except Exception:
        return None


def login_user(email, password):
    try:
        # Firebase Admin cannot check password, only checks user existence
        user = auth.get_user_by_email(email)
        return user.email
    except Exception:
        return None


def logout_user():
    return True
