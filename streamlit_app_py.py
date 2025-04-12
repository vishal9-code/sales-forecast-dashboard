# -*- coding: utf-8 -*-
"""streamlit_app.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1xauanPiPhALKGyrq7Q_LBzpeRuuOJLpp
"""



import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from datetime import datetime, timedelta
import altair as alt



from fpdf import FPDF

from prophet import Prophet

# Set page config
st.set_page_config(page_title="Sales Analytics & Forecasting Dashboard", layout="wide")
st.title("📈 Sales Analytics & Forecasting Dashboard")

# ---- Dummy Data Generation ----
@st.cache_data
def generate_dummy_data():
    np.random.seed(42)
    dates = pd.date_range(start="2023-01-01", end="2024-12-31", freq='D')
    products = ['Product A', 'Product B', 'Product C']
    regions = ['North', 'South', 'East', 'West']

    data = []
    for date in dates:
        for product in products:
            for region in regions:
                sales = np.random.poisson(lam=20)
                revenue = sales * np.random.uniform(10, 50)
                risk_flag = 1 if np.random.rand() < 0.05 else 0
                data.append([date, product, region, sales, revenue, risk_flag])

    df = pd.DataFrame(data, columns=['Date', 'Product', 'Region', 'Units Sold', 'Revenue', 'Risk Flag'])
    return df

sales_df = generate_dummy_data()

# ---- Sidebar Filters ----
st.sidebar.header("🔍 Filter Data")
selected_products = st.sidebar.multiselect("Select Product(s)", sales_df['Product'].unique(), default=sales_df['Product'].unique())
selected_regions = st.sidebar.multiselect("Select Region(s)", sales_df['Region'].unique(), default=sales_df['Region'].unique())
selected_date = st.sidebar.date_input("Select Date Range", [sales_df['Date'].min(), sales_df['Date'].max()])

filtered_df = sales_df[
    (sales_df['Product'].isin(selected_products)) &
    (sales_df['Region'].isin(selected_regions)) &
    (sales_df['Date'] >= pd.to_datetime(selected_date[0])) &
    (sales_df['Date'] <= pd.to_datetime(selected_date[1]))
]

# ---- KPIs ----
total_revenue = filtered_df['Revenue'].sum()
total_units = filtered_df['Units Sold'].sum()
avg_daily_sales = filtered_df.groupby('Date')['Units Sold'].sum().mean()
risk_alerts = filtered_df['Risk Flag'].sum()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("💰 Total Revenue", f"${total_revenue:,.0f}")
kpi2.metric("📦 Total Units Sold", f"{total_units:,}")
kpi3.metric("📊 Avg Daily Sales", f"{avg_daily_sales:.2f}")
kpi4.metric("🚨 Risk Alerts", f"{risk_alerts}")

# ---- Charts ----
st.subheader("📊 Sales Over Time")
sales_over_time = filtered_df.groupby('Date')[['Units Sold', 'Revenue']].sum().reset_index()
fig1 = plt.figure(figsize=(12, 4))
plt.plot(sales_over_time['Date'], sales_over_time['Revenue'], label='Revenue', color='green')
plt.title("Revenue Over Time")
plt.xlabel("Date")
plt.ylabel("Revenue")
plt.grid(True)
st.pyplot(fig1)

# ---- Risk Heatmap ----
st.subheader("🔥 Risk Heatmap by Region")
risk_map = filtered_df.groupby(['Region', 'Date'])['Risk Flag'].sum().unstack().fillna(0)
fig2, ax = plt.subplots(figsize=(12, 3))
sns.heatmap(risk_map, cmap="Reds", cbar=True, ax=ax)
plt.title("Risk Alerts Over Time by Region")
st.pyplot(fig2)

# ---- Table & Download ----
st.subheader("📋 Filtered Sales Table")
st.dataframe(filtered_df, use_container_width=True)

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(filtered_df)
st.download_button("⬇️ Download Filtered Data", data=csv, file_name='filtered_sales.csv', mime='text/csv')

# ---- AI Help Box Simulation ----
st.subheader("🧐 AI Help Box")
with st.expander("Need help? Ask the AI Assistant"):
    user_query = st.text_input("Ask your question:", "How can I detect a sales drop?")
    if user_query:
        if "drop" in user_query.lower():
            st.info("You can detect a sales drop by analyzing trends in the revenue over time chart or using rolling averages to highlight sudden changes.")
        elif "forecast" in user_query.lower():
            st.info("Forecasts are generated using time series models like Prophet. Check the forecast section for insights.")
        elif "download" in user_query.lower():
            st.info("You can download the filtered sales data using the 'Download Filtered Data' button below the sales table.")
        elif "risk" in user_query.lower():
            st.info("Risk alerts indicate potential problems in sales performance. Check the heatmap and the warning section for details.")
        else:
            st.info("This is a demo help box. In the future, this can be connected to an AI backend for real-time assistance.")
    st.markdown("**Common Questions:**")
    st.markdown("- How do I forecast sales?")
    st.markdown("- What does the risk alert mean?")
    st.markdown("- How do I export data?")

# ---- Forecasting Module ----
st.subheader("🔮 Sales Forecasting")

forecast_data = filtered_df.groupby('Date')['Revenue'].sum().reset_index()
forecast_data = forecast_data.rename(columns={'Date': 'ds', 'y': 'Revenue'})
forecast_data = forecast_data.rename(columns={'Revenue': 'y'})

if len(forecast_data) > 30:
    model = Prophet()
    model.fit(forecast_data)

    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    st.write("Forecast for the next 30 days:")
    fig3 = model.plot(forecast)
    st.pyplot(fig3)

    st.write("Forecast components:")
    fig4 = model.plot_components(forecast)
    st.pyplot(fig4)
else:
    st.warning("Not enough data to generate forecast. Please adjust your filters to include more data.")

# ---- Risk Warning System ----
st.subheader("⚠️ Risk Warning System")

latest_data = filtered_df[filtered_df['Date'] == filtered_df['Date'].max()]
regions_with_risk = latest_data[latest_data['Risk Flag'] == 1]['Region'].unique()

if len(regions_with_risk) > 0:
    st.error(f"⚠️ Risk Alert: Issues detected in regions: {', '.join(regions_with_risk)}")
else:
    st.success("✅ No risk alerts in the most recent data.")

# ---- Performance Insight Generator ----
st.subheader("📌 Sales Performance Insights")

cutoff = filtered_df['Date'].max() - pd.Timedelta(days=30)
last_month = filtered_df[filtered_df['Date'] > cutoff]
prev_month = filtered_df[(filtered_df['Date'] <= cutoff) & (filtered_df['Date'] > cutoff - pd.Timedelta(days=30))]

insight_text = ""
deltas = []

for region in filtered_df['Region'].unique():
    last_revenue = last_month[last_month['Region'] == region]['Revenue'].sum()
    prev_revenue = prev_month[prev_month['Region'] == region]['Revenue'].sum()
    if prev_revenue > 0:
        change = (last_revenue - prev_revenue) / prev_revenue * 100
        deltas.append({"region": region, "change": change})
        if change < -20:
            insight_text += f"⚠️ Sales in the {region} region dropped {abs(change):.1f}% compared to the previous month.\n"
        elif change > 20:
            insight_text += f"✅ Sales in the {region} region increased {change:.1f}% compared to the previous month.\n"

if insight_text:
    st.info(insight_text)
else:
    st.success("Sales performance is stable across all regions.")

# ---- Visual Trend Delta Bar ----
st.subheader("📉 Regional Sales Change Comparison")
delta_df = pd.DataFrame(deltas)
if not delta_df.empty:
    bar = alt.Chart(delta_df).mark_bar().encode(
        x=alt.X('region:N', title='Region'),
        y=alt.Y('change:Q', title='% Change in Revenue'),
        color=alt.condition(alt.datum.change > 0, alt.value("green"), alt.value("red"))
    ).properties(title="30-Day Revenue Change by Region")
    st.altair_chart(bar, use_container_width=True)

st.title("📊 Sales Forecast Dashboard with File Upload")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

# Load data
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success("File uploaded successfully!")
        st.write("📄 **Preview of Uploaded Data**")
        st.dataframe(df.head())

        # Continue with your dashboard logic here using `df`
        # For example: plotting, forecasting, etc.

    except Exception as e:
        st.error(f"Something went wrong: {e}")
else:
    st.warning("Please upload a file to continue.")
