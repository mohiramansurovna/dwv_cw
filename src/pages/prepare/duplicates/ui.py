from __future__ import annotations

import streamlit as st # pyright: ignore[reportMissingImports]

from src.pages.prepare.duplicates.transformers import get_duplicate_rows, remove_duplicates
from src.data.store import commit_transformation


def render_duplicates_tab(df) -> None:
    st.subheader("Duplicates")

    mode = st.radio(
        "Duplicate detection mode",
        ["Full row", "Subset of columns"],
        horizontal=True,
    )

    subset: list[str] | None = None
    if mode == "Subset of columns":
        subset = st.multiselect("Key columns", df.columns.tolist())

    duplicates_df = get_duplicate_rows(df, subset=subset if subset else None)
    st.write(f"Duplicate rows found: {len(duplicates_df)}")
    st.dataframe(duplicates_df.head(100), use_container_width=True, hide_index=True)

    keep = st.selectbox("Keep", ["first", "last"])

    if st.button("Remove duplicates", use_container_width=True):
        new_df, preview = remove_duplicates(df, subset=subset if subset else None, keep=keep)
        commit_transformation(
            new_df,
            operation="Remove duplicates",
            parameters={"subset": subset or [], "keep": keep},
            affected_columns=subset or [],
            preview=preview,
        )
        st.success("Transformation applied.")
        st.rerun()