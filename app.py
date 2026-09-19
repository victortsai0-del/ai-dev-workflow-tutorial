import streamlit as st

from data import DataLoadError, load_data

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
