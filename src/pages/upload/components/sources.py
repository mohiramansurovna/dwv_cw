from __future__ import annotations

import streamlit as st

from src.data.store import set_store
from src.pages.upload.components.datasets import (
    SAMPLE_DATASETS,
    load_sample_into_session,
    load_uploaded_bytes,
)


def render_source_tabs() -> None:
    upload_tab, sample_tab = st.tabs(["File Upload", "Sample Data"])

    with upload_tab:
        render_upload_tab()

    with sample_tab:
        render_sample_data_tab()


def render_upload_tab() -> None:
    uploaded_file = st.file_uploader(
        "Upload a dataset",
        type=["csv", "xlsx", "xls", "json"],
    )

    if uploaded_file is not None and st.button("Load uploaded file", type="primary"):
        extension = uploaded_file.name.split(".")[-1].lower()

        try:
            df = load_uploaded_bytes(uploaded_file.getvalue(), extension)
            set_store(df, uploaded_file.name, "upload")
            st.success("Dataset loaded into the working session.")
            st.rerun()
        except Exception as exc:
            st.error(f"Could not load this file: {exc}")


def render_sample_data_tab() -> None:
    for sample_name in SAMPLE_DATASETS:
        with st.container(border=True, height=100, gap=None):
            col1, col2, col3 = st.columns([0.6, 5, 1])

            with col1:
                st.markdown("## :material/database:")

            with col2:
                st.write(f"**{sample_name}**")
                st.caption("Sample dataset")

            with col3:
                if st.button(
                    "Load",
                    key=f"sample-{sample_name}",
                    type="secondary",
                ):
                    load_sample_into_session(sample_name)