from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data.functions.profile import profile_dataframe
from src.data.functions.transforms import (
    drop_columns_by_missing_threshold,
    drop_rows_with_missing,
    fill_missing_values,
)
from src.pages.prepare.functions.actions import apply_and_rerun


def render_missing_values_tab(df: pd.DataFrame) -> None:
    """Render null-handling controls and previews."""
    profile = profile_dataframe(df)
    missing_df = profile["missing"]
    st.dataframe(missing_df, use_container_width=True, hide_index=True)

    missing_columns = missing_df.loc[missing_df["missing_count"] > 0, "column"].tolist()

    with st.expander("Drop rows with missing values", expanded=False):
        selected_columns = st.multiselect(
            "Columns to inspect for nulls",
            options=df.columns.tolist(),
            default=missing_columns[:3],
            key="missing-drop-cols",
        )
        rows_to_remove = int(df[selected_columns].isna().any(axis=1).sum()) if selected_columns else 0
        st.caption(f"Preview: {rows_to_remove} row(s) would be removed.")
        if st.button("Apply row drop", key="apply-drop-missing", disabled=not selected_columns):
            new_df = drop_rows_with_missing(df, selected_columns)
            apply_and_rerun(
                new_df,
                operation="Drop rows with missing values",
                parameters={"columns": selected_columns},
                affected_columns=selected_columns,
                preview={"rows_removed": rows_to_remove},
            )

    with st.expander("Drop columns by missing-value threshold", expanded=False):
        threshold_pct = st.slider("Threshold (%)", 0, 100, 40, key="missing-threshold")
        _, columns_to_drop = drop_columns_by_missing_threshold(df, float(threshold_pct))
        st.caption(
            "Preview: "
            + (", ".join(columns_to_drop) if columns_to_drop else "no columns would be removed.")
        )
        if st.button("Apply column drop", key="apply-drop-columns-threshold"):
            new_df, columns_dropped = drop_columns_by_missing_threshold(df, float(threshold_pct))
            apply_and_rerun(
                new_df,
                operation="Drop columns by missing threshold",
                parameters={"threshold_pct": threshold_pct},
                affected_columns=columns_dropped,
                preview={"columns_removed": columns_dropped},
            )

    with st.expander("Fill missing values", expanded=True):
        selected_columns = st.multiselect(
            "Columns to fill",
            options=missing_columns,
            default=missing_columns[:2],
            key="missing-fill-cols",
        )
        strategy = st.selectbox(
            "Strategy",
            options=["constant", "mean", "median", "mode", "most_frequent", "ffill", "bfill"],
            key="missing-strategy",
        )
        constant_value = None
        if strategy == "constant":
            constant_value = st.text_input("Constant value", value="Unknown")
        affected_cells = int(df[selected_columns].isna().sum().sum()) if selected_columns else 0
        st.caption(f"Preview: {affected_cells} missing cell(s) would be targeted.")
        if st.button("Apply fill strategy", key="apply-fill-missing", disabled=not selected_columns):
            try:
                new_df = fill_missing_values(df, selected_columns, strategy, constant_value)
                apply_and_rerun(
                    new_df,
                    operation="Fill missing values",
                    parameters={"columns": selected_columns, "strategy": strategy, "constant": constant_value},
                    affected_columns=selected_columns,
                    preview={"targeted_cells": affected_cells},
                )
            except Exception as exc:
                st.error(f"Could not fill missing values: {exc}")
