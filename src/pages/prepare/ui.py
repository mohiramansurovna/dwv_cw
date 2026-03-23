from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.data.functions.store import get_current_data
from src.data.functions.styles import apply_css
from src.data.ui import render_workspace_panel
from src.pages.prepare.functions.categorical_tools import render_categorical_tab
from src.pages.prepare.functions.column_operations import render_columns_tab
from src.pages.prepare.functions.duplicates_tools import render_duplicates_tab
from src.pages.prepare.functions.missing_values import render_missing_values_tab
from src.pages.prepare.functions.numeric_tools import render_numeric_tab, render_scaling_tab
from src.pages.prepare.functions.type_tools import render_types_tab
from src.pages.prepare.functions.validation_tools import render_validation_tab


PREPARE_CSS_PATH = Path(__file__).with_name("prepare.css")


def render_prepare_page() -> None:
    """Render the full cleaning and preparation studio."""
    apply_css(PREPARE_CSS_PATH)
    left, right = st.columns([3.2, 1.2])
    df = get_current_data()

    with left:
        st.markdown(
            """
            <section class="page-hero prepare-hero">
                <p class="page-hero__eyebrow">Page B</p>
                <h1 class="page-hero__title">Cleaning &amp; Preparation Studio</h1>
                <p class="page-hero__subtitle">
                    Apply data-cleaning actions to the working copy and keep every successful transformation reproducible.
                </p>
            </section>
            """,
            unsafe_allow_html=True,
        )

        if df is None:
            st.info("Load a dataset on the Upload page to start cleaning.")
        else:
            st.caption("Apply transformations to the working copy. Each successful step is recorded and can be undone.")
            st.dataframe(df.head(20), use_container_width=True)

            tabs = st.tabs(
                [
                    "Missing Values",
                    "Duplicates",
                    "Types & Parsing",
                    "Categorical Tools",
                    "Numeric Cleaning",
                    "Scaling",
                    "Column Operations",
                    "Validation Rules",
                ]
            )

            with tabs[0]:
                render_missing_values_tab(df)
            with tabs[1]:
                render_duplicates_tab(df)
            with tabs[2]:
                render_types_tab(df)
            with tabs[3]:
                render_categorical_tab(df)
            with tabs[4]:
                render_numeric_tab(df)
            with tabs[5]:
                render_scaling_tab(df)
            with tabs[6]:
                render_columns_tab(df)
            with tabs[7]:
                render_validation_tab(df)

    with right:
        render_workspace_panel()
