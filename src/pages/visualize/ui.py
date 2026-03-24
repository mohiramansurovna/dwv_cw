from __future__ import annotations

import streamlit as st

from src.data.store import get_store
from src.pages.visualize.functions.builder import render_visualization_builder


def render_visualize_page() -> None:
    """Render the chart builder."""
    store = get_store()

    st.markdown(
        """
        <section>
            <h1>Visualization Builder</h1>
            <p>
                Visualize your data and save them as images to the report
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    if store["current_df"] is None:
        st.info("Load and prepare a dataset before building charts.")
        return

    render_visualization_builder(store["current_df"])