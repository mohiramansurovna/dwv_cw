from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data.functions.profile import infer_column_groups, profile_dataframe
from src.data.functions.store import apply_step, get_current_data
from src.data.functions.transforms import (
    apply_category_mapping,
    bin_numeric_column,
    cap_outliers,
    convert_column_type,
    create_formula_column,
    dataframe_to_csv_bytes,
    detect_duplicates,
    drop_columns,
    drop_columns_by_missing_threshold,
    drop_rows_with_missing,
    fill_missing_values,
    group_rare_categories,
    one_hot_encode,
    remove_duplicates,
    remove_outlier_rows,
    rename_column,
    scale_numeric,
    standardize_text,
    summarize_outliers,
    validate_allowed_categories,
    validate_non_null,
    validate_numeric_range,
)
from src.data.ui import render_workspace_panel


VALIDATION_RESULT_KEY = "validation_result"
VALIDATION_TITLE_KEY = "validation_title"


def _apply_and_rerun(
    new_df: pd.DataFrame,
    operation: str,
    parameters: dict,
    affected_columns: list[str],
    preview: dict,
) -> None:
    apply_step(
        new_df,
        operation=operation,
        parameters=parameters,
        affected_columns=affected_columns,
        preview=preview,
    )
    st.success(f"{operation} applied.")
    st.rerun()


def _set_validation_result(title: str, violations: pd.DataFrame) -> None:
    st.session_state[VALIDATION_TITLE_KEY] = title
    st.session_state[VALIDATION_RESULT_KEY] = violations


def _render_validation_result() -> None:
    violations = st.session_state.get(VALIDATION_RESULT_KEY)
    title = st.session_state.get(VALIDATION_TITLE_KEY, "Validation result")
    if violations is None:
        return

    st.divider()
    st.subheader(title)
    if violations.empty:
        st.success("No violations found.")
        return

    st.warning(f"{len(violations)} violation(s) found.")
    st.dataframe(violations, use_container_width=True, hide_index=True)
    st.download_button(
        "Download violations CSV",
        data=dataframe_to_csv_bytes(violations),
        file_name="validation_violations.csv",
        mime="text/csv",
        use_container_width=True,
    )


def _render_missing_values_tab(df: pd.DataFrame) -> None:
    profile = profile_dataframe(df)
    missing_df = profile["missing"]
    st.dataframe(missing_df, use_container_width=True, hide_index=True)

    missing_columns = missing_df.loc[missing_df["missing_count"] > 0, "column"].tolist()

    with st.expander("Drop rows with missing values", expanded=False):
        selected_columns = st.multiselect(
            "Columns to inspect for nulls",
            options=df.columns.tolist(),
            default=missing_columns[:3],
            key="missing-drop-cols",
        )
        rows_to_remove = int(df[selected_columns].isna().any(axis=1).sum()) if selected_columns else 0
        st.caption(f"Preview: {rows_to_remove} row(s) would be removed.")
        if st.button("Apply row drop", key="apply-drop-missing", disabled=not selected_columns):
            new_df = drop_rows_with_missing(df, selected_columns)
            _apply_and_rerun(
                new_df,
                operation="Drop rows with missing values",
                parameters={"columns": selected_columns},
                affected_columns=selected_columns,
                preview={"rows_removed": rows_to_remove},
            )

    with st.expander("Drop columns by missing-value threshold", expanded=False):
        threshold_pct = st.slider("Threshold (%)", 0, 100, 40, key="missing-threshold")
        _, columns_to_drop = drop_columns_by_missing_threshold(df, float(threshold_pct))
        st.caption(
            "Preview: "
            + (", ".join(columns_to_drop) if columns_to_drop else "no columns would be removed.")
        )
        if st.button("Apply column drop", key="apply-drop-columns-threshold"):
            new_df, columns_dropped = drop_columns_by_missing_threshold(df, float(threshold_pct))
            _apply_and_rerun(
                new_df,
                operation="Drop columns by missing threshold",
                parameters={"threshold_pct": threshold_pct},
                affected_columns=columns_dropped,
                preview={"columns_removed": columns_dropped},
            )

    with st.expander("Fill missing values", expanded=True):
        selected_columns = st.multiselect(
            "Columns to fill",
            options=missing_columns,
            default=missing_columns[:2],
            key="missing-fill-cols",
        )
        strategy = st.selectbox(
            "Strategy",
            options=[
                "constant",
                "mean",
                "median",
                "mode",
                "most_frequent",
                "ffill",
                "bfill",
            ],
            key="missing-strategy",
        )
        constant_value = None
        if strategy == "constant":
            constant_value = st.text_input("Constant value", value="Unknown")
        affected_cells = (
            int(df[selected_columns].isna().sum().sum()) if selected_columns else 0
        )
        st.caption(f"Preview: {affected_cells} missing cell(s) would be targeted.")
        if st.button("Apply fill strategy", key="apply-fill-missing", disabled=not selected_columns):
            try:
                new_df = fill_missing_values(df, selected_columns, strategy, constant_value)
                _apply_and_rerun(
                    new_df,
                    operation="Fill missing values",
                    parameters={"columns": selected_columns, "strategy": strategy, "constant": constant_value},
                    affected_columns=selected_columns,
                    preview={"targeted_cells": affected_cells},
                )
            except Exception as exc:
                st.error(f"Could not fill missing values: {exc}")


def _render_duplicates_tab(df: pd.DataFrame) -> None:
    duplicate_mode = st.radio(
        "Duplicate detection mode",
        options=["full_row", "subset"],
        horizontal=True,
        format_func=lambda item: "Full row" if item == "full_row" else "Subset of columns",
    )
    subset = None
    if duplicate_mode == "subset":
        subset = st.multiselect(
            "Subset columns",
            options=df.columns.tolist(),
            default=df.columns.tolist()[:2],
            key="duplicate-subset-cols",
        )

    duplicate_df = detect_duplicates(df, subset=subset if subset else None)
    st.metric("Duplicate rows detected", f"{duplicate_df.shape[0]:,}")
    if duplicate_df.empty:
        st.info("No duplicates found for the selected criteria.")
    else:
        st.dataframe(duplicate_df.head(100), use_container_width=True)

    keep = st.selectbox("When removing duplicates, keep", options=["first", "last"])
    if st.button(
        "Remove duplicates",
        key="remove-duplicates",
        disabled=duplicate_mode == "subset" and not subset,
    ):
        new_df = remove_duplicates(df, subset=subset if subset else None, keep=keep)
        _apply_and_rerun(
            new_df,
            operation="Remove duplicates",
            parameters={"subset": subset, "keep": keep},
            affected_columns=subset or df.columns.tolist(),
            preview={"rows_removed": int(df.shape[0] - new_df.shape[0])},
        )


def _render_types_tab(df: pd.DataFrame) -> None:
    selected_column = st.selectbox("Column", options=df.columns.tolist(), key="types-column")
    target_type = st.selectbox(
        "Target type",
        options=["numeric", "categorical", "datetime"],
        key="types-target",
    )
    datetime_format = ""
    if target_type == "datetime":
        datetime_format = st.text_input(
            "Datetime format (optional)",
            placeholder="%Y-%m-%d",
        )

    before_nulls = int(df[selected_column].isna().sum())
    st.caption(f"Current dtype: `{df[selected_column].dtype}` | Nulls before conversion: {before_nulls}")

    if st.button("Convert column type", key="convert-type"):
        try:
            new_df = convert_column_type(
                df,
                column=selected_column,
                target_type=target_type,
                datetime_format=datetime_format.strip() or None,
            )
            after_nulls = int(new_df[selected_column].isna().sum())
            _apply_and_rerun(
                new_df,
                operation="Convert column type",
                parameters={"column": selected_column, "target_type": target_type, "datetime_format": datetime_format},
                affected_columns=[selected_column],
                preview={"nulls_before": before_nulls, "nulls_after": after_nulls},
            )
        except Exception as exc:
            st.error(f"Conversion failed: {exc}")


def _render_categorical_tab(df: pd.DataFrame) -> None:
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
            _apply_and_rerun(
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
        mapping = {
            str(row["from"]): str(row["to"])
            for _, row in valid_rows.iterrows()
        }
        st.caption(f"Preview: {len(mapping)} mapped value(s) ready.")
        if st.button("Apply mapping", disabled=not mapping):
            new_df = apply_category_mapping(
                df,
                column=target_column,
                mapping=mapping,
                unmatched_to_other=unmatched_to_other,
            )
            _apply_and_rerun(
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
            _apply_and_rerun(
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
            preview_new_columns = int(
                sum(df[column].nunique(dropna=True) for column in selected_columns)
            )
        st.caption(f"Preview: roughly {preview_new_columns} encoded columns would be created.")
        if st.button("Apply one-hot encoding", disabled=not selected_columns):
            new_df = one_hot_encode(df, selected_columns)
            _apply_and_rerun(
                new_df,
                operation="One-hot encode categories",
                parameters={"columns": selected_columns},
                affected_columns=selected_columns,
                preview={"new_column_count": int(new_df.shape[1] - df.shape[1])},
            )


def _render_numeric_tab(df: pd.DataFrame) -> None:
    numeric_columns = infer_column_groups(df)["numeric"]
    if not numeric_columns:
        st.info("No numeric columns are available.")
        return

    selected_columns = st.multiselect(
        "Numeric columns",
        options=numeric_columns,
        default=numeric_columns[:2],
        key="outlier-cols",
    )
    method = st.selectbox("Detection method", options=["iqr", "zscore"])
    z_threshold = 3.0
    if method == "zscore":
        z_threshold = st.slider("Z-score threshold", 1.0, 5.0, 3.0, 0.1)

    if selected_columns:
        summary_df, _ = summarize_outliers(
            df,
            selected_columns,
            method="iqr" if method == "iqr" else "zscore",
            z_threshold=z_threshold,
        )
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    else:
        summary_df = pd.DataFrame()
        st.info("Choose at least one numeric column.")

    action = st.radio(
        "Action",
        options=["do_nothing", "cap", "remove_rows"],
        horizontal=True,
        format_func=lambda item: {
            "do_nothing": "Do nothing",
            "cap": "Cap / winsorize",
            "remove_rows": "Remove outlier rows",
        }[item],
    )

    if action == "cap" and st.button("Apply capping", disabled=not selected_columns):
        new_df, impact = cap_outliers(
            df,
            selected_columns,
            method="iqr" if method == "iqr" else "zscore",
            z_threshold=z_threshold,
        )
        _apply_and_rerun(
            new_df,
            operation="Cap outliers",
            parameters={"columns": selected_columns, "method": method, "z_threshold": z_threshold},
            affected_columns=selected_columns,
            preview={"values_capped": impact},
        )

    if action == "remove_rows" and st.button("Remove outlier rows", disabled=not selected_columns):
        new_df, removed_count = remove_outlier_rows(
            df,
            selected_columns,
            method="iqr" if method == "iqr" else "zscore",
            z_threshold=z_threshold,
        )
        _apply_and_rerun(
            new_df,
            operation="Remove outlier rows",
            parameters={"columns": selected_columns, "method": method, "z_threshold": z_threshold},
            affected_columns=selected_columns,
            preview={"rows_removed": removed_count},
        )


def _render_scaling_tab(df: pd.DataFrame) -> None:
    numeric_columns = infer_column_groups(df)["numeric"]
    if not numeric_columns:
        st.info("No numeric columns are available for scaling.")
        return

    selected_columns = st.multiselect(
        "Columns to scale",
        options=numeric_columns,
        default=numeric_columns[:2],
        key="scale-cols",
    )
    method = st.selectbox(
        "Scaling method",
        options=["min_max", "z_score"],
        format_func=lambda item: "Min-max" if item == "min_max" else "Z-score",
    )

    if selected_columns:
        before_stats = df[selected_columns].describe().transpose()[["mean", "std", "min", "max"]]
        st.caption("Before scaling")
        st.dataframe(before_stats.round(4), use_container_width=True)

    if st.button("Apply scaling", disabled=not selected_columns):
        try:
            new_df = scale_numeric(df, selected_columns, method)
            after_stats = new_df[selected_columns].describe().transpose()[["mean", "std", "min", "max"]]
            _apply_and_rerun(
                new_df,
                operation="Scale numeric columns",
                parameters={"columns": selected_columns, "method": method},
                affected_columns=selected_columns,
                preview={"after_stats": after_stats.round(4).to_dict()},
            )
        except Exception as exc:
            st.error(f"Scaling failed: {exc}")


def _render_columns_tab(df: pd.DataFrame) -> None:
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
                _apply_and_rerun(
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
            _apply_and_rerun(
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
                _apply_and_rerun(
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
                    _apply_and_rerun(
                        new_df,
                        operation="Bin numeric column",
                        parameters={"source_column": source_column, "new_column": new_column.strip(), "bins": bins, "method": method},
                        affected_columns=[source_column, new_column.strip()],
                        preview={"bins": bins},
                    )
                except Exception as exc:
                    st.error(f"Binning failed: {exc}")


def _render_validation_tab(df: pd.DataFrame) -> None:
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
                _set_validation_result(f"Range validation: {column}", violations)

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
                _set_validation_result(f"Allowed categories validation: {column}", violations)

    with non_null_panel:
        columns = st.multiselect("Columns that must not be null", options=df.columns.tolist())
        if st.button("Run non-null validation", disabled=not columns):
            violations = validate_non_null(df, columns)
            _set_validation_result("Non-null validation", violations)

    _render_validation_result()


def render_prepare_page() -> None:
    left, right = st.columns([3.2, 1.2])
    df = get_current_data()

    with left:
        st.title("Cleaning & Preparation Studio")

        if df is None:
            st.info("Load a dataset on the Upload page to start cleaning.")
        else:
            st.caption("Apply transformations to the working copy. Each successful step is recorded and can be undone.")
            st.dataframe(df.head(20), use_container_width=True)

            tabs = st.tabs(
                [
                    "Missing Values",
                    "Duplicates",
                    "Types & Parsing",
                    "Categorical Tools",
                    "Numeric Cleaning",
                    "Scaling",
                    "Column Operations",
                    "Validation Rules",
                ]
            )

            with tabs[0]:
                _render_missing_values_tab(df)
            with tabs[1]:
                _render_duplicates_tab(df)
            with tabs[2]:
                _render_types_tab(df)
            with tabs[3]:
                _render_categorical_tab(df)
            with tabs[4]:
                _render_numeric_tab(df)
            with tabs[5]:
                _render_scaling_tab(df)
            with tabs[6]:
                _render_columns_tab(df)
            with tabs[7]:
                _render_validation_tab(df)

    with right:
        render_workspace_panel()
