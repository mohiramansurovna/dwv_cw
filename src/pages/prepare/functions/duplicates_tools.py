from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data.functions.transforms import detect_duplicates, remove_duplicates
from src.pages.prepare.functions.actions import apply_and_rerun


def render_duplicates_tab(df: pd.DataFrame) -> None:
    """Render duplicate detection, preview, and removal controls."""
    duplicate_mode = st.radio(
        "Duplicate detection mode",
        options=["full_row", "subset"],
        horizontal=True,
        format_func=lambda item: "Full row" if item == "full_row" else "Subset of columns",
    )
    subset = None
    if duplicate_mode == "subset":
        subset = st.multiselect(
            "Subset columns",
            options=df.columns.tolist(),
            default=df.columns.tolist()[:2],
            key="duplicate-subset-cols",
        )

    duplicate_df = detect_duplicates(df, subset=subset if subset else None)
    st.metric("Duplicate rows detected", f"{duplicate_df.shape[0]:,}")
    if duplicate_df.empty:
        st.info("No duplicates found for the selected criteria.")
    else:
        st.dataframe(duplicate_df.head(100), use_container_width=True)

    keep = st.selectbox("When removing duplicates, keep", options=["first", "last"])
    if st.button(
        "Remove duplicates",
        key="remove-duplicates",
        disabled=duplicate_mode == "subset" and not subset,
    ):
        new_df = remove_duplicates(df, subset=subset if subset else None, keep=keep)
        apply_and_rerun(
            new_df,
            operation="Remove duplicates",
            parameters={"subset": subset, "keep": keep},
            affected_columns=subset or df.columns.tolist(),
            preview={"rows_removed": int(df.shape[0] - new_df.shape[0])},
        )
