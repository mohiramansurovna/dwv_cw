from __future__ import annotations

from typing import Any

import pandas as pd # pyright: ignore[reportMissingModuleSource]


def get_duplicate_rows(
    df: pd.DataFrame,
    subset: list[str] | None = None,
) -> pd.DataFrame:
    mask = df.duplicated(subset=subset, keep=False)
    return df.loc[mask].copy()


def remove_duplicates(
    df: pd.DataFrame,
    subset: list[str] | None = None,
    keep: str = "first",
) -> tuple[pd.DataFrame, dict[str, Any]]:
    duplicate_count = int(df.duplicated(subset=subset).sum())
    new_df = df.drop_duplicates(subset=subset, keep=keep)

    preview = {
        "rows_before": len(df),
        "rows_after": len(new_df),
        "rows_removed": len(df) - len(new_df),
        "duplicate_count": duplicate_count,
        "subset": subset or [],
        "keep": keep,
    }
    return new_df, preview