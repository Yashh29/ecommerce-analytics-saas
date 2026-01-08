import streamlit as st
import pyrebase
from firebase_config import firebase_config

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()


def login_user(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        return user
    except Exception as e:
        st.error("Invalid login credentials")
        return None


from core.db import db

def signup_user(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)

        # Create user document in Firestore
        user_id = user['localId']
        db.collection("users").document(user_id).set({
            "email": email,
            "created_at": firestore.SERVER_TIMESTAMP
        })

        st.success("Account created successfully! Please login.")
    except:
        st.error("Signup failed. Email may already exist.")


def logout_user():
    if "user" in st.session_state:
        del st.session_state["user"]
