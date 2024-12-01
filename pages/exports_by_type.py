import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Load the data from the same folder as the script
# data = pd.read_csv("data/pk_exports_by_type_FY24_usd.csv")


csv_file = os.path.join(
    os.path.dirname(__file__), "../data/pk_exports_by_type_FY24_usd.csv"
)
data = pd.read_csv(csv_file)


# Ensure column names are consistent and handle whitespace
data.columns = data.columns.str.strip()

# Convert the 'value' column to numeric to avoid NaN issues
data["value"] = pd.to_numeric(data["value"], errors="coerce")

st.header("Pakistan Exports Basket")

# Dropdown for selecting type of export
export_type = st.selectbox(
    "Select Export Type", ["Goods + Services", "Goods", "Services"]
)

# Filter data based on selected export type
if export_type == "Goods + Services":
    filtered_data = data
else:
    filtered_data = data[data["Type"] == export_type]

# Calculate total value for percentage calculation
total_value = filtered_data["value"].sum()

# Add percentage and million USD columns
filtered_data["value2"] = filtered_data["value"] / 1e6
filtered_data["pct"] = (filtered_data["value"] / total_value) * 100

# Add a column for multi-line labels
filtered_data["Title_with_values"] = filtered_data.apply(
    lambda row: f"{row['Title']}<br>({row['value2']:.2f}B USD)", axis=1
)

# Define consistent colors using Pastel palette
unique_categories = filtered_data["Title"].unique()
pastel_colors = px.colors.qualitative.Pastel

# Map categories to colors
color_map = {
    category: pastel_colors[i % len(pastel_colors)]
    for i, category in enumerate(unique_categories)
}

# Visualization with Plotly Treemap
treemap_fig = px.treemap(
    filtered_data,
    path=["Type", "Title_with_values"],  # Multi-line labels
    values="value",  # Size of the rectangles
    labels={"value": "USD", "Title_with_values": ""},
    color="Title",  # Color by Title
    color_discrete_map=color_map,  # Ensure consistent colors
    hover_data={"value": "value"},  # Display value in hover
)

# Update hovertemplate for Treemap
treemap_fig.update_traces(hovertemplate=("<b>%{label}</b><br>" "%{value:,.0f} USD<br>"))

# Display Treemap
st.plotly_chart(treemap_fig, use_container_width=True)

# Add a Pie Chart with Consistent Colors
pie_fig = px.pie(
    filtered_data,
    values="value",
    names="Title_with_values",  # Multi-line labels
    color="Title",  # Use the same color mapping
    color_discrete_map=color_map,  # Ensure consistent colors
    title="Export Category Breakdown",
)

# Display Pie Chart
st.plotly_chart(pie_fig, use_container_width=True)
