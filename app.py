import streamlit as st
import pandas as pd
import plotly.express as px

# Page Setup
st.set_page_config(
    page_title="Predictive Analysis of Seasonal Diseases",
    page_icon="🩺",
    layout="wide"
)

# 1. Load Dataset
@st.cache_data
def load_data():
    return pd.read_csv("seasonal_diseases_rural_urban_dataset_2024_2026.csv")

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# Header
st.title("🩺 Predictive Analysis of Seasonal Diseases in Rural & Urban Areas")
st.markdown("Analyze seasonal disease risks, regional trends, and predict risk levels based on environmental factors.")

# Sidebar Filters
st.sidebar.header("Filter Options")
selected_area = st.sidebar.multiselect("Select Area Type:", options=df["Area_Type"].unique(), default=df["Area_Type"].unique())
selected_season = st.sidebar.multiselect("Select Season:", options=df["Season"].unique(), default=df["Season"].unique())

filtered_df = df[(df["Area_Type"].isin(selected_area)) & (df["Season"].isin(selected_season))]

# Tabs Setup
tab1, tab2, tab3 = st.tabs(["📊 Analytics Dashboard", "🔮 Risk Predictor", "📁 Dataset Viewer"])

# TAB 1: ANALYTICS DASHBOARD
with tab1:
    st.subheader("Key Health Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Records", len(filtered_df))
    m2.metric("Total Reported Cases", int(filtered_df["Cases"].sum()))
    m3.metric("Avg Mosquito Index", f"{filtered_df['Mosquito_Index'].mean():.1f}")
    m4.metric("Avg Risk Score", f"{filtered_df['Risk_Score'].mean():.1f}")

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        fig_bar = px.bar(
            filtered_df,
            x="Disease",
            y="Cases",
            color="Area_Type",
            barmode="group",
            title="Reported Cases by Disease & Area Type"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        fig_box = px.box(
            filtered_df,
            x="Season",
            y="Risk_Score",
            color="Area_Type",
            title="Risk Score Spread Across Seasons"
        )
        st.plotly_chart(fig_box, use_container_width=True)

    fig_scatter = px.scatter(
        filtered_df,
        x="Temperature_C",
        y="Humidity_Percent",
        size="Cases",
        color="Disease_Risk",
        hover_data=["Disease", "Region", "Area_Type"],
        title="Impact of Climate Parameters (Temp vs Humidity) on Cases"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# TAB 2: PREDICTION ENGINE
with tab2:
    st.subheader("Predict Disease Risk Level")
    st.write("Adjust environmental indicators to compute the overall **Disease Risk Assessment**.")

    # Rule-Based Scoring Logic (Calculates dynamic weighted risk index without C-DLL dependencies)
    def calculate_predicted_risk(temp, rainfall, humidity, mosquito, water, sanitation, prev_cases):
        raw_score = (
            (mosquito * 0.35) + 
            (rainfall * 0.15) + 
            (prev_cases * 0.20) + 
            ((100 - water) * 0.15) + 
            ((100 - sanitation) * 0.15)
        )
        if raw_score >= 45:
            return "High", raw_score
        elif raw_score >= 25:
            return "Medium", raw_score
        else:
            return "Low", raw_score

    with st.form("risk_form"):
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            temp = st.slider("Temperature (°C)", int(df["Temperature_C"].min()), int(df["Temperature_C"].max()), 28)
            rainfall = st.slider("Rainfall (mm)", int(df["Rainfall_mm"].min()), int(df["Rainfall_mm"].max()), 100)
            humidity = st.slider("Humidity (%)", int(df["Humidity_Percent"].min()), int(df["Humidity_Percent"].max()), 65)

        with col_b:
            water = st.slider("Water Quality Index", int(df["Water_Quality_Index"].min()), int(df["Water_Quality_Index"].max()), 60)
            mosquito = st.slider("Mosquito Index", int(df["Mosquito_Index"].min()), int(df["Mosquito_Index"].max()), 40)
            prev_cases = st.number_input("Previous Month Cases", min_value=0, value=50)

        with col_c:
            pop_density = st.number_input("Population Density", min_value=100, value=2000)
            sanitation = st.slider("Sanitation Score", int(df["Sanitation_Score"].min()), int(df["Sanitation_Score"].max()), 60)

        btn_submit = st.form_submit_button("Calculate Risk Level")

    if btn_submit:
        risk_label, calculated_score = calculate_predicted_risk(
            temp, rainfall, humidity, mosquito, water, sanitation, prev_cases
        )

        st.markdown("### Risk Analysis Output")
        st.write(f"Calculated Composite Risk Metric: **{calculated_score:.1f}**")
        
        if risk_label == "High":
            st.error(f"🔴 Predicted Disease Risk: **HIGH RISK**")
            st.info("Recommendation: Deploy targeted vector control, inspect water sanitation, and increase regional medical supplies.")
        elif risk_label == "Medium":
            st.warning(f"🟡 Predicted Disease Risk: **MEDIUM RISK**")
            st.info("Recommendation: Monitor local cases closely and issue community awareness advisories.")
        else:
            st.success(f"🟢 Predicted Disease Risk: **LOW RISK**")
            st.info("Recommendation: Maintain standard monitoring protocols.")

# TAB 3: DATA TABLE
with tab3:
    st.subheader("Explore Raw Dataset")
    st.dataframe(filtered_df, use_container_width=True)