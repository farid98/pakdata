import streamlit as st

st.set_page_config(
    page_title="Pakistan Exports Dashboard",  # Title of the app
    page_icon="🌍",  # Icon for the app
    layout="wide",  # Use the full screen width
    initial_sidebar_state="expanded",  # Open the sidebar by default
    menu_items={
        "About": "-Farid   proj55.com",  # About section
    },
)

# Add multiple lines of markdown at the end
st.markdown(
    """
    ### Pakistan  Dashboard
    Pakistan exports approximately **38 Billion USD** worth of goods and services annually. But what are details?

    - **What are the key export categories?**
    - **Which countries are the main trading partners?**
    - **How have exports trended monthly and yearly?**

    *Use the sidebar to explore detailed insights into Pakistan's trade performance.*

    *Data Source:* [State Bank of Pakistan](https://www.sbp.org.pk) 

    ---
    """,
    unsafe_allow_html=True,
)
