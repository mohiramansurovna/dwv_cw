from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st


def infer_column_groups(df: pd.DataFrame) -> dict[str, list[str]]:
    """Split columns into numeric, categorical, and datetime groups for the UI."""
    return {
        "numeric": df.select_dtypes(include=np.number).columns.tolist(),
        "categorical": df.select_dtypes(
            include=["object", "category", "string", "bool"]
        ).columns.tolist(),
        "datetime": df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns.tolist(),
    }


@st.cache_data(show_spinner=False)
def profile_dataframe(df: pd.DataFrame) -> dict[str, pd.DataFrame | int]:
    """Compute reusable profiling tables shown in the upload page."""
    groups = infer_column_groups(df)

    dtypes_df = (
        pd.DataFrame(
            {
                "Column": df.columns,
                "Type": [str(dtype) for dtype in df.dtypes],
                "Missing": df.isna().sum().tolist(),
                "Missing (%)": (df.isna().mean() * 100).round(2).tolist(),
                "Unique": df.nunique(dropna=False).tolist(),
            }
        )
        .sort_values("Column")
        .reset_index(drop=True)
    )

    missing_df = (
        pd.DataFrame(
            {
                "Column": df.columns,
                "Missing": df.isna().sum().tolist(),
                "Missing (%)": (df.isna().mean() * 100).round(2).tolist(),
            }
        )
        .sort_values(["Missing", "Column"], ascending=[False, True])
        .reset_index(drop=True)
    )

    numeric_summary = (
        df[groups["numeric"]]
        .describe()
        .transpose()
        .reset_index()
        .rename(columns={"index": "Column"})
        if groups["numeric"]
        else pd.DataFrame(columns=["Column"])
    )

    categorical_rows: list[dict[str, object]] = []
    for column in groups["categorical"]:
        series = df[column]
        modes = series.mode(dropna=True)
        top_value = modes.iloc[0] if not modes.empty else None
        top_count = int(series.eq(top_value).sum()) if top_value is not None else 0

        categorical_rows.append(
            {
                "Column": column,
                "Unique": int(series.nunique(dropna=True)),
                "Top Value": top_value,
                "Top Count": top_count,
                "Missing": int(series.isna().sum()),
            }
        )

    categorical_summary = pd.DataFrame(categorical_rows)

    outlier_rows: list[dict[str, object]] = []
    for column in groups["numeric"]:
        series = pd.to_numeric(df[column], errors="coerce").dropna()
        if series.empty:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        mask = (series < lower) | (series > upper)

        outlier_rows.append(
            {
                "Column": column,
                "Outliers": int(mask.sum()),
                "Outliers (%)": round(float(mask.mean() * 100), 2),
                "Min Bound": round(float(lower), 4),
                "Max Bound": round(float(upper), 4),
            }
        )

    outlier_summary = pd.DataFrame(outlier_rows)
    if not outlier_summary.empty:
        outlier_summary = outlier_summary.sort_values("Column").reset_index(drop=True)

    if not categorical_summary.empty:
        categorical_summary = categorical_summary.sort_values("Column").reset_index(drop=True)

    return {
        "dtypes": dtypes_df,
        "missing": missing_df,
        "numeric_summary": numeric_summary.round(4),
        "categorical_summary": categorical_summary,
        "duplicates_count": int(df.duplicated().sum()),
        "outlier_summary": outlier_summary,
    }