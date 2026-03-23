from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from src.data.functions.store import set_data


PROJECT_ROOT = Path(__file__).resolve().parents[4]
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


def load_sample_into_session(name: str) -> None:
    df = load_sample_dataset(str(SAMPLE_DATASETS[name]))
    set_data(df, source_name=name, source_kind="sample")
    st.success(f"Loaded sample dataset: {name}")
    st.rerun()
