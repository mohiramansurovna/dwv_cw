from __future__ import annotations

from collections.abc import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from src.data.functions.profile import infer_column_groups
from src.data.functions.store import get_current_data
from src.data.ui import render_workspace_panel


SAVED_CHARTS_KEY = "saved_charts"


def _apply_filters(
    df: pd.DataFrame,
    category_column: str | None,
    category_values: list[str],
    numeric_column: str | None,
    numeric_range: tuple[float, float] | None,
) -> pd.DataFrame:
    filtered_df = df.copy()
    if category_column and category_values:
        filtered_df = filtered_df[filtered_df[category_column].isin(category_values)]
    if numeric_column and numeric_range is not None:
        lower, upper = numeric_range
        numeric_series = pd.to_numeric(filtered_df[numeric_column], errors="coerce")
        filtered_df = filtered_df[numeric_series.between(lower, upper)]
    return filtered_df


def _ensure_saved_charts() -> list[dict]:
    if SAVED_CHARTS_KEY not in st.session_state:
        st.session_state[SAVED_CHARTS_KEY] = []
    return st.session_state[SAVED_CHARTS_KEY]


def _save_chart_spec(spec: dict) -> None:
    saved = _ensure_saved_charts()
    saved.append(spec)


def _build_chart(
    df: pd.DataFrame,
    chart_type: str,
    x_column: str | None,
    y_column: str | None,
    group_column: str | None,
    aggregation: str,
    top_n: int,
) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(10, 5))

    if chart_type == "histogram":
        values = pd.to_numeric(df[x_column], errors="coerce").dropna()
        ax.hist(values, bins=20, color="#1f77b4", edgecolor="white")
        ax.set_title(f"Histogram of {x_column}")
        ax.set_xlabel(x_column)
        ax.set_ylabel("Count")

    elif chart_type == "box_plot":
        if group_column:
            grouped = [
                pd.to_numeric(group[y_column], errors="coerce").dropna().values
                for _, group in df.groupby(group_column)
            ]
            labels = [str(name) for name, _ in df.groupby(group_column)]
            ax.boxplot(grouped, labels=labels, vert=True)
            ax.set_xlabel(group_column)
        else:
            values = pd.to_numeric(df[y_column], errors="coerce").dropna()
            ax.boxplot(values, vert=True)
        ax.set_title(f"Box plot of {y_column}")
        ax.set_ylabel(y_column)

    elif chart_type == "scatter_plot":
        if group_column:
            cmap = plt.get_cmap("tab10")
            for index, (name, group) in enumerate(df.groupby(group_column)):
                ax.scatter(
                    pd.to_numeric(group[x_column], errors="coerce"),
                    pd.to_numeric(group[y_column], errors="coerce"),
                    label=str(name),
                    alpha=0.7,
                    color=cmap(index % 10),
                )
            ax.legend()
        else:
            ax.scatter(
                pd.to_numeric(df[x_column], errors="coerce"),
                pd.to_numeric(df[y_column], errors="coerce"),
                alpha=0.7,
                color="#ff7f0e",
            )
        ax.set_title(f"{y_column} vs {x_column}")
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)

    elif chart_type == "line_chart":
        working_df = df.copy()
        working_df = working_df.sort_values(x_column)
        agg_map = {
            "sum": "sum",
            "mean": "mean",
            "count": "count",
            "median": "median",
        }
        if group_column:
            grouped = (
                working_df.groupby([x_column, group_column])[y_column]
                .agg(agg_map[aggregation])
                .reset_index()
            )
            for name, group in grouped.groupby(group_column):
                ax.plot(group[x_column], group[y_column], marker="o", label=str(name))
            ax.legend()
        else:
            grouped = working_df.groupby(x_column)[y_column].agg(agg_map[aggregation]).reset_index()
            ax.plot(grouped[x_column], grouped[y_column], marker="o", color="#2ca02c")
        ax.set_title(f"{aggregation.title()} {y_column} by {x_column}")
        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)

    elif chart_type == "bar_chart":
        agg_map = {
            "sum": "sum",
            "mean": "mean",
            "count": "count",
            "median": "median",
        }
        if aggregation == "count":
            grouped = df.groupby(x_column).size().reset_index(name="value")
        else:
            grouped = df.groupby(x_column)[y_column].agg(agg_map[aggregation]).reset_index(name="value")
        grouped = grouped.sort_values("value", ascending=False).head(top_n)
        ax.bar(grouped[x_column].astype(str), grouped["value"], color="#d62728")
        ax.set_title(f"Top {top_n} {x_column} categories")
        ax.set_xlabel(x_column)
        ax.set_ylabel(aggregation.title())
        ax.tick_params(axis="x", rotation=45)

    elif chart_type == "heatmap":
        corr_df = df.select_dtypes(include=np.number).corr(numeric_only=True)
        image = ax.imshow(corr_df, cmap="coolwarm", aspect="auto", vmin=-1, vmax=1)
        ax.set_xticks(range(len(corr_df.columns)))
        ax.set_xticklabels(corr_df.columns, rotation=45, ha="right")
        ax.set_yticks(range(len(corr_df.columns)))
        ax.set_yticklabels(corr_df.columns)
        ax.set_title("Correlation matrix")
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)

    fig.tight_layout()
    return fig


def render_visualize_page() -> None:
    left, right = st.columns([3.2, 1.2])
    df = get_current_data()

    with left:
        st.title("Visualization Builder")

        if df is None:
            st.info("Load and prepare a dataset before building charts.")
        else:
            groups = infer_column_groups(df)
            numeric_columns = groups["numeric"]
            categorical_columns = groups["categorical"]
            x_candidates = df.columns.tolist()
            y_candidates = numeric_columns

            with st.expander("Filters", expanded=True):
                category_filter_column = st.selectbox(
                    "Category filter column",
                    options=["None"] + categorical_columns,
                )
                category_filter_column = None if category_filter_column == "None" else category_filter_column
                category_values: list[str] = []
                if category_filter_column:
                    values = sorted(df[category_filter_column].dropna().astype(str).unique().tolist())
                    category_values = st.multiselect(
                        "Category values",
                        options=values,
                        default=values[: min(5, len(values))],
                    )

                numeric_filter_column = st.selectbox(
                    "Numeric filter column",
                    options=["None"] + numeric_columns,
                )
                numeric_filter_column = None if numeric_filter_column == "None" else numeric_filter_column
                numeric_range = None
                if numeric_filter_column:
                    series = pd.to_numeric(df[numeric_filter_column], errors="coerce").dropna()
                    if not series.empty:
                        numeric_range = st.slider(
                            "Numeric range",
                            min_value=float(series.min()),
                            max_value=float(series.max()),
                            value=(float(series.min()), float(series.max())),
                        )

            filtered_df = _apply_filters(
                df,
                category_filter_column,
                category_values,
                numeric_filter_column,
                numeric_range,
            )

            st.caption(f"Filtered rows available for charting: {filtered_df.shape[0]:,}")
            if filtered_df.empty:
                st.warning("The active filters removed all rows. Adjust the filters to continue.")
            else:
                chart_type = st.selectbox(
                    "Chart type",
                    options=[
                        "histogram",
                        "box_plot",
                        "scatter_plot",
                        "line_chart",
                        "bar_chart",
                        "heatmap",
                    ],
                    format_func=lambda item: item.replace("_", " ").title(),
                )

                x_column = None
                y_column = None
                group_column = None
                aggregation = "mean"
                top_n = 10

                if chart_type == "histogram":
                    x_column = st.selectbox("Numeric column", options=numeric_columns)
                elif chart_type == "box_plot":
                    y_column = st.selectbox("Numeric column", options=numeric_columns)
                    group_column = st.selectbox("Group column (optional)", options=["None"] + categorical_columns)
                    group_column = None if group_column == "None" else group_column
                elif chart_type == "scatter_plot":
                    x_column = st.selectbox("X column", options=numeric_columns)
                    y_column = st.selectbox("Y column", options=numeric_columns, index=min(1, len(numeric_columns) - 1))
                    group_column = st.selectbox("Color/group column (optional)", options=["None"] + categorical_columns)
                    group_column = None if group_column == "None" else group_column
                elif chart_type == "line_chart":
                    x_column = st.selectbox("X column", options=x_candidates)
                    y_column = st.selectbox("Y column", options=y_candidates)
                    group_column = st.selectbox("Group column (optional)", options=["None"] + categorical_columns)
                    group_column = None if group_column == "None" else group_column
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
                        chart_type = ""

                if chart_type == "heatmap" and len(numeric_columns) < 2:
                    st.info("At least two numeric columns are required for a correlation heatmap.")
                    chart_type = ""

                if chart_type:
                    try:
                        fig = _build_chart(
                            filtered_df,
                            chart_type=chart_type,
                            x_column=x_column,
                            y_column=y_column,
                            group_column=group_column,
                            aggregation=aggregation,
                            top_n=top_n,
                        )
                        st.pyplot(fig, clear_figure=True, use_container_width=True)
                    except Exception as exc:
                        st.error(f"Could not build the chart: {exc}")
                    else:
                        chart_spec = {
                            "chart_type": chart_type,
                            "x_column": x_column,
                            "y_column": y_column,
                            "group_column": group_column,
                            "aggregation": aggregation,
                            "top_n": top_n,
                            "filters": {
                                "category_filter_column": category_filter_column,
                                "category_values": category_values,
                                "numeric_filter_column": numeric_filter_column,
                                "numeric_range": list(numeric_range) if isinstance(numeric_range, Iterable) else None,
                            },
                        }

                        if st.button("Save chart definition to session report"):
                            _save_chart_spec(chart_spec)
                            st.success("Chart definition saved for export.")

            saved_charts = _ensure_saved_charts()
            if saved_charts:
                st.divider()
                st.subheader("Saved chart definitions")
                st.json(saved_charts)

    with right:
        render_workspace_panel()
