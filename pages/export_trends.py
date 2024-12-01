import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# Load the CSV data
csv_file = os.path.join(os.path.dirname(__file__), "../data/pakistan_exports.csv")
data = pd.read_csv(csv_file)

# Strip leading/trailing spaces from column names
data.columns = data.columns.str.strip()

# Convert 'Date' to datetime and ensure 'Exports' is numeric
data["Date"] = pd.to_datetime(data["Date"], format="%m/%d/%y")
data["Exports"] = data["Exports"].astype(float)

# Add Year column for yearly aggregation
data["Year"] = data["Date"].dt.year

# Sidebar for Moving Average Settings
st.sidebar.title("Settings")

# Moving average options
moving_avg_option = st.sidebar.radio(
    "Moving Average Window",
    ["None", "3 Months", "6 Months", "12 Months"],
    index=3,  # Default selection
)

# Format exports to billions for display purposes
data["Exports_Billions"] = data["Exports"] / 1e9

# Apply moving average if selected
if moving_avg_option != "None":
    window = int(moving_avg_option.split()[0])  # Extract window size
    data["Moving_Avg"] = (
        data["Exports_Billions"].rolling(window=window, min_periods=1).mean()
    )

# Plotly Line Chart
fig_line = px.line(
    data,
    x="Date",
    y="Exports_Billions",
    title="Pakistan Monthly Exports Over Time",
    labels={"Exports_Billions": "Exports (Billions USD)", "Date": "Date"},
    hover_data={"Date": "|%Y-%m-%d", "Exports_Billions": ":.2f"},
)

if moving_avg_option != "None":
    fig_line.add_scatter(
        x=data["Date"],
        y=data["Moving_Avg"],
        mode="lines",  # Changed to solid line
        name=f"{window}-Month Moving Average",
        line=dict(color="orange"),
    )

fig_line.update_layout(
    xaxis_title=None,
    yaxis_title="Exports (Billions USD)",
    hovermode="x unified",
    legend=dict(
        orientation="h", yanchor="top", y=1.1, xanchor="center", x=0.5
    ),  # Legend on top
)

# Display Line Chart
st.plotly_chart(fig_line, use_container_width=True)

# Yearly Data and Growth Rate
yearly_data = data.groupby("Year")["Exports"].sum().reset_index()
yearly_data["Growth_Rate"] = yearly_data["Exports"].pct_change() * 100

# Plotly Bar Chart for Yearly Growth Rates
fig_bar = px.bar(
    yearly_data,
    x="Year",
    y="Growth_Rate",
    title="Yearly Growth Rates",
    labels={"Growth_Rate": "Yearly Growth Rate (%)", "Year": "Year"},
    color="Growth_Rate",
    color_continuous_scale=["red", "green"],
    hover_data={"Year": True, "Growth_Rate": ":.2f"},
)

fig_bar.update_traces(
    marker_line_width=1.5,
    marker_line_color="black",
)

fig_bar.update_layout(
    xaxis_title=None,
    yaxis_title="Growth Rate (%)",
    hovermode="x unified",
    showlegend=False,  # Hide legend
)

# Display Bar Chart
st.plotly_chart(fig_bar, use_container_width=True)
