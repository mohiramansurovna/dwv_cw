from __future__ import annotations

import pandas as pd


def apply_filters(
    df: pd.DataFrame,
    category_column: str | None,
    category_values: list[str],
    numeric_column: str | None,
    numeric_range: tuple[float, float] | None,
) -> pd.DataFrame:
    """Apply the optional category and numeric filters before charting."""
    filtered_df = df.copy()
    if category_column and category_values:
        filtered_df = filtered_df[filtered_df[category_column].isin(category_values)]
    if numeric_column and numeric_range is not None:
        lower, upper = numeric_range
        numeric_series = pd.to_numeric(filtered_df[numeric_column], errors="coerce")
        filtered_df = filtered_df[numeric_series.between(lower, upper)]
    return filtered_df
