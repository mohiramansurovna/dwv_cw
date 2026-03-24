from __future__ import annotations
import streamlit as st

from src.data.store import get_store
from src.sidebars.workspace import render_workspace
from src.pages.upload.components.overview import render_overview
from src.pages.upload.components.sources import render_source_tabs


def render_upload_page() -> None:
    left, right = st.columns([3.2, 1.2])

    with left:
        st.markdown(
            """
            <section>
                <h1>Upload &amp; Overview</h1>
                <p>
                    Load a CSV, Excel, JSON file or one of the sample datasets.
                </p>
            </section>
            """,
            unsafe_allow_html=True,
        )

        render_source_tabs()

        store = get_store()
        if store['current_df'] is not None:
            st.divider()
            render_overview(store['current_df'])

    with right:
        render_workspace()
