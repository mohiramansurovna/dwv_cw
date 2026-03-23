from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.data.functions.store import get_current_data
from src.data.functions.styles import apply_css
from src.data.ui import render_workspace_panel
from src.pages.export.functions.content import render_export_content


EXPORT_CSS_PATH = Path(__file__).with_name("export.css")


def render_export_page() -> None:
    """Render export downloads plus the final dataset/report preview."""
    apply_css(EXPORT_CSS_PATH)
    left, right = st.columns([3.2, 1.2])
    df = get_current_data()

    with left:
        st.markdown(
            """
            <section class="page-hero export-hero">
                <p class="page-hero__eyebrow">Page D</p>
                <h1 class="page-hero__title">Export &amp; Report</h1>
                <p class="page-hero__subtitle">
                    Download the cleaned dataset, the transformation report, and the reproducible JSON recipe.
                </p>
            </section>
            """,
            unsafe_allow_html=True,
        )

        if df is None:
            st.info("Load a dataset before exporting.")
        else:
            render_export_content(df)

    with right:
        render_workspace_panel()
