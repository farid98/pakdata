import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import os

# Add CSS for better layout adjustment
st.markdown(
    """
    <style>
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 5rem;
            padding-bottom: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load the CSV data
# csv_file = "data/pakistan_exports.csv"

csv_file = os.path.join(os.path.dirname(__file__), "../data/pakistan_exports.csv")
data = pd.read_csv(csv_file)

data = pd.read_csv(csv_file)

# Strip leading/trailing spaces from column names
data.columns = data.columns.str.strip()

# Convert 'Date' to datetime and ensure 'Exports' is numeric
data["Date"] = pd.to_datetime(data["Date"], format="%m/%d/%y")
data["Exports"] = data["Exports"].astype(float)

# Add Year column for yearly aggregation
data["Year"] = data["Date"].dt.year

# Sidebar for Settings
st.sidebar.title("Settings")

# Time range options
time_range_option = st.sidebar.radio(
    "Time Range",
    ["All Data", "Last 5 Years", "Last 10 Years"],
    index=0,  # Default selection
)

# Moving average options
moving_avg_option = st.sidebar.radio(
    "Moving Average Window",
    ["None", "3 Months", "6 Months", "12 Months"],
    index=3,  # Default selection
)

# Filter data based on the selected time range
if time_range_option == "All Data":
    time_filtered_data = data
elif time_range_option == "Last 5 Years":
    cutoff_date = datetime.now() - timedelta(days=5 * 365)
    time_filtered_data = data[data["Date"] >= cutoff_date]
elif time_range_option == "Last 10 Years":
    cutoff_date = datetime.now() - timedelta(days=10 * 365)
    time_filtered_data = data[data["Date"] >= cutoff_date]

# Format exports to billions for display purposes
time_filtered_data["Exports_Billions"] = time_filtered_data["Exports"] / 1e9

# Calculate yearly growth rates (exclude incomplete 2024 data for yearly calculations)
complete_years_data = data[data["Year"] < 2024]
yearly_data = complete_years_data.groupby("Year")["Exports"].sum().reset_index()
yearly_data["Growth_Rate"] = yearly_data["Exports"].pct_change() * 100

# Apply moving average if selected
if moving_avg_option != "None":
    window = int(moving_avg_option.split()[0])  # Extract window size
    time_filtered_data["Moving_Avg"] = (
        time_filtered_data["Exports_Billions"]
        .rolling(window=window, min_periods=1)
        .mean()
    )

# Create the Altair chart with or without moving average
line = (
    alt.Chart(time_filtered_data)
    .mark_line(color="green")
    .encode(
        x=alt.X("Date:T", axis=alt.Axis(title=None)),  # Remove x-axis title
        y=alt.Y(
            "Exports_Billions:Q",
            axis=alt.Axis(title="Monthly Exports (Billions USD)", format=".2f"),
        ),
        tooltip=["Date:T", alt.Tooltip("Exports_Billions:Q", format=".2f")],
    )
    .properties(width=800, height=400, title="Pakistan Monthly Exports Over Time")
)

if moving_avg_option != "None":
    moving_avg = (
        alt.Chart(time_filtered_data)
        .mark_line(color="orange")
        .encode(x="Date:T", y=alt.Y("Moving_Avg:Q", title=""))
    )
    chart = line + moving_avg
else:
    chart = line

# Filter yearly data based on the time range selector
filtered_yearly_data = yearly_data[
    yearly_data["Year"] >= time_filtered_data["Year"].min()
]

growth_chart = (
    alt.Chart(filtered_yearly_data)
    .mark_bar()
    .encode(
        x=alt.X("Year:O", axis=alt.Axis(title=None, labelAngle=0)),
        y=alt.Y("Growth_Rate:Q", title="Yearly Growth Rate (%)"),
        color=alt.condition(
            "datum.Growth_Rate >= 0", alt.value("green"), alt.value("red")
        ),
        tooltip=["Year:O", alt.Tooltip("Growth_Rate:Q", format=".2f")],
    )
    .properties(title="Yearly Growth Rates", width=800, height=300)
)

# Display the charts
st.altair_chart(chart, use_container_width=True)
st.altair_chart(growth_chart, use_container_width=True)
