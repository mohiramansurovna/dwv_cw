from __future__ import annotations

from typing import Any, TypedDict

from datetime import datetime
import pandas as pd  # pyright: ignore[reportMissingModuleSource]
import streamlit as st  # pyright: ignore[reportMissingImports]
from src.data.utils import make_json_safe

STORE_KEY = "dwv_data_store"


class DataStore(TypedDict):
    source_name: str | None
    source_kind: str | None
    original_df: pd.DataFrame | None
    current_df: pd.DataFrame | None
    snapshots: list[pd.DataFrame]
    transform_log: list[dict[str, Any]]


def get_store() -> DataStore:
    if STORE_KEY not in st.session_state:
        set_store(None, None, None)
    return st.session_state[STORE_KEY]


def set_store(
    df: pd.DataFrame | None,
    source_name: str | None,
    source_kind: str | None,
) -> None:
    st.session_state[STORE_KEY] = {
        "source_name": source_name,
        "source_kind": source_kind,
        "original_df": df.copy() if df is not None else None,
        "current_df": df.copy() if df is not None else None,
        "snapshots": [],
        "transform_log": [],
    }

def commit_transformation(
    new_df: pd.DataFrame,
    operation: str,
    parameters: dict[str, Any] | None = None,
    affected_columns: list[str] | None = None,
    preview: dict[str, Any] | None = None,
) -> None:
    store = get_store()
    current_df = store["current_df"]

    if current_df is not None:
        store["snapshots"].append(current_df.copy())

    store["current_df"] = new_df.copy()
    store["transform_log"].append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operation": operation,
            "parameters": make_json_safe(parameters or {}),
            "affected_columns": affected_columns or [],
            "shape_before": list(current_df.shape) if current_df is not None else None,
            "shape_after": list(new_df.shape),
            "preview": make_json_safe(preview or {}),
        }
    )
