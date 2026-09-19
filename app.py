import plotly.express as px
import streamlit as st

from data import DataLoadError, load_data, monthly_trend, total_orders, total_sales

st.set_page_config(page_title="ShopSmart Sales Dashboard", layout="wide")
st.title("ShopSmart Sales Dashboard")


@st.cache_data
def get_data(path):
    return load_data(path)


try:
    df = get_data("data/sales-data.csv")
except DataLoadError as e:
    st.error(str(e))
    st.stop()

col1, col2 = st.columns(2)
col1.metric("Total Sales", f"${total_sales(df):,.0f}")
col2.metric("Total Orders", f"{total_orders(df):,}")

st.subheader("Sales Trend Over Time")
trend = monthly_trend(df)
trend_fig = px.line(
    x=trend.index,
    y=trend.values,
    labels={"x": "Month", "y": "Sales ($)"},
    markers=True,
)
st.plotly_chart(trend_fig, use_container_width=True)
