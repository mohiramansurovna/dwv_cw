from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data.functions.transforms import convert_column_type
from src.pages.prepare.functions.actions import apply_and_rerun


def render_types_tab(df: pd.DataFrame) -> None:
    """Render per-column type conversion and parsing controls."""
    selected_column = st.selectbox("Column", options=df.columns.tolist(), key="types-column")
    target_type = st.selectbox(
        "Target type",
        options=["numeric", "categorical", "datetime"],
        key="types-target",
    )
    datetime_format = ""
    if target_type == "datetime":
        datetime_format = st.text_input("Datetime format (optional)", placeholder="%Y-%m-%d")

    before_nulls = int(df[selected_column].isna().sum())
    st.caption(f"Current dtype: `{df[selected_column].dtype}` | Nulls before conversion: {before_nulls}")

    if st.button("Convert column type", key="convert-type"):
        try:
            new_df = convert_column_type(
                df,
                column=selected_column,
                target_type=target_type,
                datetime_format=datetime_format.strip() or None,
            )
            after_nulls = int(new_df[selected_column].isna().sum())
            apply_and_rerun(
                new_df,
                operation="Convert column type",
                parameters={"column": selected_column, "target_type": target_type, "datetime_format": datetime_format},
                affected_columns=[selected_column],
                preview={"nulls_before": before_nulls, "nulls_after": after_nulls},
            )
        except Exception as exc:
            st.error(f"Conversion failed: {exc}")
