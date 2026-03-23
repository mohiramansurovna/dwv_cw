from __future__ import annotations

from collections.abc import Iterable

import pandas as pd
import streamlit as st

from src.data.functions.profile import infer_column_groups
from src.pages.visualize.functions.charting import build_chart
from src.pages.visualize.functions.filters import apply_filters
from src.pages.visualize.functions.state import ensure_saved_charts, save_chart_image


def render_visualization_builder(df: pd.DataFrame) -> None:
    """Render all chart controls, chart output, and saved chart images."""
    groups = infer_column_groups(df)
    numeric_columns = groups["numeric"]
    categorical_columns = groups["categorical"]
    x_candidates = df.columns.tolist()
    y_candidates = numeric_columns


    with st.container(border=True):
        col1, col2 = st.columns(2)

        # --- LEFT: Category Filter ---
        with col1:
            st.markdown("**Category Filter**")

            category_filter_column = st.selectbox(
                "Column",
                options=["None"] + categorical_columns,
                key="cat_col"
            )
            category_filter_column = None if category_filter_column == "None" else category_filter_column

            category_values = []
            if category_filter_column:
                values = sorted(df[category_filter_column].dropna().astype(str).unique().tolist())
                category_values = st.multiselect(
                    "Values",
                    options=values,
                    default=values[: min(5, len(values))],
                    key="cat_vals"
                )

        # --- RIGHT: Numeric Filter ---
        with col2:
            st.markdown("**Numeric Filter**")

            numeric_filter_column = st.selectbox(
                "Column",
                options=["None"] + numeric_columns,
                key="num_col"
            )
            numeric_filter_column = None if numeric_filter_column == "None" else numeric_filter_column

            numeric_range = None
            if numeric_filter_column:
                series = pd.to_numeric(df[numeric_filter_column], errors="coerce").dropna()
                if not series.empty:
                    numeric_range = st.slider(
                        "Range",
                        min_value=float(series.min()),
                        max_value=float(series.max()),
                        value=(float(series.min()), float(series.max())),
                        key="num_range"
                    )
                    
    filtered_df = apply_filters(
        df,
        category_filter_column,
        category_values,
        numeric_filter_column,
        numeric_range,
    )

    st.caption(f"Filtered rows available for charting: {filtered_df.shape[0]:,}")
    if filtered_df.empty:
        st.warning("The active filters removed all rows. Adjust the filters to continue.")
        render_saved_chart_definitions()
        return

    chart_type = st.selectbox(
        "Chart type",
        options=["histogram", "box_plot", "scatter_plot", "line_chart", "bar_chart", "heatmap"],
        format_func=lambda item: item.replace("_", " ").title(),
    )

    x_column = None
    y_column = None
    aggregation = "mean"
    top_n = 10

    if chart_type == "histogram":
        x_column = st.selectbox("Numeric column", options=numeric_columns)
    elif chart_type == "box_plot":
        y_column = st.selectbox("Numeric column", options=numeric_columns)
    elif chart_type == "scatter_plot":
        x_column = st.selectbox("X column", options=numeric_columns)
        y_column = st.selectbox("Y column", options=numeric_columns, index=min(1, len(numeric_columns) - 1))
    elif chart_type == "line_chart":
        x_column = st.selectbox("X column", options=x_candidates)
        y_column = st.selectbox("Y column", options=y_candidates)
        aggregation = st.selectbox("Aggregation", options=["sum", "mean", "count", "median"])
    elif chart_type == "bar_chart":
        x_column = st.selectbox("Category column", options=categorical_columns or x_candidates)
        y_choices = ["None"] + y_candidates
        y_column = st.selectbox("Y column", options=y_choices)
        y_column = None if y_column == "None" else y_column
        aggregation = st.selectbox("Aggregation", options=["count", "sum", "mean", "median"])
        top_n = st.slider("Top N categories", 3, 25, 10)
        if aggregation != "count" and y_column is None:
            st.info("Choose a numeric Y column for sum, mean, or median.")
            render_saved_chart_definitions()
            return

    if chart_type == "heatmap" and len(numeric_columns) < 2:
        st.info("At least two numeric columns are required for a correlation heatmap.")
        render_saved_chart_definitions()
        return

    try:
        fig = build_chart(
            filtered_df,
            chart_type=chart_type,
            x_column=x_column,
            y_column=y_column,
            aggregation=aggregation,
            top_n=top_n,
        )
        st.pyplot(fig, use_container_width=True)
    except Exception as exc:
        st.error(f"Could not build the chart: {exc}")
        render_saved_chart_definitions()
        return

    if st.button("Save chart image"):
        filename = save_chart_image(fig, chart_type, x_column, y_column)
        st.success(f"Saved chart image: {filename}")

    render_saved_chart_definitions()


def render_saved_chart_definitions() -> None:
    """Render the session-stored chart images below the builder."""
    saved_charts = ensure_saved_charts()
    if saved_charts:
        st.divider()
        st.subheader("Saved charts")
        for chart in saved_charts:
            st.caption(chart["filename"])
            st.image(chart["image_bytes"], use_container_width=True)
