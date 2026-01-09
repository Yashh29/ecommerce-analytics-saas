import streamlit as st
from core.db import save_user
from core.auth import login_user, signup_user

st.set_page_config(page_title="Login — SaaS Platform", layout="centered")

# Session state init
if "user" not in st.session_state:
    st.session_state["user"] = None

# Tabs
tab_login, tab_signup = st.tabs(["Login", "Sign Up"])

# ---------------------------------------------
# LOGIN TAB
# ---------------------------------------------
with tab_login:
    st.header("🔐 Login to Your Account")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        user = login_user(email, password)

        if user:
            st.session_state["user"] = user
            save_user(email)
            st.success("Login successful!")

            # 👇 IMPORTANT: navigate to main app
            st.switch_page("app.py")
        else:
            st.error("Invalid email or user does not exist.")


# ---------------------------------------------
# SIGNUP TAB
# ---------------------------------------------
with tab_signup:
    st.header("🆕 Create an Account")

    new_email = st.text_input("New Email", key="signup_email")
    new_pass = st.text_input("New Password", type="password", key="signup_password")

    if st.button("Sign Up"):
        result = signup_user(new_email, new_pass)

        if result:
            save_user(new_email)
            st.success("Account created successfully! Please login.")
        else:
            st.error("Sign-up failed. Try another email or check format.")
