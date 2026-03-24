from __future__ import annotations

from typing import Any

import pandas as pd # pyright: ignore[reportMissingModuleSource]


def convert_column_type(
    df: pd.DataFrame,
    column: str,
    target_type: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    new_df = df.copy()

    if target_type == "numeric":
        new_df[column] = pd.to_numeric(new_df[column], errors="coerce")
    elif target_type == "categorical":
        new_df[column] = new_df[column].astype("category")
    elif target_type == "datetime":
        new_df[column] = pd.to_datetime(new_df[column], errors="coerce")
    elif target_type == "string":
        new_df[column] = new_df[column].astype("string")
    else:
        raise ValueError("Unsupported target type.")

    preview = {
        "column": column,
        "target_type": target_type,
        "dtype_after": str(new_df[column].dtype),
    }
    return new_df, preview


def parse_datetime_column(
    df: pd.DataFrame,
    column: str,
    date_format: str | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    new_df = df.copy()
    new_df[column] = pd.to_datetime(new_df[column], format=date_format, errors="coerce")

    preview = {
        "column": column,
        "format": date_format or "auto",
        "dtype_after": str(new_df[column].dtype),
    }
    return new_df, preview


def clean_dirty_numeric_column(
    df: pd.DataFrame,
    column: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    new_df = df.copy()

    cleaned = (
        new_df[column]
        .astype("string")
        .str.replace(",", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.replace("€", "", regex=False)
        .str.replace("£", "", regex=False)
        .str.strip()
    )

    new_df[column] = pd.to_numeric(cleaned, errors="coerce")

    preview = {
        "column": column,
        "dtype_after": str(new_df[column].dtype),
    }
    return new_df, preview