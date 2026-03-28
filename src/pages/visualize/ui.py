from __future__ import annotations

from src.sidebars.workspace import render_workspace
import streamlit as st

from src.data.store import get_store
from src.pages.visualize.functions.builder import render_visualization_builder


def render_visualize_page() -> None:
    store = get_store()
    left, right = st.columns([3.2, 1.2])
    with left:

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
    with right:
        render_workspace()