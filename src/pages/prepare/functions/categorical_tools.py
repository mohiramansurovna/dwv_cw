from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data.functions.profile import infer_column_groups
from src.data.functions.transforms import (
    apply_category_mapping,
    group_rare_categories,
    one_hot_encode,
    standardize_text,
)
from src.pages.prepare.functions.actions import apply_and_rerun


def render_categorical_tab(df: pd.DataFrame) -> None:
    """Render text cleanup, mapping, rare grouping, and one-hot encoding tools."""
    groups = infer_column_groups(df)
    categorical_columns = groups["categorical"]

    if not categorical_columns:
        st.info("No categorical columns are currently available.")
        return

    with st.expander("Value standardization", expanded=True):
        selected_columns = st.multiselect(
            "Columns",
            options=categorical_columns,
            default=categorical_columns[:2],
            key="cat-standardize-cols",
        )
        trim = st.checkbox("Trim whitespace", value=True)
        case_style = st.selectbox("Case style", options=["unchanged", "lower", "upper", "title"])
        if st.button("Apply standardization", disabled=not selected_columns):
            new_df = standardize_text(
                df,
                columns=selected_columns,
                trim_whitespace=trim,
                case_style=case_style,
            )
            apply_and_rerun(
                new_df,
                operation="Standardize categorical values",
                parameters={"columns": selected_columns, "trim": trim, "case_style": case_style},
                affected_columns=selected_columns,
                preview={"columns_updated": selected_columns},
            )

    with st.expander("Mapping / replacement", expanded=False):
        target_column = st.selectbox("Column to map", options=categorical_columns, key="mapping-column")
        editor_df = st.data_editor(
            pd.DataFrame({"from": [""], "to": [""]}),
            num_rows="dynamic",
            use_container_width=True,
            key="mapping-editor",
        )
        unmatched_to_other = st.checkbox("Set unmatched values to Other", value=False)
        valid_rows = editor_df[(editor_df["from"].astype(str).str.strip() != "")]
        mapping = {str(row["from"]): str(row["to"]) for _, row in valid_rows.iterrows()}
        st.caption(f"Preview: {len(mapping)} mapped value(s) ready.")
        if st.button("Apply mapping", disabled=not mapping):
            new_df = apply_category_mapping(
                df,
                column=target_column,
                mapping=mapping,
                unmatched_to_other=unmatched_to_other,
            )
            apply_and_rerun(
                new_df,
                operation="Map categorical values",
                parameters={"column": target_column, "mapping": mapping, "unmatched_to_other": unmatched_to_other},
                affected_columns=[target_column],
                preview={"mapped_values": len(mapping)},
            )

    with st.expander("Rare category grouping", expanded=False):
        target_column = st.selectbox("Column", options=categorical_columns, key="rare-column")
        threshold_pct = st.slider("Frequency threshold (%)", 0.1, 15.0, 2.0, 0.1)
        _, rare_categories = group_rare_categories(df, target_column, threshold_pct)
        st.caption(
            "Preview: "
            + (", ".join(map(str, rare_categories[:10])) if rare_categories else "no rare categories found.")
        )
        if st.button("Group rare categories"):
            new_df, rare_categories = group_rare_categories(df, target_column, threshold_pct)
            apply_and_rerun(
                new_df,
                operation="Group rare categories",
                parameters={"column": target_column, "threshold_pct": threshold_pct},
                affected_columns=[target_column],
                preview={"grouped_categories": rare_categories},
            )

    with st.expander("One-hot encoding", expanded=False):
        selected_columns = st.multiselect(
            "Columns to encode",
            options=categorical_columns,
            key="one-hot-cols",
        )
        preview_new_columns = 0
        if selected_columns:
            preview_new_columns = int(sum(df[column].nunique(dropna=True) for column in selected_columns))
        st.caption(f"Preview: roughly {preview_new_columns} encoded columns would be created.")
        if st.button("Apply one-hot encoding", disabled=not selected_columns):
            new_df = one_hot_encode(df, selected_columns)
            apply_and_rerun(
                new_df,
                operation="One-hot encode categories",
                parameters={"columns": selected_columns},
                affected_columns=selected_columns,
                preview={"new_column_count": int(new_df.shape[1] - df.shape[1])},
            )
