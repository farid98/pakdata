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

# Define a color palette
unique_countries = data["country"].unique()
color_palette = px.colors.qualitative.Set3

# Map countries to colors
color_map = {
    country: color_palette[i % len(color_palette)]
    for i, country in enumerate(unique_countries)
}

# Visualization with Plotly Bar Chart
bar_fig = px.bar(
    data.sort_values(by="Exports", ascending=False),  # Sort by exports
    x="country",
    y="Value_Billions",
    title="Pakistan Exports by Country",
    labels={"Value_Billions": "Exports (Billions USD)", "country": "Country"},
    color="country",
    color_discrete_map=color_map,
    hover_data={"Value_Billions": ":.2f", "Percentage": ":.2f"},
)

# Update hovertemplate for Bar Chart
bar_fig.update_traces(
    hovertemplate="<b>%{x}</b><br>Exports: %{y:.2f}B USD<br>Percentage: %{customdata[1]:.2f}%",
    customdata=data[["Value_Billions", "Percentage"]].values,
)

bar_fig.update_layout(
    xaxis_title=None,
    yaxis_title="Exports (Billions USD)",
    hovermode="x unified",
    showlegend=False,  # Hide legend
)

# Display Bar Chart
st.plotly_chart(bar_fig, use_container_width=True)

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
