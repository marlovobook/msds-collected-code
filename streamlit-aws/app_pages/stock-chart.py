import boto3
import streamlit as st
import pandas as pd
import awswrangler as wr
import re
import os

import streamlit.components.v1 as components

# st.title('Econ Upload Page')
# st.markdown('---')


import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import create_engine

# Set up Streamlit page
#st.set_page_config(page_title="NVDA Stock Dashboard", layout="wide")
st.title("📈 NVDA Stock Data Viewer")

# Database connection
engine = create_engine(
    'postgresql+psycopg2://postgres:postgres@database-dataeng.cgnlmpjizzzm.us-east-1.rds.amazonaws.com:5432/project'
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_sql("SELECT * FROM nvda_stock_data", con=engine)
    df['date'] = pd.to_datetime(df['date'])
    return df.sort_values("date")

df = load_data()

# Sidebar filters
st.sidebar.header("📊 Plot Options")
plot_type = st.sidebar.selectbox("Select chart type", ["Line Chart", "Candlestick"])
indicators = st.sidebar.multiselect(
    "Overlay indicators",
    options=["rsi", "sma", "ema", "macd", "atr"],
    default=["sma", "ema"]
)

# Filter date range
date_range = st.sidebar.date_input("Select date range", [df['date'].min(), df['date'].max()])
filtered_df = df[(df['date'] >= pd.to_datetime(date_range[0])) & (df['date'] <= pd.to_datetime(date_range[1]))]

# Plotting
fig = go.Figure()

if plot_type == "Line Chart":
    fig.add_trace(go.Scatter(x=filtered_df['date'], y=filtered_df['close'], mode='lines', name='Close'))
else:
    fig.add_trace(go.Candlestick(
        x=filtered_df['date'],
        open=filtered_df['open'],
        high=filtered_df['high'],
        low=filtered_df['low'],
        close=filtered_df['close'],
        name='Candlestick'
    ))

# Add indicators
color_map = {
    "sma": "orange", "ema": "blue", "rsi": "green", "macd": "purple", "atr": "red"
}
for indicator in indicators:
    if indicator in filtered_df.columns:
        fig.add_trace(go.Scatter(
            x=filtered_df['date'],
            y=filtered_df[indicator],
            mode='lines',
            name=indicator.upper(),
            line=dict(color=color_map.get(indicator, 'gray'), dash='dot')
        ))

fig.update_layout(title="NVDA Stock Price & Indicators", xaxis_title="Date", yaxis_title="Price")

st.plotly_chart(fig, use_container_width=True)

# Show data table
if st.checkbox("Show raw data"):
    st.dataframe(filtered_df)
