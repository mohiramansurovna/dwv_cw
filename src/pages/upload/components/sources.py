from __future__ import annotations

import streamlit as st

from src.data.functions.store import set_data
from src.pages.upload.components.datasets import (
    SAMPLE_DATASETS,
    load_sample_into_session,
    load_uploaded_bytes,
)


def render_source_tabs() -> None:
    """Render the file-upload, and sample-data source controls."""
    upload_tab, sample_tab = st.tabs(["File Upload","Sample Data"])

    with upload_tab:
        render_upload_tab()

    with sample_tab:
        render_sample_data_tab()


def render_upload_tab() -> None:
    """Render the local file upload controls."""
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


def render_sample_data_tab() -> None:
    """Render buttons for the bundled sample datasets."""
    for sample_name in SAMPLE_DATASETS:
        sample_col, action_col = st.columns([4, 1])
        sample_col.write(sample_name)
        if action_col.button("Load", key=f"sample-{sample_name}"):
            load_sample_into_session(sample_name)
