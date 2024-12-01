import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Load the data from the same folder as the script
csv_file = os.path.join(
    os.path.dirname(__file__), "../data/pk_exports_by_type_FY24_usd.csv"
)
data = pd.read_csv(csv_file)

st.markdown(
    """
     *Tip: Click on any **box** to explore deeper. Click it again to return.*
    """,
    unsafe_allow_html=True,
)

xxxx = []

# Ensure column names are consistent and handle whitespace
data.columns = data.columns.str.strip()

# Convert the 'value' column to numeric to avoid NaN issues
data["value"] = pd.to_numeric(data["value"], errors="coerce")

# st.header("Pakistan Exports Basket")

# Radio buttons for selecting type of export
export_type = st.radio(" ### Goods and Services:", ["Separated", "Combined"])

# Filter data based on selected export type
if export_type == "Separated":
    xxxx = ["Type", "Title_with_values"]
else:  # export_type == "Combined"
    xxxx = ["Title_with_values"]


# Calculate total value for percentage calculation
total_value = data["value"].sum()

# Add percentage and million USD columns
data["value2"] = data["value"] / 1e6
data["pct"] = (data["value"] / total_value) * 100

# Add a column for multi-line labels
data["Title_with_values"] = data.apply(
    lambda row: f"{row['Title']}<br>({row['value2']:.2f}B USD)", axis=1
)

# Define consistent colors using Pastel palette
unique_categories = data["Title"].unique()
pastel_colors = px.colors.qualitative.D3

# Map categories to colors
color_map = {
    category: pastel_colors[i % len(pastel_colors)]
    for i, category in enumerate(unique_categories)
}

# Visualization with Plotly Treemap
treemap_fig = px.treemap(
    data,
    path=xxxx,
    # path=["Type", "Title_with_values"],  # Multi-line labels
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
    data,
    values="value",
    names="Title_with_values",  # Multi-line labels
    color="Title",  # Use the same color mapping
    color_discrete_map=color_map,  # Ensure consistent colors
    title="Export Category Breakdown",
)

# Display Pie Chart
# st.plotly_chart(pie_fig, use_container_width=True)

# Sort data by value in descending order
sorted_data = data.sort_values(by="value", ascending=False)


# Generate the legend with matching colors in two columns
st.markdown("### Export Categories (Legend)")

# Create two columns for the legend
col1, col2 = st.columns(2)

# Populate the columns with aligned content
with col1:
    st.markdown(
        "<br>".join(
            [
                f'<span style="color:{color_map[row["Title"]]};">⬤</span> '
                f'**{row["Title"]}**'
                for _, row in sorted_data.iterrows()
            ]
        ),
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        "<br>".join(
            [
                f'{row["value2"]:.2f}B USD ({row["pct"]:.2f}%)'
                for _, row in sorted_data.iterrows()
            ]
        ),
        unsafe_allow_html=True,
    )
