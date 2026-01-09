import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth

# ----------------------------------------------------
# Initialize Firebase Admin using Streamlit Secrets
# ----------------------------------------------------
if not firebase_admin._apps:
    cred = credentials.Certificate(st.secrets["gcp_service_account"])
    firebase_admin.initialize_app(cred)


# ----------------------------------------------------
# SIGN UP USER
# ----------------------------------------------------
def signup_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return user.uid
    except Exception as e:
        return None


# ----------------------------------------------------
# LOGIN USER
# (Firebase Admin CANNOT check password, so we verify email only)
# ----------------------------------------------------
def login_user(email, password):
    try:
        user = auth.get_user_by_email(email)
        return user.email   # return the email as the login success indicator
    except Exception:
        return None


# ----------------------------------------------------
# LOGOUT USER
# ----------------------------------------------------
def logout_user():
    return True
