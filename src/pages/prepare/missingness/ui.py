from __future__ import annotations

import streamlit as st # pyright: ignore[reportMissingImports]

from src.pages.prepare.missingness.transformers import (
    drop_columns_by_missing_threshold,
    drop_rows_with_missing,
    fill_missing_with_constant,
    fill_missing_with_direction,
    fill_missing_with_statistic,
    get_missing_summary,
)
from src.data.store import commit_transformation


def render_missingness_tab(df) -> None:
    st.subheader("Missing Values")

    summary = get_missing_summary(df)
    st.dataframe(summary, use_container_width=True, hide_index=True)

    action = st.selectbox(
        "Action",
        [
            "Drop rows with missing values",
            "Drop columns above missing threshold",
            "Fill with constant",
            "Fill with statistic",
            "Forward/backward fill",
        ],
    )

    columns = df.columns.tolist()

    if action == "Drop rows with missing values":
        selected_columns = st.multiselect("Columns", columns)
        if st.button("Apply missing-row drop", use_container_width=True):
            if not selected_columns:
                st.warning("Select at least one column.")
                return
            new_df, preview = drop_rows_with_missing(df, selected_columns)
            commit_transformation(
                new_df,
                operation="Drop rows with missing values",
                parameters={"columns": selected_columns},
                affected_columns=selected_columns,
                preview=preview,
            )
            st.success("Transformation applied.")
            st.rerun()

    elif action == "Drop columns above missing threshold":
        threshold = st.slider("Threshold (%)", min_value=0.0, max_value=100.0, value=30.0, step=1.0)
        if st.button("Apply missing-column drop", use_container_width=True):
            new_df, preview = drop_columns_by_missing_threshold(df, threshold)
            commit_transformation(
                new_df,
                operation="Drop columns above missing threshold",
                parameters={"threshold_percent": threshold},
                affected_columns=preview.get("columns_removed", []),
                preview=preview,
            )
            st.success("Transformation applied.")
            st.rerun()

    elif action == "Fill with constant":
        selected_columns = st.multiselect("Columns", columns)
        fill_value = st.text_input("Constant value")
        if st.button("Apply constant fill", use_container_width=True):
            if not selected_columns:
                st.warning("Select at least one column.")
                return
            new_df, preview = fill_missing_with_constant(df, selected_columns, fill_value)
            commit_transformation(
                new_df,
                operation="Fill missing values with constant",
                parameters={"columns": selected_columns, "value": fill_value},
                affected_columns=selected_columns,
                preview=preview,
            )
            st.success("Transformation applied.")
            st.rerun()

    elif action == "Fill with statistic":
        selected_columns = st.multiselect("Columns", columns)
        strategy = st.selectbox("Statistic", ["mean", "median", "mode", "most_frequent"])
        if st.button("Apply statistic fill", use_container_width=True):
            if not selected_columns:
                st.warning("Select at least one column.")
                return
            new_df, preview = fill_missing_with_statistic(df, selected_columns, strategy)
            commit_transformation(
                new_df,
                operation="Fill missing values with statistic",
                parameters={"columns": selected_columns, "strategy": strategy},
                affected_columns=selected_columns,
                preview=preview,
            )
            st.success("Transformation applied.")
            st.rerun()

    elif action == "Forward/backward fill":
        selected_columns = st.multiselect("Columns", columns)
        direction = st.selectbox("Direction", ["forward", "backward"])
        if st.button("Apply directional fill", use_container_width=True):
            if not selected_columns:
                st.warning("Select at least one column.")
                return
            new_df, preview = fill_missing_with_direction(df, selected_columns, direction)
            commit_transformation(
                new_df,
                operation="Fill missing values with direction",
                parameters={"columns": selected_columns, "direction": direction},
                affected_columns=selected_columns,
                preview=preview,
            )
            st.success("Transformation applied.")
            st.rerun()