from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st


def infer_column_groups(df: pd.DataFrame) -> dict[str, list[str]]:
    return {
        "numeric": df.select_dtypes(include=np.number).columns.tolist(),
        "categorical": df.select_dtypes(
            include=["object", "category", "string", "bool"]
        ).columns.tolist(),
        "datetime": df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns.tolist(),
    }


@st.cache_data(show_spinner=False)
def profile_dataframe(df: pd.DataFrame) -> dict[str, pd.DataFrame | int]:
    groups = infer_column_groups(df)

    dtypes_df = (
        pd.DataFrame(
            {
                "column": df.columns,
                "dtype": [str(dtype) for dtype in df.dtypes],
                "non_null": df.notna().sum().tolist(),
                "nulls": df.isna().sum().tolist(),
                "unique_values": df.nunique(dropna=False).tolist(),
            }
        )
        .sort_values("column")
        .reset_index(drop=True)
    )

    missing_df = (
        pd.DataFrame(
            {
                "column": df.columns,
                "missing_count": df.isna().sum().tolist(),
                "missing_pct": ((df.isna().mean() * 100).round(2)).tolist(),
            }
        )
        .sort_values(["missing_count", "column"], ascending=[False, True])
        .reset_index(drop=True)
    )

    numeric_summary = (
        df[groups["numeric"]].describe().transpose().reset_index().rename(columns={"index": "column"})
        if groups["numeric"]
        else pd.DataFrame(columns=["column"])
    )

    categorical_rows: list[dict[str, object]] = []
    for column in groups["categorical"]:
        series = df[column]
        modes = series.mode(dropna=True)
        top_value = modes.iloc[0] if not modes.empty else None
        top_count = int(series.eq(top_value).sum()) if top_value is not None else 0
        categorical_rows.append(
            {
                "column": column,
                "unique_values": int(series.nunique(dropna=True)),
                "top_value": top_value,
                "top_count": top_count,
                "missing_count": int(series.isna().sum()),
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
                "column": column,
                "outlier_count": int(mask.sum()),
                "outlier_pct": round(float(mask.mean() * 100), 2),
                "lower_bound": round(float(lower), 4),
                "upper_bound": round(float(upper), 4),
            }
        )

    return {
        "dtypes": dtypes_df,
        "missing": missing_df,
        "numeric_summary": numeric_summary.round(4),
        "categorical_summary": categorical_summary,
        "duplicates_count": int(df.duplicated().sum()),
        "outlier_summary": pd.DataFrame(outlier_rows),
    }
