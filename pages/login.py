import streamlit as st
st.set_page_config(page_title="Login")

from db import save_user


from core.auth import login_user, signup_user, logout_user

st.set_page_config(page_title="Login — SaaS Platform", layout="centered")

if "user" not in st.session_state:
    st.session_state["user"] = None

tab1, tab2 = st.tabs(["Login", "Sign Up"])

with tab1:
    st.header("🔐 Login to Your Account")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(email, password)
        if user:
            st.session_state["user"] = user
            st.success("Login successful!")
            save_user(email)
            st.switch_page("app.py")

with tab2:
    st.header("🆕 Create an Account")
    email_su = st.text_input("New Email")
    password_su = st.text_input("New Password", type="password")

    if st.button("Sign Up"):
        signup_user(email_su, password_su)
