import streamlit as st # pyright: ignore[reportMissingImports]

from src.sidebars.navigation import render_navigation
from src.pages.export.index import render_export_page
from src.pages.prepare.index import render_prepare_page
from src.pages.upload.index import render_upload_page
from src.pages.visualize.ui import render_visualize_page


st.set_page_config(
    page_title="DWV CW ",
    layout="wide",
    initial_sidebar_state="expanded",
)
page = render_navigation()

if page == "upload":
    render_upload_page()
elif page == "prepare":
    render_prepare_page()
elif page == "visualize":
    render_visualize_page()
else:
    render_export_page()
