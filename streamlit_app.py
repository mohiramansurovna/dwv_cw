import streamlit as st

from src.data.ui import render_data_sidebar
from src.pages.export.ui import render_export_page
from src.pages.prepare.ui import render_prepare_page
from src.pages.upload.ui import render_upload_page
from src.pages.visualize.ui import render_visualize_page


st.set_page_config(
    page_title="Data Workflow Studio",
    layout="wide",
)

st.markdown(
    """
    <style>
        div[data-testid="stMetric"] {
            border: 1px solid #1d4ed8;
            border-radius: 14px;
            padding: 0.6rem;
            background: #1d4ed8;
            box-shadow: 0 10px 24px rgba(29, 78, 216, 0.18);
        }
        div[data-testid="stMetric"] label,
        div[data-testid="stMetric"] p,
        div[data-testid="stMetric"] [data-testid="stMetricLabel"],
        div[data-testid="stMetric"] [data-testid="stMetricValue"],
        div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
            color: white !important;
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        [data-testid="stSidebar"] [role="radiogroup"] {
            gap: 0.45rem;
            padding-top: 0.35rem;
        }
        [data-testid="stSidebar"] [role="radiogroup"] label {
            justify-content: center;
            min-height: 3rem;
            border-radius: 14px;
        }
        [data-testid="stSidebar"] [role="radiogroup"] p {
            font-size: 1.35rem;
            line-height: 1;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

page = render_data_sidebar()

if page == "upload":
    render_upload_page()
elif page == "prepare":
    render_prepare_page()
elif page == "visualize":
    render_visualize_page()
else:
    render_export_page()
