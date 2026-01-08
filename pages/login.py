import streamlit as st
st.set_page_config(page_title="Login — SaaS Platform", layout="centered")

from core.auth import login_user, signup_user
from db import save_user

# Initialize session state
if "user" not in st.session_state:
    st.session_state["user"] = None

# Tabs for Login / Signup
tab1, tab2 = st.tabs(["Login", "Sign Up"])

# ---------------------------
# LOGIN TAB
# ---------------------------
with tab1:
    st.header("🔐 Login to Your Account")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(email, password)
        if user:
            st.session_state["user"] = user
            save_user(email)
            st.success("Login successful!")

            # Redirect to main app
            st.switch_page("app")

# ---------------------------
# SIGNUP TAB
# ---------------------------
with tab2:
    st.header("🆕 Create an Account")

    email_su = st.text_input("New Email")
    password_su = st.text_input("New Password", type="password")

    if st.button("Sign Up"):
        signup_user(email_su, password_su)
        st.success("Account created! You can now log in.")
