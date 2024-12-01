import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta


# Add this at the beginning of your script
st.markdown(
    """
    <style>
        /* Remove side margins and padding for all devices */
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 2rem;
            padding-bottom: 1rem;
        }
        
        /* Adjust width for mobile screens */
        @media (max-width: 768px) {
            .block-container {
                padding-left: 0.5rem;
                padding-right: 0.5rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


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
# st.title("Pakistan Exports")
# with st.popover("Settings"):


with st.expander("Settings", expanded=False):

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

    # Moving average options using segmented control
    moving_avg_option = st.segmented_control(
        "Moving Average Window",
        ["None", "3 Months", "6 Months", "12 Months"],
        selection_mode="single",
        default="12 Months",
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


# Create the Altair chart with or without moving average
line = (
    alt.Chart(time_filtered_data)
    .mark_line(color="green")
    .encode(
        x=alt.X("Date:T", axis=alt.Axis(title=None)),  # Remove x-axis title
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
    .mark_bar()  # Adjust bar width with `size`
    .encode(
        x=alt.X(
            "Year:O",  # Use `O` for ordinal scale, ensures bars are closer
            axis=alt.Axis(title=None, labelAngle=0),
        ),
        y=alt.Y("Growth_Rate:Q", title="Yearly Growth Rate (%)"),
        color=alt.condition(
            "datum.Growth_Rate >= 0",  # Conditional logic
            alt.value("green"),  # Positive growth is green
            alt.value("red"),  # Negative growth is red
        ),
        tooltip=["Year:O", alt.Tooltip("Growth_Rate:Q", format=".2f")],
    )
    .properties(title="Yearly Growth Rates", width=800, height=300)
)

annotations = filtered_yearly_data[
    filtered_yearly_data["Year"].isin([2009, 2020, 2021])
].copy()
annotations["Label"] = annotations["Year"].map(
    {2009: "Political Unrest", 2020: "Covid", 2021: "Covid Rebound"}
)

# Drop rows with missing Growth_Rate values (e.g., years not in the filtered dataset)
annotations = annotations.dropna(subset=["Growth_Rate"])

annotation_2009 = (
    alt.Chart(annotations[annotations["Year"] == 2009])
    .mark_text(
        align="left",
        dx=-5,  # Horizontal offset for 2009
        dy=10,  # Vertical offset for 2009
        fontSize=12,
        # fontWeight="bold",
        color="blue",
    )
    .encode(
        x="Year:O",
        y="Growth_Rate:Q",
        text="Label",
    )
)

annotation_2021 = (
    alt.Chart(annotations[annotations["Year"] == 2021])
    .mark_text(
        align="left",
        dx=-5,  # Horizontal offset for 2021
        dy=-15,  # Vertical offset for 2021
        fontSize=12,
        # fontWeight="bold",
        color="blue",
    )
    .encode(
        x="Year:O",
        y="Growth_Rate:Q",
        text="Label",
    )
)


annotation_2020 = (
    alt.Chart(annotations[annotations["Year"] == 2020])
    .mark_text(
        align="left",
        dx=-5,  # Horizontal offset for 2021
        dy=10,  # Vertical offset for 2021
        fontSize=12,
        # fontWeight="bold",
        color="blue",
    )
    .encode(
        x="Year:O",
        y="Growth_Rate:Q",
        text="Label",
    )
)


# Combine both annotation charts
annotation_chart = annotation_2009 + annotation_2020 + annotation_2021


# Combine growth chart and annotations
annotated_growth_chart = growth_chart + annotation_chart

# Display the chart
st.altair_chart(chart, use_container_width=True)

# Display the growth rate chart with annotations
st.altair_chart(annotated_growth_chart, use_container_width=True)
