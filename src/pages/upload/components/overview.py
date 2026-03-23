from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data.functions.profile import infer_column_groups, profile_dataframe


def render_overview(df: pd.DataFrame) -> None:
    st.html(
        """
        <style>
        div[data-testid="metric-container"] {
            background: var(--st-primary-color) !important;
            border: 1px solid var(--st-primary-color) !important;
            border-radius: 12px !important;
            padding: 12px 14px !important;
        }

        div[data-testid="metric-container"] * {
            color: white !important;
        }

        div[data-testid="metric-container"] label,
        div[data-testid="metric-container"] [data-testid="stMetricLabel"] {
            color: rgba(255, 255, 255, 0.85) !important;
        }

        div[data-testid="metric-container"] [data-testid="stMetricValue"] {
            color: white !important;
        }

        div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
            color: white !important;
        }
        </style>
        """
    )

    profile = profile_dataframe(df)
    groups = infer_column_groups(df)
    missing_cells = int(df.isna().sum().sum())

    metric_cols = st.columns(5)
    metric_cols[0].metric("Rows", f"{df.shape[0]:,}", border=True)
    metric_cols[1].metric("Columns", df.shape[1], border=True)
    metric_cols[2].metric("Numeric", len(groups["numeric"]), border=True)
    metric_cols[3].metric("Categorical", len(groups["categorical"]), border=True)
    metric_cols[4].metric("Missing cells", f"{missing_cells:,}", border=True)

    duplicates_col, outliers_col = st.columns(2)
    duplicates_col.metric("Duplicate rows", f"{profile['duplicates_count']:,}", border=True)

    outlier_total = (
        int(profile["outlier_summary"]["outlier_count"].sum())
        if not profile["outlier_summary"].empty
        else 0
    )
    outliers_col.metric("Potential outliers", f"{outlier_total:,}", border=True)

    if df.shape[0] < 1000 or df.shape[1] < 8:
        st.warning("This dataset is smaller than the project target of 1,000 rows and 8 columns.")

    tabs = st.tabs(
        [
            "Preview",
            "Columns & Types",
            "Summary Stats",
            "Missingness",
            "Outliers",
        ]
    )

    with tabs[0]:
        st.dataframe(df.head(50), use_container_width=True)

    with tabs[1]:
        st.dataframe(profile["dtypes"], use_container_width=True, hide_index=True)

    with tabs[2]:
        st.caption("Numeric summary")
        if profile["numeric_summary"].empty:
            st.info("No numeric columns found.")
        else:
            st.dataframe(
                profile["numeric_summary"],
                use_container_width=True,
                hide_index=True,
            )

        st.caption("Categorical summary")
        if profile["categorical_summary"].empty:
            st.info("No categorical columns found.")
        else:
            st.dataframe(
                profile["categorical_summary"],
                use_container_width=True,
                hide_index=True,
            )

    with tabs[3]:
        st.dataframe(profile["missing"], use_container_width=True, hide_index=True)

    with tabs[4]:
        if profile["outlier_summary"].empty:
            st.info("No numeric columns available for outlier profiling.")
        else:
            st.dataframe(
                profile["outlier_summary"],
                use_container_width=True,
                hide_index=True,
            )