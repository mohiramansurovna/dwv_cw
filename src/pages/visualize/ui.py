from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.data.functions.store import get_current_data
from src.data.functions.styles import apply_css
from src.data.ui import render_workspace_panel
from src.pages.visualize.functions.builder import render_visualization_builder


VISUALIZE_CSS_PATH = Path(__file__).with_name("visualize.css")


def render_visualize_page() -> None:
    """Render the chart builder, filter controls, and saved chart definitions."""
    apply_css(VISUALIZE_CSS_PATH)
    left, right = st.columns([3.2, 1.2])
    df = get_current_data()

    with left:
        st.markdown(
            """
            <section class="page-hero visualize-hero">
                <p class="page-hero__eyebrow">Page C</p>
                <h1 class="page-hero__title">Visualization Builder</h1>
                <p class="page-hero__subtitle">
                    Build matplotlib charts from the cleaned working dataset and save chart definitions for export.
                </p>
            </section>
            """,
            unsafe_allow_html=True,
        )

        if df is None:
            st.info("Load and prepare a dataset before building charts.")
        else:
            render_visualization_builder(df)

    with right:
        render_workspace_panel()
