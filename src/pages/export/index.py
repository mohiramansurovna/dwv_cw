from __future__ import annotations

import streamlit as st

from src.data.store import get_store
from src.sidebars.workspace import render_workspace
from src.pages.export.components.content import render_export_content


def render_export_page() -> None:
    left, right = st.columns([3.2, 1.2])
    store=get_store()

    with left:
        st.markdown(
            """
            <section>
                <h1>Export &amp; Report</h1>
                <p>
                    Download the cleaned dataset, the transformation report, and the reproducible JSON recipe.
                </p>
            </section>
            """,
            unsafe_allow_html=True,
        )

        if store['current_df'] is None:
            st.info("Load a dataset before exporting.")
        else:
            render_export_content(store['current_df'])

    with right:
        render_workspace()
