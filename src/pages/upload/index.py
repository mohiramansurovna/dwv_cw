from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.data.functions.store import get_current_data
from src.data.functions.styles import apply_css
from src.data.ui import render_workspace_panel
from src.pages.upload.components.overview import render_overview
from src.pages.upload.components.sources import render_source_tabs


def render_upload_page() -> None:
    """Render the upload sources plus the overview page for the current dataset."""
    left, right = st.columns([3.2, 1.2])

    with left:
        st.markdown(
            """
            <section class="page-hero upload-hero">
                <p class="page-hero__eyebrow">Page A</p>
                <h1 class="page-hero__title">Upload &amp; Overview</h1>
                <p class="page-hero__subtitle">
                    Load a CSV, Excel, JSON file, a public Google Sheet, or one of the bundled sample datasets.
                </p>
            </section>
            """,
            unsafe_allow_html=True,
        )

        render_source_tabs()

        df = get_current_data()
        if df is not None:
            st.divider()
            render_overview(df)

    with right:
        render_workspace_panel()
