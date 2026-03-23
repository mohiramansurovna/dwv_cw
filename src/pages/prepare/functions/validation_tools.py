from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data.functions.profile import infer_column_groups
from src.data.functions.transforms import (
    validate_allowed_categories,
    validate_non_null,
    validate_numeric_range,
)
from src.pages.prepare.functions.actions import render_validation_result, set_validation_result


def render_validation_tab(df: pd.DataFrame) -> None:
    """Render the dataset rule checks and surface any violating rows."""
    range_panel, category_panel, non_null_panel = st.tabs(
        ["Numeric Range", "Allowed Categories", "Non-null Constraints"]
    )

    with range_panel:
        numeric_columns = infer_column_groups(df)["numeric"]
        if not numeric_columns:
            st.info("No numeric columns are available.")
        else:
            column = st.selectbox("Numeric column", options=numeric_columns, key="validation-range-col")
            series = pd.to_numeric(df[column], errors="coerce").dropna()
            min_default = float(series.min()) if not series.empty else 0.0
            max_default = float(series.max()) if not series.empty else 0.0
            min_value = st.number_input("Minimum allowed value", value=min_default)
            max_value = st.number_input("Maximum allowed value", value=max_default)
            if st.button("Run range validation"):
                violations = validate_numeric_range(df, column, min_value=min_value, max_value=max_value)
                set_validation_result(f"Range validation: {column}", violations)

    with category_panel:
        categorical_columns = infer_column_groups(df)["categorical"]
        if not categorical_columns:
            st.info("No categorical columns are available.")
        else:
            column = st.selectbox("Categorical column", options=categorical_columns, key="validation-cat-col")
            allowed_text = st.text_area(
                "Allowed values (comma-separated)",
                placeholder="North, South, East, West",
            )
            if st.button("Run category validation"):
                allowed_values = [item.strip() for item in allowed_text.split(",") if item.strip()]
                violations = validate_allowed_categories(df, column, allowed_values) if allowed_values else pd.DataFrame()
                set_validation_result(f"Allowed categories validation: {column}", violations)

    with non_null_panel:
        columns = st.multiselect("Columns that must not be null", options=df.columns.tolist())
        if st.button("Run non-null validation", disabled=not columns):
            violations = validate_non_null(df, columns)
            set_validation_result("Non-null validation", violations)

    render_validation_result()
