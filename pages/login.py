import streamlit as st
from core.db import save_user
from core.auth import login_user, signup_user

st.set_page_config(page_title="Login — SaaS Platform", layout="centered")

# ---------------------------------------------
# INIT SESSION
# ---------------------------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None

# ---------------------------------------------
# UI
# ---------------------------------------------
tab1, tab2 = st.tabs(["🔐 Login", "🆕 Sign Up"])

# ---------------------------------------------
# LOGIN TAB
# ---------------------------------------------
with tab1:
    st.header("Login to Your Account")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(email, password)

        if user:
            st.session_state["user"] = email
            save_user(email)
            st.success("Login successful! Redirecting...")
            st.switch_page("app")
        else:
            st.error("Invalid email or password")


# ---------------------------------------------
# SIGN UP TAB
# ---------------------------------------------
with tab2:
    st.header("Create a New Account")

    email_su = st.text_input("New Email")
    password_su = st.text_input("New Password", type="password")

    if st.button("Sign Up"):
        created = signup_user(email_su, password_su)
        if created:
            st.success("Account created successfully! You can now log in.")
        else:
            st.error("Failed to create account. Try again.")
