import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from google.cloud import storage
import pandas as pd
import os

# ---------------------------------------------
# Redirect if not logged in
# ---------------------------------------------
if "user" not in st.session_state or st.session_state["user"] is None:
    st.switch_page("pages/login.py")   # IMPORTANT


# ---------------------------------------------
# Firebase Storage Client
# ---------------------------------------------
import json
from google.oauth2 import service_account

def get_storage_client():
    """Create a Storage Client using credentials in st.secrets"""
    creds_dict = st.secrets["gcp_service_account"]
    credentials = service_account.Credentials.from_service_account_info(creds_dict)
    return storage.Client(credentials=credentials, project=creds_dict["project_id"])



BUCKET_NAME = "ecommerce-analytics-saas-f2a2f.appspot.com"


# ---------------------------------------------
# Check if file exists
# ---------------------------------------------
def user_file_exists(user_email, filename):
    try:
        client = get_storage_client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{user_email}/{filename}")
        return blob.exists()
    except Exception as e:
        st.error(f"Storage check failed: {e}")
        return False


# ---------------------------------------------
# Load file from Storage
# ---------------------------------------------
def load_user_file(user_email, filename):
    try:
        client = get_storage_client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{user_email}/{filename}")

        if not blob.exists():
            return None

        raw = blob.download_as_bytes()
        return pd.read_csv(pd.io.common.BytesIO(raw))

    except Exception as e:
        st.warning(f"Error loading file: {e}")
        return None


# ---------------------------------------------
# Local fallback
# ---------------------------------------------
@st.cache_data
def load_local_dashboard_data():
    return pd.read_csv("core/data/processed/dashboard_data.csv")

@st.cache_data
def load_local_forecast_data():
    df = pd.read_csv("core/data/processed/segment_revenue_forecast.csv")
    df["order_month"] = pd.to_datetime(df["order_month"])
    return df


# ---------------------------------------------
# Load dashboard data
# ---------------------------------------------
def get_dashboard_data():
    email = st.session_state["user"]

    if user_file_exists(email, "dashboard_data.csv"):
        df = load_user_file(email, "dashboard_data.csv")
        if df is not None:
            st.success("Loaded personalized dashboard data 🚀")
            return df

    st.info("Using demo dataset.")
    return load_local_dashboard_data()


def get_forecast_data():
    email = st.session_state["user"]

    if user_file_exists(email, "segment_revenue_forecast.csv"):
        df = load_user_file(email, "segment_revenue_forecast.csv")
        if df is not None:
            df["order_month"] = pd.to_datetime(df["order_month"])
            st.success("Loaded personalized forecast data 🚀")
            return df

    st.info("Using demo forecast dataset.")
    return load_local_forecast_data()


# ---------------------------------------------
# Load final data
# ---------------------------------------------
data = get_dashboard_data()
forecast_df = get_forecast_data()

# ---------------------------------------------
# UI — Dashboard
# ---------------------------------------------
st.title("📊 Enterprise E-Commerce Analytics Platform")
st.markdown("For Executives • Marketing • Strategy Teams")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📌 Executive Overview",
    "🧩 Customer Segments",
    "⚠️ Churn Risk Analysis",
    "🎯 Recommendations",
    "📈 Revenue Forecast"
])


# TAB 1
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", data["customer_id"].nunique())
    col2.metric("Churn Rate (%)", f"{data['actual_churn'].mean()*100:.2f}")
    col3.metric("High-Risk (%)", f"{(data['risk_level']=='High Risk').mean()*100:.2f}")
    col4.metric("Average CLV", f"{data['clv_proxy'].mean():.2f}")

    st.divider()

    fig, ax = plt.subplots()
    data["risk_level"].value_counts().plot.pie(autopct="%1.1f%%", ax=ax)
    ax.set_ylabel("")
    st.pyplot(fig)

    st.subheader("Churn Probability vs CLV")
    fig, ax = plt.subplots()
    ax.scatter(data["clv_proxy"], data["churn_probability"], alpha=0.6)
    ax.set_xlabel("CLV")
    ax.set_ylabel("Churn Probability")
    st.pyplot(fig)


# TAB 2
with tab2:
    summary = data.groupby("segment").agg(
        customers=("customer_id", "count"),
        avg_clv=("clv_proxy", "mean"),
        churn_rate=("actual_churn", "mean")
    ).reset_index()

    st.dataframe(summary, use_container_width=True)

    st.subheader("Customers per Segment")
    fig, ax = plt.subplots()
    summary.set_index("segment")["customers"].plot(kind="bar", ax=ax)
    st.pyplot(fig)


# TAB 3
with tab3:
    risk = st.selectbox("Risk Level", ["All", "High Risk", "Medium Risk", "Low Risk"])
    df = data if risk == "All" else data[data["risk_level"] == risk]

    st.dataframe(
        df[["customer_id", "segment", "clv_proxy", "churn_probability", "risk_level"]]
        .sort_values("churn_probability", ascending=False),
        use_container_width=True
    )


# TAB 4
with tab4:
    st.markdown("""
    ### Retention Recommendations
    - **High Risk + High CLV** → Manual VIP retention  
    - **High Risk + Low CLV** → Automated campaigns  
    - **Medium Risk** → Discounts + email  
    - **Low Risk** → Normal engagement  
    """)


# TAB 5
with tab5:
    segs = st.multiselect(
        "Select Segments",
        forecast_df["segment"].unique(),
        default=forecast_df["segment"].unique()
    )

    fdf = forecast_df[forecast_df["segment"].isin(segs)]

    fig, ax = plt.subplots(figsize=(12, 5))
    for s in fdf["segment"].unique():
        sd = fdf[fdf["segment"] == s]
        ax.plot(sd["order_month"], sd["forecast"], marker="o", label=f"Segment {s}")

    ax.legend()
    st.pyplot(fig)


st.divider()
st.write("© 2025/26 — Yash Modi")

if st.button("Logout"):
    del st.session_state["user"]
    st.switch_page("pages/login.py")
