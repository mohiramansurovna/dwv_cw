from __future__ import annotations

import streamlit as st  # pyright: ignore[reportMissingImports]

from src.data.store import get_store, set_store


def undo_last_step() -> bool:
    store = get_store()

    if not store["snapshots"]:
        return False

    store["current_df"] = store["snapshots"].pop()

    if store["transform_log"]:
        store["transform_log"].pop()

    return True


def reset_all() -> bool:
    store = get_store()

    if store["original_df"] is None:
        return False

    store["current_df"] = store["original_df"].copy()
    store["snapshots"] = []
    store["transform_log"] = []

    return True


def clear_session() -> None:
    store = get_store()

    set_store(
        df=None,
        source_name=None,
        source_kind=None,
    )

    for key in ["validation_result", "validation_title", "saved_charts", "charts"]:
        st.session_state.pop(key, None)