import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Load the CSV data
csv_file = os.path.join(os.path.dirname(__file__), "../data/pk_exports_by_country.csv")
data = pd.read_csv(csv_file)

# Strip leading/trailing spaces from column names
data.columns = data.columns.str.strip()

# Ensure 'Exports' column is numeric
data["Exports"] = pd.to_numeric(data["Exports"], errors="coerce")

# Calculate total exports for percentage calculation
total_exports = data["Exports"].sum()

# Add percentage and value in billions
data["Value_Billions"] = data["Exports"] / 1e9
data["Percentage"] = (data["Exports"] / total_exports) * 100

# Add a column for multi-line labels
data["Title_with_values"] = data.apply(
    lambda row: f"{row['country']}<br>({row['Value_Billions']:.2f}B USD)", axis=1
)

# Define a color palette
unique_countries = data["country"].unique()
color_palette = px.colors.qualitative.Set3

# Map countries to colors
color_map = {
    country: color_palette[i % len(color_palette)]
    for i, country in enumerate(unique_countries)
}

# Visualization with Plotly Treemap
treemap_fig = px.treemap(
    data,
    path=["Title_with_values"],  # Use multi-line labels
    values="Exports",  # Size of the rectangles
    labels={"Exports": "Exports (USD)", "Title_with_values": "Country"},
    color="country",  # Color by country
    color_discrete_map=color_map,  # Ensure consistent colors
    hover_data={"Value_Billions": ":.2f", "Percentage": ":.2f"},
)

# Update hovertemplate for Treemap
treemap_fig.update_traces(
    hovertemplate="<b>%{label}</b><br>Exports: %{value:,.0f} USD<br>Percentage: %{customdata[1]:.2f}%",
    customdata=data[["Value_Billions", "Percentage"]].values,
)

treemap_fig.update_layout(
    hovermode="x unified",
    title="Pakistan Exports by Country",
)

# Display Treemap
st.plotly_chart(treemap_fig, use_container_width=True)

# Add a message between the chart and the legend
st.markdown(
    "*(~150 more countries with small amounts totaling about 2 Billion USD)*",
    unsafe_allow_html=True,
)

# List Section (Similar to Legend)
st.markdown("### Export Breakdown by Country")

# Create a single-column list with name, percentage, and value
export_list = [
    f'<span style="color:{color_map[row["country"]]};">⬤</span> '
    f'**{row["country"]}**: {row["Value_Billions"]:.2f}B USD ({row["Percentage"]:.2f}%)'
    for _, row in data.sort_values(by="Exports", ascending=False).iterrows()
]

# Render the list
st.markdown("<br>".join(export_list), unsafe_allow_html=True)
