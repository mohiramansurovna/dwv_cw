from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from src.data.functions.profile import infer_column_groups, profile_dataframe
from src.data.functions.store import get_current_data, set_data
from src.data.ui import render_workspace_panel


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SAMPLE_DATASETS = {
    "Retail Orders": PROJECT_ROOT / "sample_data" / "retail_orders_sample.csv",
    "HR Analytics": PROJECT_ROOT / "sample_data" / "hr_analytics_sample.csv",
}


@st.cache_data(show_spinner=False)
def load_uploaded_bytes(file_bytes: bytes, extension: str) -> pd.DataFrame:
    buffer = BytesIO(file_bytes)
    if extension == "csv":
        return pd.read_csv(buffer)
    if extension in {"xlsx", "xls"}:
        return pd.read_excel(buffer)
    if extension == "json":
        return pd.read_json(buffer)
    raise ValueError("Unsupported file type.")


@st.cache_data(show_spinner=False)
def load_sample_dataset(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def _normalize_google_sheet_url(url: str) -> str:
    if "docs.google.com/spreadsheets" not in url:
        return url
    if "/export?" in url:
        return url
    base = url.split("/edit")[0]
    gid = "0"
    if "gid=" in url:
        gid = url.split("gid=")[-1].split("&")[0]
    return f"{base}/export?format=csv&gid={gid}"


@st.cache_data(show_spinner=False)
def load_google_sheet(url: str) -> pd.DataFrame:
    return pd.read_csv(_normalize_google_sheet_url(url))


def _load_sample(name: str) -> None:
    df = load_sample_dataset(str(SAMPLE_DATASETS[name]))
    set_data(df, source_name=name, source_kind="sample")
    st.success(f"Loaded sample dataset: {name}")
    st.rerun()


def _render_overview(df: pd.DataFrame) -> None:
    profile = profile_dataframe(df)
    groups = infer_column_groups(df)
    missing_cells = int(df.isna().sum().sum())

    metric_cols = st.columns(5)
    metric_cols[0].metric("Rows", f"{df.shape[0]:,}")
    metric_cols[1].metric("Columns", df.shape[1])
    metric_cols[2].metric("Numeric", len(groups["numeric"]))
    metric_cols[3].metric("Categorical", len(groups["categorical"]))
    metric_cols[4].metric("Missing cells", f"{missing_cells:,}")

    duplicates_col, outliers_col = st.columns(2)
    duplicates_col.metric("Duplicate rows", f"{profile['duplicates_count']:,}")
    outlier_total = (
        int(profile["outlier_summary"]["outlier_count"].sum())
        if not profile["outlier_summary"].empty
        else 0
    )
    outliers_col.metric("Potential outliers", f"{outlier_total:,}")

    if df.shape[0] < 1000 or df.shape[1] < 8:
        st.warning("This dataset is smaller than the project target of 1,000 rows and 8 columns.")

    tabs = st.tabs(
        [
            "Preview",
            "Columns & Types",
            "Summary Stats",
            "Missingness",
            "Outliers",
        ]
    )

    with tabs[0]:
        st.dataframe(df.head(50), use_container_width=True)

    with tabs[1]:
        st.dataframe(profile["dtypes"], use_container_width=True, hide_index=True)

    with tabs[2]:
        left, right = st.columns(2)
        with left:
            st.caption("Numeric summary")
            if profile["numeric_summary"].empty:
                st.info("No numeric columns found.")
            else:
                st.dataframe(profile["numeric_summary"], use_container_width=True, hide_index=True)
        with right:
            st.caption("Categorical summary")
            if profile["categorical_summary"].empty:
                st.info("No categorical columns found.")
            else:
                st.dataframe(
                    profile["categorical_summary"],
                    use_container_width=True,
                    hide_index=True,
                )

    with tabs[3]:
        st.dataframe(profile["missing"], use_container_width=True, hide_index=True)

    with tabs[4]:
        if profile["outlier_summary"].empty:
            st.info("No numeric columns available for outlier profiling.")
        else:
            st.dataframe(profile["outlier_summary"], use_container_width=True, hide_index=True)


def render_upload_page() -> None:
    left, right = st.columns([3.2, 1.2])

    with left:
        st.title("Upload & Overview")
        st.caption(
            "Load a CSV, Excel, JSON file, a public Google Sheet, or one of the bundled sample datasets."
        )

        upload_tab, sheets_tab, sample_tab = st.tabs(["File Upload", "Google Sheets", "Sample Data"])

        with upload_tab:
            uploaded_file = st.file_uploader(
                "Upload a dataset",
                type=["csv", "xlsx", "xls", "json"],
            )
            if uploaded_file is not None and st.button("Load uploaded file", type="primary"):
                extension = uploaded_file.name.split(".")[-1].lower()
                try:
                    df = load_uploaded_bytes(uploaded_file.getvalue(), extension)
                    set_data(df, source_name=uploaded_file.name, source_kind="upload")
                    st.success("Dataset loaded into the working session.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not load this file: {exc}")

        with sheets_tab:
            sheets_url = st.text_input(
                "Public Google Sheet URL",
                placeholder="https://docs.google.com/spreadsheets/d/.../edit#gid=0",
            )
            if st.button("Load Google Sheet"):
                if not sheets_url.strip():
                    st.warning("Paste a Google Sheet URL first.")
                else:
                    try:
                        df = load_google_sheet(sheets_url.strip())
                        set_data(df, source_name="Google Sheet", source_kind="sheets")
                        st.success("Google Sheet loaded successfully.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Could not read the sheet. Make sure it is public. Details: {exc}")

        with sample_tab:
            st.write("Included sample datasets")
            for sample_name in SAMPLE_DATASETS:
                sample_col, action_col = st.columns([4, 1])
                sample_col.write(sample_name)
                if action_col.button("Load", key=f"sample-{sample_name}"):
                    _load_sample(sample_name)

        df = get_current_data()
        if df is None:
            st.info("Load a dataset to unlock profiling, cleaning, visualization, and export.")
        else:
            st.divider()
            _render_overview(df)

    with right:
        render_workspace_panel()
