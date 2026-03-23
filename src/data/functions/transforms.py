from __future__ import annotations

import re
from io import BytesIO

import numpy as np
import pandas as pd


def drop_rows_with_missing(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Remove rows where any of the selected columns is null."""
    return df.dropna(subset=columns).copy()


def drop_columns_by_missing_threshold(
    df: pd.DataFrame, threshold_pct: float
) -> tuple[pd.DataFrame, list[str]]:
    """Remove columns whose missing-value percentage is above the chosen cutoff."""
    missing_pct = df.isna().mean() * 100
    columns_to_drop = missing_pct[missing_pct >= threshold_pct].index.tolist()
    return df.drop(columns=columns_to_drop).copy(), columns_to_drop


def fill_missing_values(
    df: pd.DataFrame,
    columns: list[str],
    strategy: str,
    constant_value: str | None = None,
) -> pd.DataFrame:
    """Fill nulls in the selected columns using the strategy chosen in the UI."""
    new_df = df.copy()

    for column in columns:
        series = new_df[column]
        if strategy == "constant":
            new_df[column] = series.fillna(constant_value)
        elif strategy == "mean":
            new_df[column] = series.fillna(pd.to_numeric(series, errors="coerce").mean())
        elif strategy == "median":
            new_df[column] = series.fillna(pd.to_numeric(series, errors="coerce").median())
        elif strategy in {"mode", "most_frequent"}:
            mode = series.mode(dropna=True)
            fill_value = mode.iloc[0] if not mode.empty else None
            new_df[column] = series.fillna(fill_value)
        elif strategy == "ffill":
            new_df[column] = series.ffill()
        elif strategy == "bfill":
            new_df[column] = series.bfill()
        else:
            raise ValueError(f"Unsupported strategy: {strategy}")

    return new_df


def detect_duplicates(df: pd.DataFrame, subset: list[str] | None = None) -> pd.DataFrame:
    """Return all rows that belong to a duplicate group."""
    subset = subset or None
    mask = df.duplicated(subset=subset, keep=False)
    return df.loc[mask].copy()


def remove_duplicates(
    df: pd.DataFrame,
    subset: list[str] | None = None,
    keep: str = "first",
) -> pd.DataFrame:
    """Drop duplicate rows, optionally using only a subset of key columns."""
    subset = subset or None
    return df.drop_duplicates(subset=subset, keep=keep).copy()


def _clean_dirty_numeric(series: pd.Series) -> pd.Series:
    """Strip common currency/formatting characters before numeric conversion."""
    cleaned = (
        series.astype("string")
        .str.replace(r"[\$,£€,%]", "", regex=True)
        .str.replace(",", "", regex=False)
        .str.replace(r"\((.+)\)", r"-\1", regex=True)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")


def convert_column_type(
    df: pd.DataFrame,
    column: str,
    target_type: str,
    datetime_format: str | None = None,
) -> pd.DataFrame:
    """Convert one column to numeric, categorical, or datetime form."""
    new_df = df.copy()

    if target_type == "numeric":
        new_df[column] = _clean_dirty_numeric(new_df[column])
    elif target_type == "categorical":
        new_df[column] = new_df[column].astype("string")
    elif target_type == "datetime":
        fmt = datetime_format or None
        new_df[column] = pd.to_datetime(new_df[column], format=fmt, errors="coerce")
    else:
        raise ValueError(f"Unsupported target type: {target_type}")

    return new_df


def standardize_text(
    df: pd.DataFrame,
    columns: list[str],
    trim_whitespace: bool = True,
    case_style: str = "unchanged",
) -> pd.DataFrame:
    """Normalize text casing and whitespace in categorical columns."""
    new_df = df.copy()

    for column in columns:
        series = new_df[column].astype("string")
        if trim_whitespace:
            series = series.str.strip()
        if case_style == "lower":
            series = series.str.lower()
        elif case_style == "upper":
            series = series.str.upper()
        elif case_style == "title":
            series = series.str.title()
        new_df[column] = series

    return new_df


def apply_category_mapping(
    df: pd.DataFrame,
    column: str,
    mapping: dict[str, str],
    unmatched_to_other: bool = False,
) -> pd.DataFrame:
    """Replace category labels using the mapping editor values from the UI."""
    new_df = df.copy()
    original = new_df[column].copy()
    mapped = original.map(mapping)

    if unmatched_to_other:
        new_values = pd.Series("Other", index=new_df.index, dtype="object")
        new_values[original.isna()] = np.nan
        new_values[original.isin(mapping.keys())] = mapped[original.isin(mapping.keys())]
        new_df[column] = new_values
    else:
        new_df[column] = original.replace(mapping)

    return new_df


def group_rare_categories(
    df: pd.DataFrame,
    column: str,
    threshold_pct: float,
) -> tuple[pd.DataFrame, list[str]]:
    """Collapse infrequent category values into a shared 'Other' bucket."""
    new_df = df.copy()
    frequencies = new_df[column].value_counts(normalize=True, dropna=True) * 100
    rare_categories = frequencies[frequencies < threshold_pct].index.tolist()
    new_df[column] = new_df[column].where(~new_df[column].isin(rare_categories), "Other")
    return new_df, rare_categories


def one_hot_encode(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Expand categorical columns into dummy/indicator columns."""
    return pd.get_dummies(df, columns=columns, dummy_na=False).copy()


def summarize_outliers(
    df: pd.DataFrame,
    columns: list[str],
    method: str = "iqr",
    z_threshold: float = 3.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build an outlier summary table plus a row mask for later actions."""
    summary_rows: list[dict[str, object]] = []
    mask_df = pd.DataFrame(index=df.index)

    for column in columns:
        series = pd.to_numeric(df[column], errors="coerce")
        valid = series.dropna()
        if valid.empty:
            mask_df[column] = False
            continue

        if method == "iqr":
            q1 = valid.quantile(0.25)
            q3 = valid.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
        else:
            mean = valid.mean()
            std = valid.std(ddof=0)
            lower = mean - z_threshold * std
            upper = mean + z_threshold * std

        mask = (series < lower) | (series > upper)
        mask_df[column] = mask.fillna(False)
        summary_rows.append(
            {
                "column": column,
                "outlier_count": int(mask.sum()),
                "outlier_pct": round(float(mask.mean() * 100), 2),
                "lower_bound": round(float(lower), 4),
                "upper_bound": round(float(upper), 4),
            }
        )

    return pd.DataFrame(summary_rows), mask_df


def cap_outliers(
    df: pd.DataFrame,
    columns: list[str],
    method: str = "iqr",
    z_threshold: float = 3.0,
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Winsorize outlier values by clipping them to computed lower/upper bounds."""
    summary_df, _ = summarize_outliers(df, columns, method=method, z_threshold=z_threshold)
    bounds = summary_df.set_index("column")[["lower_bound", "upper_bound"]].to_dict("index")

    new_df = df.copy()
    impact: dict[str, int] = {}
    for column in columns:
        series = pd.to_numeric(new_df[column], errors="coerce")
        if column not in bounds:
            impact[column] = 0
            continue
        lower = bounds[column]["lower_bound"]
        upper = bounds[column]["upper_bound"]
        clipped = series.clip(lower=lower, upper=upper)
        impact[column] = int((series != clipped).fillna(False).sum())
        new_df[column] = clipped

    return new_df, impact


def remove_outlier_rows(
    df: pd.DataFrame,
    columns: list[str],
    method: str = "iqr",
    z_threshold: float = 3.0,
) -> tuple[pd.DataFrame, int]:
    """Drop rows that contain at least one outlier in the selected columns."""
    _, mask_df = summarize_outliers(df, columns, method=method, z_threshold=z_threshold)
    rows_to_remove = mask_df.any(axis=1)
    removed_count = int(rows_to_remove.sum())
    return df.loc[~rows_to_remove].copy(), removed_count


def scale_numeric(df: pd.DataFrame, columns: list[str], method: str) -> pd.DataFrame:
    """Apply min-max or z-score scaling to the chosen numeric columns."""
    new_df = df.copy()
    for column in columns:
        series = pd.to_numeric(new_df[column], errors="coerce")
        if method == "min_max":
            denominator = series.max() - series.min()
            new_df[column] = 0.0 if denominator == 0 else (series - series.min()) / denominator
        elif method == "z_score":
            std = series.std(ddof=0)
            new_df[column] = 0.0 if std == 0 else (series - series.mean()) / std
        else:
            raise ValueError(f"Unsupported scaling method: {method}")
    return new_df


def rename_column(df: pd.DataFrame, old_name: str, new_name: str) -> pd.DataFrame:
    """Rename a single column."""
    return df.rename(columns={old_name: new_name}).copy()


def drop_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Remove the selected columns from the working dataframe."""
    return df.drop(columns=columns).copy()


def _safe_identifier(column_name: str) -> str:
    """Turn any column name into a Python-safe alias for formula evaluation."""
    identifier = re.sub(r"\W+", "_", column_name).strip("_") or "column"
    if identifier[0].isdigit():
        identifier = f"col_{identifier}"
    return identifier


def create_formula_column(df: pd.DataFrame, new_column: str, formula: str) -> pd.DataFrame:
    """Evaluate a limited Python expression and store the result as a new column."""
    new_df = df.copy()
    env: dict[str, object] = {
        "np": np,
        "pd": pd,
        "log": np.log,
        "sqrt": np.sqrt,
        "abs": np.abs,
        "clip": lambda series, lower=None, upper=None: series.clip(lower=lower, upper=upper),
        "where": np.where,
        "col": lambda name: new_df[name],
    }

    for column in new_df.columns:
        env[_safe_identifier(column)] = new_df[column]
        if column.isidentifier():
            env[column] = new_df[column]

    result = eval(formula, {"__builtins__": {}}, env)
    if np.isscalar(result):
        new_df[new_column] = result
    else:
        new_df[new_column] = pd.Series(result, index=new_df.index)
    return new_df


def bin_numeric_column(
    df: pd.DataFrame,
    source_column: str,
    new_column: str,
    bins: int,
    method: str,
) -> pd.DataFrame:
    """Bucket a numeric column into equal-width or quantile-based bins."""
    new_df = df.copy()
    series = pd.to_numeric(new_df[source_column], errors="coerce")
    if method == "equal_width":
        new_df[new_column] = pd.cut(series, bins=bins)
    else:
        new_df[new_column] = pd.qcut(series, q=bins, duplicates="drop")
    return new_df


def validate_numeric_range(
    df: pd.DataFrame,
    column: str,
    min_value: float | None = None,
    max_value: float | None = None,
) -> pd.DataFrame:
    """Return rows whose numeric values fall outside the allowed range."""
    series = pd.to_numeric(df[column], errors="coerce")
    mask = pd.Series(False, index=df.index)
    if min_value is not None:
        mask |= series < min_value
    if max_value is not None:
        mask |= series > max_value

    violations = df.loc[mask, [column]].copy()
    violations.insert(0, "row_index", violations.index)
    violations.insert(1, "rule", "numeric_range")
    violations["details"] = f"Expected {min_value} <= value <= {max_value}"
    return violations.reset_index(drop=True)


def validate_allowed_categories(
    df: pd.DataFrame,
    column: str,
    allowed_values: list[str],
) -> pd.DataFrame:
    """Return rows whose category value is not in the allowed list."""
    mask = ~df[column].isin(allowed_values) & df[column].notna()
    violations = df.loc[mask, [column]].copy()
    violations.insert(0, "row_index", violations.index)
    violations.insert(1, "rule", "allowed_categories")
    violations["details"] = f"Allowed: {', '.join(allowed_values)}"
    return violations.reset_index(drop=True)


def validate_non_null(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Collect rows that violate non-null rules for the selected columns."""
    frames: list[pd.DataFrame] = []
    for column in columns:
        mask = df[column].isna()
        if not mask.any():
            continue
        violations = df.loc[mask, [column]].copy()
        violations.insert(0, "row_index", violations.index)
        violations.insert(1, "rule", "non_null")
        violations["details"] = "Expected non-null value"
        frames.append(violations.reset_index(drop=True))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Serialize a dataframe into CSV bytes for download buttons."""
    return df.to_csv(index=False).encode("utf-8")


def dataframe_to_excel_bytes(df: pd.DataFrame) -> bytes:
    """Serialize a dataframe into an in-memory Excel file for download buttons."""
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="cleaned_data")
    return buffer.getvalue()
