import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# Load the CSV data
csv_file = "pakistan_exports.csv"
data = pd.read_csv(csv_file)

# Strip leading/trailing spaces from column names
data.columns = data.columns.str.strip()

# Convert 'Date' to datetime and ensure 'Exports' is numeric
data["Date"] = pd.to_datetime(data["Date"], format="%m/%d/%y")
data["Exports"] = data["Exports"].astype(float)

# Add Year column for yearly aggregation
data["Year"] = data["Date"].dt.year

# Streamlit App
st.title("Pakistan Exports")
st.markdown("Source: State Bank Data")
st.divider()

# Time range options using segmented control
time_range_option = st.segmented_control(
    "Time Range",
    ["All Data", "Last 5 Years", "Last 10 Years"],
    selection_mode="single",
    default="All Data",
)

# Handle deselection (if any) by ensuring a valid option
if not time_range_option:
    time_range_option = "All Data"

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

# Moving average options using segmented control
moving_avg_option = st.segmented_control(
    "Moving Average Window",
    ["None", "3 Months", "6 Months", "12 Months"],
    selection_mode="single",
    default="12 Months",
)

# Handle deselection (if any) by ensuring a valid option
if not moving_avg_option:
    moving_avg_option = "None"

if moving_avg_option != "None":
    window = int(
        moving_avg_option.split()[0]
    )  # Extract the window size from the option
    time_filtered_data["Moving_Avg"] = (
        time_filtered_data["Exports_Billions"]
        .rolling(window=window, min_periods=1)
        .mean()
    )

st.divider()

# Create the Altair chart with or without moving average
line = (
    alt.Chart(time_filtered_data)
    .mark_line(point=True)
    .encode(
        x="Date:T",
        y=alt.Y(
            "Exports_Billions:Q",
            axis=alt.Axis(title="Exports (in Billions USD)", format=".2f"),
        ),
        tooltip=["Date:T", alt.Tooltip("Exports_Billions:Q", format=".2f")],
    )
    .properties(width=800, height=400, title="Pakistan Exports Over Time")
)

if moving_avg_option != "None":
    moving_avg = (
        alt.Chart(time_filtered_data)
        .mark_line(color="red")
        .encode(x="Date:T", y=alt.Y("Moving_Avg:Q", title=""))
    )
    chart = line + moving_avg
else:
    chart = line

# Create the growth rate chart
growth_chart = (
    alt.Chart(yearly_data)
    .mark_bar(color="green")
    .encode(
        x=alt.X(
            "Year:Q", title="Year", axis=alt.Axis(format="d")
        ),  # Remove commas from Year
        y=alt.Y("Growth_Rate:Q", title="Yearly Growth Rate (%)"),
        tooltip=["Year:Q", alt.Tooltip("Growth_Rate:Q", format=".2f")],
    )
    .properties(width=800, height=300, title="Yearly Growth Rates")
)

# Display the chart
st.altair_chart(chart, use_container_width=True)

# Display the growth rate chart
st.altair_chart(growth_chart, use_container_width=True)
