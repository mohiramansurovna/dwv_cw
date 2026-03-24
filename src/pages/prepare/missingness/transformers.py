from __future__ import annotations

from typing import Any

import pandas as pd # pyright: ignore[reportMissingModuleSource]


def get_missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = pd.DataFrame(
        {
            "column": df.columns,
            "missing_count": df.isna().sum().values,
            "missing_percent": (df.isna().mean() * 100).round(2).values,
        }
    )
    return summary.sort_values(by=["missing_count", "column"], ascending=[False, True]).reset_index(drop=True)


def drop_rows_with_missing(
    df: pd.DataFrame,
    columns: list[str],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    new_df = df.dropna(subset=columns)

    preview = {
        "rows_before": len(df),
        "rows_after": len(new_df),
        "rows_removed": len(df) - len(new_df),
        "affected_columns": columns,
    }
    return new_df, preview


def drop_columns_by_missing_threshold(
    df: pd.DataFrame,
    threshold_percent: float,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    missing_percent = df.isna().mean() * 100
    columns_to_drop = missing_percent[missing_percent > threshold_percent].index.tolist()

    new_df = df.drop(columns=columns_to_drop)

    preview = {
        "columns_before": len(df.columns),
        "columns_after": len(new_df.columns),
        "columns_removed": columns_to_drop,
        "threshold_percent": threshold_percent,
    }
    return new_df, preview


def fill_missing_with_constant(
    df: pd.DataFrame,
    columns: list[str],
    value: Any,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    new_df = df.copy()
    before_missing = int(new_df[columns].isna().sum().sum())
    new_df[columns] = new_df[columns].fillna(value)
    after_missing = int(new_df[columns].isna().sum().sum())

    preview = {
        "affected_columns": columns,
        "missing_before": before_missing,
        "missing_after": after_missing,
        "fill_value": str(value),
    }
    return new_df, preview


def fill_missing_with_statistic(
    df: pd.DataFrame,
    columns: list[str],
    strategy: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    new_df = df.copy()

    for column in columns:
        series = new_df[column]

        if strategy == "mean":
            fill_value = series.mean()
        elif strategy == "median":
            fill_value = series.median()
        elif strategy in {"mode", "most_frequent"}:
            mode = series.mode(dropna=True)
            fill_value = mode.iloc[0] if not mode.empty else None
        else:
            raise ValueError("Unsupported fill strategy.")

        new_df[column] = series.fillna(fill_value)

    preview = {
        "affected_columns": columns,
        "strategy": strategy,
    }
    return new_df, preview


def fill_missing_with_direction(
    df: pd.DataFrame,
    columns: list[str],
    direction: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    new_df = df.copy()

    if direction == "forward":
        new_df[columns] = new_df[columns].ffill()
    elif direction == "backward":
        new_df[columns] = new_df[columns].bfill()
    else:
        raise ValueError("Unsupported fill direction.")

    preview = {
        "affected_columns": columns,
        "direction": direction,
    }
    return new_df, preview