import streamlit as st

from src.navigation.ui import render_navigation_sidebar
from src.pages.export.ui import render_export_page
from src.pages.prepare.ui import render_prepare_page
from src.pages.upload.index import render_upload_page
from src.pages.visualize.ui import render_visualize_page


st.set_page_config(
    page_title="Your App",
    layout="wide",
    initial_sidebar_state="expanded",
)
page = render_navigation_sidebar()

if page == "upload":
    render_upload_page()
elif page == "prepare":
    render_prepare_page()
elif page == "visualize":
    render_visualize_page()
else:
    render_export_page()
