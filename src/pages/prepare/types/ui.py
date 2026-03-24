from __future__ import annotations

import streamlit as st # pyright: ignore[reportMissingImports]

from src.pages.prepare.types.transformers import (
    clean_dirty_numeric_column,
    convert_column_type,
    parse_datetime_column,
)
from src.data.store import commit_transformation


def render_types_tab(df) -> None:
    st.subheader("Data Types & Parsing")

    action = st.selectbox(
        "Action",
        [
            "Convert column type",
            "Parse datetime",
            "Clean dirty numeric strings",
        ],
    )

    column = st.selectbox("Column", df.columns.tolist())

    if action == "Convert column type":
        target_type = st.selectbox("Target type", ["numeric", "categorical", "datetime", "string"])
        if st.button("Apply type conversion", use_container_width=True):
            new_df, preview = convert_column_type(df, column, target_type)
            commit_transformation(
                new_df,
                operation="Convert column type",
                parameters={"column": column, "target_type": target_type},
                affected_columns=[column],
                preview=preview,
            )
            st.success("Transformation applied.")
            st.rerun()

    elif action == "Parse datetime":
        date_format = st.text_input("Date format", placeholder="%Y-%m-%d")
        if st.button("Apply datetime parse", use_container_width=True):
            new_df, preview = parse_datetime_column(df, column, date_format or None)
            commit_transformation(
                new_df,
                operation="Parse datetime column",
                parameters={"column": column, "format": date_format or "auto"},
                affected_columns=[column],
                preview=preview,
            )
            st.success("Transformation applied.")
            st.rerun()

    elif action == "Clean dirty numeric strings":
        if st.button("Apply numeric cleanup", use_container_width=True):
            new_df, preview = clean_dirty_numeric_column(df, column)
            commit_transformation(
                new_df,
                operation="Clean dirty numeric strings",
                parameters={"column": column},
                affected_columns=[column],
                preview=preview,
            )
            st.success("Transformation applied.")
            st.rerun()