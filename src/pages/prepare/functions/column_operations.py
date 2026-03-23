from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data.functions.profile import infer_column_groups
from src.data.functions.transforms import (
    bin_numeric_column,
    create_formula_column,
    drop_columns,
    rename_column,
)
from src.pages.prepare.functions.actions import apply_and_rerun


def render_columns_tab(df: pd.DataFrame) -> None:
    """Render rename, drop, formula, and binning column operations."""
    rename_panel, drop_panel, formula_panel, bin_panel = st.tabs(
        ["Rename", "Drop", "Formula Column", "Binning"]
    )

    with rename_panel:
        old_name = st.selectbox("Column to rename", options=df.columns.tolist(), key="rename-old")
        new_name = st.text_input("New column name", key="rename-new")
        if st.button("Apply rename", disabled=not new_name.strip()):
            if new_name in df.columns:
                st.error("Choose a new name that does not already exist.")
            else:
                new_df = rename_column(df, old_name, new_name.strip())
                apply_and_rerun(
                    new_df,
                    operation="Rename column",
                    parameters={"old_name": old_name, "new_name": new_name.strip()},
                    affected_columns=[old_name],
                    preview={"renamed_to": new_name.strip()},
                )

    with drop_panel:
        selected_columns = st.multiselect("Columns to drop", options=df.columns.tolist(), key="drop-cols")
        st.caption(f"Preview: {len(selected_columns)} column(s) would be removed.")
        if st.button("Apply column drop", disabled=not selected_columns, key="apply-drop-cols"):
            new_df = drop_columns(df, selected_columns)
            apply_and_rerun(
                new_df,
                operation="Drop columns",
                parameters={"columns": selected_columns},
                affected_columns=selected_columns,
                preview={"columns_removed": selected_columns},
            )

    with formula_panel:
        new_column = st.text_input("New column name", key="formula-new-column")
        formula = st.text_input(
            "Formula",
            placeholder="sales / units or log(revenue) or profit - profit.mean()",
            key="formula-expression",
        )
        st.caption(
            "Tip: use existing column names directly when they are simple identifiers. "
            "If not, use col('Column Name')."
        )
        if formula.strip():
            try:
                preview_df = create_formula_column(df.head(10).copy(), new_column or "preview_column", formula)
                st.dataframe(preview_df.tail(10), use_container_width=True)
            except Exception as exc:
                st.warning(f"Preview unavailable: {exc}")
        if st.button("Create formula column", disabled=not new_column.strip() or not formula.strip()):
            try:
                new_df = create_formula_column(df, new_column.strip(), formula.strip())
                apply_and_rerun(
                    new_df,
                    operation="Create formula column",
                    parameters={"new_column": new_column.strip(), "formula": formula.strip()},
                    affected_columns=[new_column.strip()],
                    preview={"new_column": new_column.strip()},
                )
            except Exception as exc:
                st.error(f"Formula evaluation failed: {exc}")

    with bin_panel:
        numeric_columns = infer_column_groups(df)["numeric"]
        if not numeric_columns:
            st.info("No numeric columns are available for binning.")
        else:
            source_column = st.selectbox("Source numeric column", options=numeric_columns, key="bin-source")
            new_column = st.text_input("New binned column name", value=f"{source_column}_bin")
            bins = st.slider("Number of bins", 2, 10, 4)
            method = st.selectbox(
                "Binning method",
                options=["equal_width", "quantile"],
                format_func=lambda item: "Equal width" if item == "equal_width" else "Quantile",
            )
            if st.button("Apply binning", disabled=not new_column.strip()):
                try:
                    new_df = bin_numeric_column(df, source_column, new_column.strip(), bins, method)
                    apply_and_rerun(
                        new_df,
                        operation="Bin numeric column",
                        parameters={"source_column": source_column, "new_column": new_column.strip(), "bins": bins, "method": method},
                        affected_columns=[source_column, new_column.strip()],
                        preview={"bins": bins},
                    )
                except Exception as exc:
                    st.error(f"Binning failed: {exc}")
