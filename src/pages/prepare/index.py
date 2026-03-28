from __future__ import annotations

from src.sidebars.workspace import render_workspace
import streamlit as st # pyright: ignore[reportMissingImports]

from src.data.profile import profile_dataframe
from src.data.store import get_store
from src.pages.prepare.duplicates.ui import render_duplicates_tab
from src.pages.prepare.missingness.ui import render_missingness_tab
from src.pages.prepare.types.ui import render_types_tab


# def _render_history_buttons() -> None:
#     store = get_store()

#     has_data = store["current_df"] is not None
#     has_history = len(store["transform_log"]) > 0

#     col1, col2, col3 = st.columns(3)

#     with col1:
#         if st.button("Undo last step", use_container_width=True, disabled=not has_history):
#             if undo_last_step():
#                 st.success("Last transformation removed.")
#                 st.rerun()

#     with col2:
#         if st.button("Reset to original dataset", use_container_width=True, disabled=not has_data):
#             if reset_all():
#                 st.success("Working copy reset.")
#                 st.rerun()

#     with col3:
#         if st.button("Reset session", use_container_width=True):
#             clear_session()
#             st.success("Session cleared.")
#             st.rerun()


def render_prepare_page() -> None:
    store = get_store()
    df = store["current_df"]
    left, right = st.columns([3.2, 1.2])
    with left:


        st.markdown(
            """
            <section>
                <h1>Prepare Data</h1>
                <p>Clean and transform your dataset before visualization and export.</p>
            </section>
            """,
            unsafe_allow_html=True,
        )

        if df is None:
            st.info("Load a dataset first.")
            return

        profile = profile_dataframe(df)

        rows_count = len(df)
        columns_count = len(df.columns)
        missing_cells_count = int(df.isna().sum().sum())
        duplicates_count = int(profile["duplicates_count"])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Rows", rows_count)
        col2.metric("Columns", columns_count)
        col3.metric("Missing Cells", missing_cells_count)
        col4.metric("Duplicate Rows", duplicates_count)

        with st.expander("Dataset overview", expanded=False):
            st.dataframe(profile["dtypes"], use_container_width=True, hide_index=True)


        tab1, tab2, tab3 = st.tabs(
            [
                "Missing Values",
                "Duplicates",
                "Types & Parsing",
            ]
        )

        with tab1:
            render_missingness_tab(df)

        with tab2:
            render_duplicates_tab(df)

        with tab3:
            render_types_tab(df)
    with right:
        render_workspace()