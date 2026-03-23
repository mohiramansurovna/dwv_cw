from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st


STORE_KEY = "dwv_store"


def _make_json_safe(value: Any) -> Any:
    """Convert pandas/numpy values into plain Python types for logs and exports."""
    if isinstance(value, dict):
        return {str(key): _make_json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_make_json_safe(item) for item in value]
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, (pd.Series, pd.Index)):
        return [_make_json_safe(item) for item in value.tolist()]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            return str(value)
    return value


def _empty_store() -> dict[str, Any]:
    """Build the initial session-store shape used by the whole app."""
    return {
        "source_name": None,
        "source_kind": None,
        "original_df": None,
        "current_df": None,
        "snapshots": [],
        "transform_log": [],
    }


def init_store() -> None:
    """Create the Streamlit session store the first time the app runs."""
    if STORE_KEY not in st.session_state:
        st.session_state[STORE_KEY] = _empty_store()


def get_store() -> dict[str, Any]:
    """Return the shared session store, creating it first when needed."""
    init_store()
    return st.session_state[STORE_KEY]


def clear_session() -> None:
    """Drop all session state so the app starts from a clean slate."""
    st.session_state.clear()


def has_data() -> bool:
    """Check whether a working dataframe is currently loaded."""
    return get_store()["current_df"] is not None


def set_data(
    df: pd.DataFrame,
    source_name: str | None = None,
    source_kind: str | None = None,
) -> None:
    """Load a new dataset and reset history, saved charts, and validation outputs."""
    store = get_store()
    store["source_name"] = source_name
    store["source_kind"] = source_kind
    store["original_df"] = df.copy()
    store["current_df"] = df.copy()
    store["snapshots"] = []
    store["transform_log"] = []
    for key in ["validation_result", "validation_title", "saved_charts"]:
        st.session_state.pop(key, None)


def get_current_data() -> pd.DataFrame | None:
    """Return a copy of the editable working dataframe."""
    df = get_store()["current_df"]
    return df.copy() if df is not None else None


def get_original_data() -> pd.DataFrame | None:
    """Return a copy of the untouched dataset that was first loaded."""
    df = get_store()["original_df"]
    return df.copy() if df is not None else None


def get_transform_log() -> list[dict[str, Any]]:
    """Return a safe copy of the transformation history for UI and export use."""
    return deepcopy(get_store()["transform_log"])


def get_source_name() -> str | None:
    """Expose the human-readable dataset source shown in the workspace panel."""
    return get_store()["source_name"]


def apply_step(
    new_df: pd.DataFrame,
    operation: str,
    parameters: dict[str, Any] | None = None,
    affected_columns: list[str] | None = None,
    preview: dict[str, Any] | None = None,
) -> None:
    """Commit a transformation, save an undo snapshot, and append a log entry."""
    store = get_store()
    current_df = store["current_df"]

    if current_df is not None:
        store["snapshots"].append(current_df.copy())

    store["current_df"] = new_df.copy()
    store["transform_log"].append(
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operation": operation,
            "parameters": _make_json_safe(parameters or {}),
            "affected_columns": affected_columns or [],
            "shape_before": list(current_df.shape) if current_df is not None else None,
            "shape_after": list(new_df.shape),
            "preview": _make_json_safe(preview or {}),
        }
    )


def undo_last_step() -> bool:
    """Restore the previous dataframe snapshot and remove the last log entry."""
    store = get_store()
    if not store["snapshots"]:
        return False

    store["current_df"] = store["snapshots"].pop()
    if store["transform_log"]:
        store["transform_log"].pop()
    return True


def reset_all() -> bool:
    """Reset the working dataframe back to the originally loaded dataset."""
    store = get_store()
    if store["original_df"] is None:
        return False

    store["current_df"] = store["original_df"].copy()
    store["snapshots"] = []
    store["transform_log"] = []
    return True


def build_report_payload() -> dict[str, Any]:
    """Assemble the base export report shared by the export page downloads."""
    current_df = get_current_data()
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_name": get_source_name(),
        "final_shape": list(current_df.shape) if current_df is not None else None,
        "transformations": get_transform_log(),
    }


def get_recipe_json() -> str:
    """Serialize the transformation log as the reproducible recipe output."""
    return json.dumps(get_transform_log(), indent=2)


def get_report_json() -> str:
    """Serialize the base report payload as JSON."""
    return json.dumps(build_report_payload(), indent=2)
