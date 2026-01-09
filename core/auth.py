import firebase_admin
from firebase_admin import credentials, auth

import os

# Ensure Firebase Admin initializes only once
if not firebase_admin._apps:
    cred = credentials.Certificate("ServiceAccountKey.json")
    firebase_admin.initialize_app(cred)


# ---------------------------
# SIGN UP USER
# ---------------------------
def signup_user(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        return user.uid
    except Exception as e:
        return None


# ---------------------------
# LOGIN USER (email/password)
# Firebase Admin cannot login users directly
# So we simulate login by checking if user exists
# ---------------------------
def login_user(email, password):
    try:
        # Firebase Admin cannot verify password!
        # Check user exists only
        user = auth.get_user_by_email(email)
        return user.email
    except Exception:
        return None


# ---------------------------
# LOGOUT
# ---------------------------
def logout_user():
    return True
