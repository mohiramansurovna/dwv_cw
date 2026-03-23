from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def build_chart(
    df: pd.DataFrame,
    chart_type: str,
    x_column: str | None,
    y_column: str | None,
    group_column: str | None,
    aggregation: str,
    top_n: int,
) -> plt.Figure:
    """Build the requested matplotlib figure from the current chart settings."""
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
        working_df = df.copy().sort_values(x_column)
        agg_map = {"sum": "sum", "mean": "mean", "count": "count", "median": "median"}
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
        agg_map = {"sum": "sum", "mean": "mean", "count": "count", "median": "median"}
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
