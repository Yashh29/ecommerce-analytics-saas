import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from google.cloud import storage
from google.oauth2 import service_account
import io

# ---------------------------------------------------------
# Redirect if user not logged in
# ---------------------------------------------------------
if "user" not in st.session_state or st.session_state["user"] is None:
    st.switch_page("pages/login.py")


# ---------------------------------------------------------
# Firebase Storage Client (NOW USING st.secrets)
# ---------------------------------------------------------
@st.cache_resource
def get_storage_client():
    """Authenticate using Streamlit secrets instead of JSON file."""
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"]
    )
    return storage.Client(credentials=credentials)


BUCKET_NAME = "ecommerce-analytics-saas-f2a2f.appspot.com"


# ---------------------------------------------------------
# Check if file exists in Firebase Storage
# ---------------------------------------------------------
def user_file_exists(user_email, filename):
    try:
        client = get_storage_client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{user_email}/{filename}")
        return blob.exists()
    except Exception as e:
        st.error(f"Storage error: {e}")
        return False


# ---------------------------------------------------------
# Load user file from Firebase
# ---------------------------------------------------------
def load_user_file(user_email, filename):
    try:
        client = get_storage_client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"{user_email}/{filename}")

        if not blob.exists():
            return None

        data_bytes = blob.download_as_bytes()
        return pd.read_csv(io.BytesIO(data_bytes))

    except Exception as e:
        st.warning(f"File loading failed: {e}")
        return None


# ---------------------------------------------------------
# Local fallback loaders
# ---------------------------------------------------------
@st.cache_data
def load_local_dashboard_data():
    return pd.read_csv("core/data/processed/dashboard_data.csv")

@st.cache_data
def load_local_forecast_data():
    df = pd.read_csv("core/data/processed/segment_revenue_forecast.csv")
    df["order_month"] = pd.to_datetime(df["order_month"])
    return df


# ---------------------------------------------------------
# Final Data Loader (Firebase → Local fallback)
# ---------------------------------------------------------
def get_dashboard_data():
    email = st.session_state["user"]

    if user_file_exists(email, "dashboard_data.csv"):
        df = load_user_file(email, "dashboard_data.csv")
        if df is not None:
            st.success("Loaded your personal dashboard dataset from cloud 🚀")
            return df

    st.info("Using demo dashboard dataset.")
    return load_local_dashboard_data()


def get_forecast_data():
    email = st.session_state["user"]

    if user_file_exists(email, "segment_revenue_forecast.csv"):
        df = load_user_file(email, "segment_revenue_forecast.csv")
        if df is not None:
            df["order_month"] = pd.to_datetime(df["order_month"])
            st.success("Loaded your personalized forecast data 🚀")
            return df

    st.info("Using demo forecast dataset.")
    return load_local_forecast_data()


# ---------------------------------------------------------
# Sidebar: Process My Data
# ---------------------------------------------------------
st.sidebar.header("⚙️ SaaS Controls")

if st.sidebar.button("📤 Process My Uploaded Data"):
    st.session_state["run_processing"] = True
    st.success("Pipeline triggered! Upload your raw file in Upload page.")
else:
    st.session_state["run_processing"] = False


# ---------------------------------------------------------
# Load Data
# ---------------------------------------------------------
data = get_dashboard_data()
forecast_df = get_forecast_data()


# ---------------------------------------------------------
# Dashboard UI
# ---------------------------------------------------------
st.title("📊 Enterprise E-Commerce Analytics Platform")
st.markdown("**Audience:** Executives • Marketing • Strategy • Retention Teams**")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📌 Executive Overview",
    "🧩 Segments",
    "⚠️ Churn Risk",
    "🎯 Recommendations",
    "📈 Forecast"
])


# ---------------------------------------------------------
# TAB 1 — Executive Overview
# ---------------------------------------------------------
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Customers", data["customer_id"].nunique())
    col2.metric("Churn Rate (%)", f"{data['actual_churn'].mean()*100:.2f}")
    col3.metric("High-Risk (%)", f"{(data['risk_level']=='High Risk').mean()*100:.2f}")
    col4.metric("Avg CLV", f"{data['clv_proxy'].mean():.2f}")

    st.divider()

    st.subheader("Churn Risk Distribution")
    fig, ax = plt.subplots()
    data["risk_level"].value_counts().plot.pie(autopct="%1.1f%%", ax=ax)
    ax.set_ylabel("")
    st.pyplot(fig)

    st.subheader("CLV vs Churn Probability")
    fig, ax = plt.subplots()
    ax.scatter(data["clv_proxy"], data["churn_probability"], alpha=0.5)
    st.pyplot(fig)


# ---------------------------------------------------------
# TAB 2 — Segments
# ---------------------------------------------------------
with tab2:
    summary = data.groupby("segment").agg(
        customers=("customer_id", "count"),
        avg_clv=("clv_proxy", "mean"),
        churn_rate=("actual_churn", "mean"),
    ).reset_index()

    st.dataframe(summary, use_container_width=True)

    st.subheader("Customers per Segment")
    fig, ax = plt.subplots()
    summary.set_index("segment")["customers"].plot(kind="bar", ax=ax)
    st.pyplot(fig)

    st.subheader("Average CLV per Segment")
    fig, ax = plt.subplots()
    summary.set_index("segment")["avg_clv"].plot(kind="bar", ax=ax)
    st.pyplot(fig)


# ---------------------------------------------------------
# TAB 3 — Churn Risk
# ---------------------------------------------------------
with tab3:
    risk_filter = st.selectbox(
        "Select Risk Level", ["All", "High Risk", "Medium Risk", "Low Risk"]
    )
    df = data if risk_filter == "All" else data[data["risk_level"] == risk_filter]

    st.dataframe(df.sort_values("churn_probability", ascending=False))


# ---------------------------------------------------------
# TAB 4 — Recommendations
# ---------------------------------------------------------
with tab4:
    st.markdown("""
    ### Retention Strategy  
    - **High Risk + High CLV** → Manual retention  
    - **High Risk + Low CLV** → Automated campaigns  
    - **Medium Risk** → Engagement emails  
    - **Low Risk** → Normal nurturing  
    """)


# ---------------------------------------------------------
# TAB 5 — Forecast
# ---------------------------------------------------------
with tab5:
    segments = st.multiselect(
        "Select segments", forecast_df["segment"].unique(),
        default=forecast_df["segment"].unique()
    )

    fd = forecast_df[forecast_df["segment"].isin(segments)]

    fig, ax = plt.subplots(figsize=(12, 5))
    for seg in fd["segment"].unique():
        sd = fd[fd["segment"] == seg]
        ax.plot(sd["order_month"], sd["forecast"], marker="o", label=seg)
    ax.legend()
    st.pyplot(fig)


# ---------------------------------------------------------
# Footer + Logout
# ---------------------------------------------------------
st.divider()
st.write("© 2025/26 — Yash Modi")

if st.button("Logout"):
    del st.session_state["user"]
    st.switch_page("pages/login.py")
