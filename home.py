import streamlit as st


st.set_page_config(
    page_title="Pakistan Exports Dashboard",  # Title of the app
    page_icon="🌍",  # Icon for the app
    layout="wide",  # Use the full screen width
    initial_sidebar_state="expanded",  # Open the sidebar by default
    menu_items={
        # "Get help": "https://example.com/help",  # Custom help link
        # "Report a bug": "https://example.com/bug",  # Bug reporting link
        "About": "-Farid   proj55.com",  # About section
    },
)


st.title("Pakistan Stats Dashboard")
st.write("Use the links in the sidebar to explore")
