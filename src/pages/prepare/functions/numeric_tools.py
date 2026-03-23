from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data.functions.profile import infer_column_groups
from src.data.functions.transforms import (
    cap_outliers,
    remove_outlier_rows,
    scale_numeric,
    summarize_outliers,
)
from src.pages.prepare.functions.actions import apply_and_rerun


def render_numeric_tab(df: pd.DataFrame) -> None:
    """Render outlier detection plus capping or row-removal actions."""
    numeric_columns = infer_column_groups(df)["numeric"]
    if not numeric_columns:
        st.info("No numeric columns are available.")
        return

    selected_columns = st.multiselect(
        "Numeric columns",
        options=numeric_columns,
        default=numeric_columns[:2],
        key="outlier-cols",
    )
    method = st.selectbox("Detection method", options=["iqr", "zscore"])
    z_threshold = 3.0
    if method == "zscore":
        z_threshold = st.slider("Z-score threshold", 1.0, 5.0, 3.0, 0.1)

    if selected_columns:
        summary_df, _ = summarize_outliers(
            df,
            selected_columns,
            method="iqr" if method == "iqr" else "zscore",
            z_threshold=z_threshold,
        )
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    else:
        st.info("Choose at least one numeric column.")

    action = st.radio(
        "Action",
        options=["do_nothing", "cap", "remove_rows"],
        horizontal=True,
        format_func=lambda item: {
            "do_nothing": "Do nothing",
            "cap": "Cap / winsorize",
            "remove_rows": "Remove outlier rows",
        }[item],
    )

    if action == "cap" and st.button("Apply capping", disabled=not selected_columns):
        new_df, impact = cap_outliers(
            df,
            selected_columns,
            method="iqr" if method == "iqr" else "zscore",
            z_threshold=z_threshold,
        )
        apply_and_rerun(
            new_df,
            operation="Cap outliers",
            parameters={"columns": selected_columns, "method": method, "z_threshold": z_threshold},
            affected_columns=selected_columns,
            preview={"values_capped": impact},
        )

    if action == "remove_rows" and st.button("Remove outlier rows", disabled=not selected_columns):
        new_df, removed_count = remove_outlier_rows(
            df,
            selected_columns,
            method="iqr" if method == "iqr" else "zscore",
            z_threshold=z_threshold,
        )
        apply_and_rerun(
            new_df,
            operation="Remove outlier rows",
            parameters={"columns": selected_columns, "method": method, "z_threshold": z_threshold},
            affected_columns=selected_columns,
            preview={"rows_removed": removed_count},
        )


def render_scaling_tab(df: pd.DataFrame) -> None:
    """Render numeric scaling controls with before/after statistics."""
    numeric_columns = infer_column_groups(df)["numeric"]
    if not numeric_columns:
        st.info("No numeric columns are available for scaling.")
        return

    selected_columns = st.multiselect(
        "Columns to scale",
        options=numeric_columns,
        default=numeric_columns[:2],
        key="scale-cols",
    )
    method = st.selectbox(
        "Scaling method",
        options=["min_max", "z_score"],
        format_func=lambda item: "Min-max" if item == "min_max" else "Z-score",
    )

    if selected_columns:
        before_stats = df[selected_columns].describe().transpose()[["mean", "std", "min", "max"]]
        st.caption("Before scaling")
        st.dataframe(before_stats.round(4), use_container_width=True)

    if st.button("Apply scaling", disabled=not selected_columns):
        try:
            new_df = scale_numeric(df, selected_columns, method)
            after_stats = new_df[selected_columns].describe().transpose()[["mean", "std", "min", "max"]]
            apply_and_rerun(
                new_df,
                operation="Scale numeric columns",
                parameters={"columns": selected_columns, "method": method},
                affected_columns=selected_columns,
                preview={"after_stats": after_stats.round(4).to_dict()},
            )
        except Exception as exc:
            st.error(f"Scaling failed: {exc}")
